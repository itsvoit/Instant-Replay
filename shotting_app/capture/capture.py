import errno
import multiprocessing
import os
import re
import threading
import time
from abc import abstractmethod
from copy import copy
from io import BytesIO
from multiprocessing import Queue, Pipe, Manager
from pprint import pprint

import cv2
import dxcam
import mss
import numpy as np
from PIL import Image

import shotting_app.values as values


class Frame:
    def __init__(self,
                 sct_img,
                 format_,
                 quality):
        self.buffered_img = BytesIO()
        self.size = sct_img.size
        self.format_ = format_

        img = Image.fromarray(sct_img, mode=values.CAPTURE_MODE)

        img.save(self.buffered_img, format=format_, quality=quality)

    def to_file(self, path_):
        with open(path_, mode="wb") as file:
            file.write(self.buffered_img.getbuffer().tobytes())

    def get(self):
        return Image.open(self.buffered_img, formats=(self.format_,))


class FileSaver:
    def __init__(self,
                 directory,
                 file_prefix,
                 file_extension):
        self.directory = directory
        self.file_prefix = file_prefix
        self.file_extension = file_extension

    # Taken from https://stackoverflow.com/a/600612/119527
    def _mkdir_p(self):
        try:
            os.makedirs(self.directory)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(self.directory):
                pass
            else:
                raise

    def get_free_path(self):
        self._mkdir_p()
        files = [(file, match) for file in os.listdir(self.directory)
                 if (match :=
                     re.match(re.escape(self.file_prefix) + r"_(?P<value>.*)\." + re.escape(self.file_extension), file)
                     )]

        vals = set()
        for file, match in files:
            try:
                vals.add(int(match['value']))
            except ValueError:
                pass

        cnt = 0
        for val in sorted(vals):
            if val == cnt:
                cnt += 1
            else:
                break

        return os.path.join(self.directory, self.file_prefix + "_" + str(cnt) + "." + self.file_extension)


class VideoEncoder:
    def __init__(self,
                 fps,
                 file_saver: FileSaver):
        self.fps = fps
        self.file_saver = file_saver

    @abstractmethod
    def encode(self, frames: list[Frame], screen_size):
        pass


class Mp4VideoEncoder(VideoEncoder):
    def __init__(self,
                 fps,
                 file_saver: FileSaver = FileSaver("videos", "video", "mp4")):
        super().__init__(fps, file_saver)

    # noinspection PyUnresolvedReferences
    def encode(self, frames: list[Frame], screen_size):
        output_path = self.file_saver.get_free_path()

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, self.fps, screen_size)

        for frame in frames:
            out.write(cv2.cvtColor(np.asarray(frame.get()), cv2.COLOR_RGB2BGR))
        out.release()


class SomeOtherVideoEncoder(VideoEncoder):
    # todo new encoding
    def __init__(self,
                 fps,
                 file_saver: FileSaver = FileSaver("videos", "video", "mp4")):
        super().__init__(fps, file_saver)

    def encode(self, frames: list[Frame], screen_size):
        ...


VID_ENCODERS = {"mp4": Mp4VideoEncoder,
                "other": SomeOtherVideoEncoder
                }


class PhotoEncoder:
    def __init__(self,
                 file_saver: FileSaver):
        self.file_saver = file_saver

    @abstractmethod
    def encode(self, sct_img, screen_size, scale=None):
        pass


class PngEncoder(PhotoEncoder):
    def __init__(self,
                 file_saver: FileSaver = FileSaver("photos", "screenshot", "png")):
        PhotoEncoder.__init__(self, file_saver)

    def encode(self, sct_img, screen_size, scale=None):
        img = Image.fromarray(sct_img, mode=values.CAPTURE_MODE)
        img.save(self.file_saver.get_free_path(), format=values.CAPTURE_PNG, quality=95)


class JpegEncoder(PhotoEncoder):
    def __init__(self,
                 file_saver: FileSaver = FileSaver("photos", "screenshot", "jpeg")):
        PhotoEncoder.__init__(self, file_saver)
        ...

    def encode(self, sct_img, screen_size, scale=None):
        if scale != screen_size:
            sct_img = cv2.resize(sct_img, scale)
        img = Image.fromarray(sct_img, mode=values.CAPTURE_MODE)
        img.save(self.file_saver.get_free_path(), format=values.CAPTURE_JPEG, quality=95)


P_ENCODERS = {
    "png": PngEncoder,
    "jpeg": JpegEncoder,
}


class RecorderProcess(multiprocessing.Process):
    def __init__(self,
                 img_queue,
                 rec_conn,
                 shot_conn,
                 interval,
                 display,
                 verbose=False):
        super(RecorderProcess, self).__init__()
        # Communication
        self.img_queue = img_queue
        self.task = rec_conn
        self.shot_conn = shot_conn

        # Capture info
        self.interval = interval
        self.display = display

        # Logging
        self.verbose = verbose

    def run(self):
        if self.verbose:
            print("[Capture/Record] Recording process running...")
        # recorder = dxcam.create(output_color="BGR")
        # recorder.start(target_fps=60, video_mode=True)
        sct = dxcam.create(output_idx=self.display, output_color=values.CAPTURE_MODE)

        previous_shot = time.perf_counter_ns()
        previous_frame = None
        while "Recording":
            # Check for tasks
            if self.task.poll():
                task = self.task.recv()
                if task == values.TASK_KILL:  # Kill the thread - break the loop
                    break
                if task == values.TASK_SHOT:  # Export a screenshot
                    shot = sct.grab()
                    self.shot_conn.send(shot if shot is not None else previous_frame)

            # Wait to align the frames
            while time.perf_counter_ns() < previous_shot + self.interval:
                pass

            previous_shot = time.perf_counter_ns()
            sct_img = sct.grab()  # if idling (nothing new to render) then grab returns None
            sct_img = sct_img if sct_img is not None else previous_frame
            previous_frame = sct_img

            self.img_queue.put(sct_img)  # Send to the next thread

        if self.verbose:
            print("[Capture/Record] Recording process finishing...")


class ConvertThread(multiprocessing.Process):
    def __init__(self,
                 img_queue,
                 buffered_frames,
                 task,
                 trim_send,
                 length,
                 fps,
                 format_,
                 quality,
                 verbose=False):
        super(ConvertThread, self).__init__()
        # Communication
        self.img_queue = img_queue
        self.frames = buffered_frames
        self.task = task
        self.trim_signal = trim_send

        # Frame format / quality
        self.length = length
        self.fps = fps
        self.format_ = format_
        self.quality = quality

        # Logging
        self.verbose = verbose

    def run(self):
        cnt = 0
        if self.verbose:
            print("[Capture/Convert] Converting process running...")
        while "There are screenshots":
            if self.task.poll() and self.task.recv() == values.TASK_KILL:
                break
            if cnt == self.length * self.fps * 2:
                cnt = self.length * self.fps
                self.trim_signal.send(values.TASK_TRIM)

            sct_img = self.img_queue.get()
            if sct_img is None:
                break

            frame = Frame(sct_img, self.format_, self.quality)
            self.frames.append(frame)
            cnt += 1
        if self.verbose:
            print("[Capture/Convert] Converting process finishing...")


class TrimThread(multiprocessing.Process):
    def __init__(self,
                 buffered_frames,
                 task,
                 length,
                 fps,
                 verbose=False):
        super(TrimThread, self).__init__()
        # Communication
        self.buffered_frames = buffered_frames
        self.task = task

        # Trimming info
        self.length = length
        self.fps = fps

        # Logging
        self.verbose = verbose

    def run(self):
        if self.verbose:
            print("[Capture/Trim] Trimming process running...")
        while "Working":
            if self.task.poll():
                task = self.task.recv()
                if task == values.TASK_KILL:
                    break
                elif task == values.TASK_TRIM:
                    if self.verbose:
                        print(f"[Capture/Trim] Trimming buffered frames (len={len(self.buffered_frames)})")
                    del self.buffered_frames[:-self.length * self.fps]
                    if self.verbose:
                        print(f"[Capture/Trim] After trim (len={len(self.buffered_frames)})")

        if self.verbose:
            print("[Capture/Trim] Trimming process finishing...")


def get_displays_info():
    displays_info = dxcam.output_info().strip().split('\n')
    displays = []
    for display in displays_info:
        match = re.match(
            r"Device\[(?P<device>\d)] Output\[(?P<output>\d)]: " +
            r"Res:(?P<resolution>\(\d*, \d*\)) Rot:(?P<rotation>\d*) Primary:(?P<primary>.*)", display)
        res_match = re.match(r"\((?P<width>\d*), (?P<height>\d*)\)", match['resolution'])
        resolution = (int(res_match['width']), int(res_match['height'])) if res_match else values.DEFAULT_RESOLUTION
        displays.append({
            "device": int(match['device']),
            "output": int(match['output']),
            "resolution": resolution,
            "rotation": int(match['rotation']),
            "primary": match['primary'] == "True",
        } if match else None)

    return displays


class Capture:
    def __init__(self,
                 video_encoder: VideoEncoder,
                 photo_encoder: PhotoEncoder,
                 display=0,
                 resolution=(1920, 1080),
                 scale=(1920, 1080),
                 quality=80,
                 fps=15,
                 length=20,
                 with_sound: bool = False,
                 verbose: bool = False):
        # Recording options
        self.display = display
        self.displays = get_displays_info()
        self.resolution = resolution
        self.scale = scale if scale <= resolution else resolution
        self.quality = quality  # quality of the saved frames (increase for more ram usage)
        self.format_ = values.CAPTURE_JPEG
        self.fps = fps
        self.interval = (1 / self.fps) * pow(10, 9)  # interval between frames in nanoseconds
        self.length = length
        self.with_sound = with_sound
        self.video_encoder = video_encoder
        self.photo_encoder = photo_encoder

        # Logging
        self.verbose = verbose

        # Buffer for video
        self.manager = Manager()
        self.buffered_frames = self.manager.list()

        # Multiprocessing communication
        self.is_recording = False
        self.img_queue = Queue()
        self.rec_conn2, self.rec_conn1 = Pipe()
        self.shot_conn2, self.shot_conn1 = Pipe()
        self.conv_conn2, self.conv_conn1 = Pipe()
        self.trim_conn2, self.trim_conn1 = Pipe()

        # Processes
        self.rec_process = None
        self.conv_process = None
        self.trim_process = None
        self._make_processes()

        if self.verbose:
            print("[Capture] Initialized Capture object")

    @classmethod
    def from_config(cls, config, video_encoder: VideoEncoder, photo_encoder: PhotoEncoder, verbose=False):
        match = re.match(r"(?P<width>\d*)x(?P<height>\d*)", config['resolution'])
        try:
            resolution = (int(match['width']), int(match['height'])) if match else values.DEFAULT_RESOLUTION
        except ValueError:
            resolution = values.DEFAULT_RESOLUTION

        match = re.match(r"(?P<width>\d*)x(?P<height>\d*)", config['scale'])
        try:
            scale = (int(match['width']), int(match['height'])) if match else values.DEFAULT_RESOLUTION
        except ValueError:
            scale = values.DEFAULT_RESOLUTION

        return cls(
            video_encoder=video_encoder,
            photo_encoder=photo_encoder,
            display=config['display'],
            scale=scale,
            resolution=resolution,
            quality=config['quality'],
            fps=config['fps'],
            length=config['duration'],
            with_sound=config['save_sound'],
            verbose=verbose
        )

    def _make_processes(self):
        self.rec_process = RecorderProcess(self.img_queue, self.rec_conn2, self.shot_conn2, copy(self.interval),
                                           copy(self.display), verbose=self.verbose)
        self.conv_process = ConvertThread(self.img_queue, self.buffered_frames, self.conv_conn2, self.trim_conn1, copy(self.length),
                                          copy(self.fps), copy(self.format_), copy(self.quality), verbose=self.verbose)
        self.trim_process = TrimThread(self.buffered_frames, self.trim_conn2, copy(self.length), copy(self.fps),
                                       verbose=self.verbose)

    def start_recording(self):
        if self.verbose:
            self.rec_process.verbose = True
            self.conv_process.verbose = True
            self.trim_process.verbose = True

        self.is_recording = True

        # Run all the processes
        self.rec_process.start()
        self.conv_process.start()
        self.trim_process.start()
        return True

    def stop_recording(self):
        if not self.rec_process.is_alive():
            if self.verbose:
                print("[Capture] Processes haven't started")
            return False

        if self.verbose:
            print("[Capture] Killing processes...")
        self.rec_conn1.send(values.TASK_KILL)
        self.conv_conn1.send(values.TASK_KILL)
        self.trim_conn1.send(values.TASK_KILL)

        self.rec_process.join()
        self.conv_process.join()
        self.trim_process.join()

        if self.verbose:
            print("[Capture] Processes joined")

        self.is_recording = False

        # Set-up for next recording
        self.img_queue = Queue()

        self.buffered_frames = self.manager.list()

        self._make_processes()

        return True

    def export_recording(self):
        if not self.is_recording:
            return False
        display = self.displays[self.display]
        width, height = display['resolution']
        screen_size = (width, height) if display is not None else values.DEFAULT_SCREEN_SIZE

        frames = list(self.buffered_frames[-self.length * self.fps:])

        if self.verbose:
            print(f"[Capture] Exporting {len(frames)} frames")

        thread = threading.Thread(target=self.video_encoder.encode, args=(frames, screen_size,))
        thread.start()
        thread.join()
        return True

    def export_screenshot(self):
        self.rec_conn1.send(values.TASK_SHOT)
        while not self.shot_conn1.poll():
            pass

        self.photo_encoder.encode(self.shot_conn1.recv(), self.resolution, self.scale)

    def get_video_encoder(self):
        return self.video_encoder
