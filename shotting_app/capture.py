import errno
import multiprocessing
import os
import re
import time
from abc import abstractmethod
from copy import copy
from io import BytesIO
from multiprocessing import Queue, Pipe, Manager

import cv2
import mss
import numpy as np
from PIL import Image

from shotting_app import values


class Config:
    def __init__(self, display, resolution, fps, length, with_sound: bool):
        self.display = display
        self.resolution = resolution
        self.fps = fps
        self.length = length
        self.with_sound = with_sound

    ...


class Frame:
    def __init__(self, sct_img, format_, quality):
        self.buffered_img = BytesIO()
        self.size = sct_img.size
        self.format_ = format_

        img = Image.frombytes("RGB", self.size, sct_img.bgra, "raw", "BGRX")
        img.save(self.buffered_img, format=format_, quality=quality)

    def to_file(self, path_):
        with open(path_, mode="wb") as file:
            file.write(self.buffered_img.getbuffer().tobytes())

    def get(self):
        return Image.open(self.buffered_img, formats=(self.format_,))


class FileSaver:
    def __init__(self, directory, file_prefix, file_extension):
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
        # todo - figure out a way to save files
        self._mkdir_p()
        files = [(file, match) for file in os.listdir(self.directory)
                 if (match :=
                     re.match(re.escape(self.file_prefix) + r"(?P<value>.*)" + re.escape(self.file_extension), file)
                     )]

        for file, match in files:
            ...


class VideoEncoder:
    def __init__(self, fps, screen_size, file_saver: FileSaver):
        self.fps = fps
        self.screen_size = screen_size

    @abstractmethod
    def encode(self, frames: list[Frame]):
        pass


class RecorderProcess(multiprocessing.Process):
    def __init__(self, img_queue, rec_recv, interval, display, verbose=True):
        multiprocessing.Process.__init__(self)
        # Communication
        self.img_queue = img_queue
        self.task = rec_recv

        # Capture info
        self.interval = interval
        self.display = display

        # Logging
        self.verbose = verbose

    def run(self):
        if self.verbose:
            print("[Capture/Record] Recording process running...")
        with mss.mss() as sct:
            mon = sct.monitors[self.display]
            previous_shot = time.perf_counter_ns()
            while "Recording":
                if self.task.poll() and self.task.recv() == values.TASK_KILL:
                    self.img_queue.put(None)
                    break

                # Wait to align the frames
                while time.perf_counter_ns() < previous_shot + self.interval:
                    pass

                previous_shot = time.perf_counter_ns()
                sct_img = sct.grab(mon)
                self.img_queue.put(sct_img)

        if self.verbose:
            print("[Capture/Record] Recording process finishing...")


class ConvertProcess(multiprocessing.Process):
    def __init__(self, img_queue, buffered_frames, trim_send, length, fps, format_, quality, verbose=True):
        multiprocessing.Process.__init__(self)
        # Communication
        self.img_queue = img_queue
        self.frames = buffered_frames
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
            if cnt == self.length * self.fps * 2:
                cnt = self.length * self.fps
                self.trim_signal.send(values.TASK_TRIM)

            sct_img = self.img_queue.get()
            # print("Got an image")
            if sct_img is None:
                self.trim_signal.send(values.TASK_KILL)
                break

            frame = Frame(sct_img, self.format_, self.quality)
            self.frames.append(frame)
            cnt += 1
        if self.verbose:
            print("[Capture/Convert] Converting process finishing...")


class TrimProcess(multiprocessing.Process):
    def __init__(self, buffered_frames, trim_recv, length, fps, verbose=True):
        multiprocessing.Process.__init__(self)
        # Communication
        self.buffered_frames = buffered_frames
        self.trim_recv = trim_recv

        # Trimming info
        self.length = length
        self.fps = fps

        # Logging
        self.verbose = verbose

    def run(self):
        if self.verbose:
            print("[Capture/Trim] Trimming process running...")
        while "Working":
            if self.trim_recv.poll():
                task = self.trim_recv.recv()
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


class Capture:
    def __init__(self, video_encoder: VideoEncoder, output_dir="videos", display=1, quality=80, fps=20, length=10,
                 with_sound: bool = False, verbose: bool = False):
        # Recording options
        self.output_dir = output_dir
        self.display = display
        self.quality = quality  # quality of the saved frames (increase for more ram usage)
        self.format_ = values.CAPTURE_JPEG
        self.fps = fps
        self.interval = (1 / self.fps) * pow(10, 9)  # interval between frames in nanoseconds
        self.length = length
        self.with_sound = with_sound
        self.video_encoder = video_encoder

        # Logging
        self.verbose = verbose

        # Buffer for video
        self.manager = Manager()
        self.buffered_frames = self.manager.list()

        # Multiprocessing
        self.img_queue = Queue()
        self.rec_recv, self.rec_send = Pipe(duplex=False)
        self.trim_recv, self.trim_send = Pipe(duplex=False)
        self.snap_recv, self.snap_send = Pipe(duplex=False)

        # Processes
        self.rec_process = RecorderProcess(self.img_queue, self.rec_recv, copy(self.interval), copy(self.display))
        self.conv_process = ConvertProcess(self.img_queue, self.buffered_frames, self.trim_send,
                                           copy(self.length), copy(self.fps), copy(self.format_), copy(self.quality))
        self.trim_process = TrimProcess(self.buffered_frames, self.trim_recv, copy(self.length), copy(self.fps))

        if self.verbose:
            print("[Capture] Initialized Capture object")

    @classmethod
    def from_config(cls, config: Config, video_encoder: VideoEncoder):
        # todo - update config to have all necessary options
        return cls(
            video_encoder,
            config.display,
            config.resolution,
            config.fps,
            config.length,
            config.with_sound
        )

    def start_recording(self):
        # Run all the processes
        self.rec_process.start()
        self.conv_process.start()
        self.trim_process.start()

    def stop_recording(self):
        if not self.rec_process.is_alive():
            if self.verbose:
                print("[Capture] Process is unalived")
            return

        if self.verbose:
            print("[Capture] Killing processes...")
        self.rec_send.send(values.TASK_KILL)

        self.rec_process.join()
        self.conv_process.join()
        self.trim_process.join()

        # Set-up for next recording
        self.img_queue = Queue()

        self.buffered_frames = self.manager.list()

        self.rec_process = RecorderProcess(self.img_queue, self.rec_recv, copy(self.interval), copy(self.display))
        self.conv_process = ConvertProcess(self.img_queue, self.buffered_frames, self.trim_send,
                                           copy(self.length), copy(self.fps), copy(self.format_), copy(self.quality))
        self.trim_process = TrimProcess(self.buffered_frames, self.trim_recv, copy(self.length), copy(self.fps))

    def get_snapshot(self):
        frames = list(self.buffered_frames[-self.length * self.fps:])
        if self.verbose:
            print(f"[Capture] Exporting {len(frames)} frames")
        return self.video_encoder.encode(frames, os.path.join(self.output_dir))

    def get_screenshot(self):
        return self.buffered_frames[-1]
