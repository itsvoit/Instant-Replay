import multiprocessing
import queue
import time
from copy import copy
from io import BytesIO
from multiprocessing import Queue, Process, Array, Pipe, Manager, Value

import mss
from PIL import Image


class Config:
    def __init__(self, display, resolution, fps, length, with_sound: bool):
        self.display = display
        self.resolution = resolution
        self.fps = fps
        self.length = length
        self.with_sound = with_sound

    ...


class Frame:
    ...


class VideoEncoder:
    def __init__(self):
        ...

    def encode(self, frames: list[Frame], config: Config):  # instead of config just fps?
        ...

    ...


def img_to_buffer(sct_img, ext, quality):
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    buffer = BytesIO()
    img.save(buffer, ext, quality=quality)
    return buffer


class RecorderProcess(multiprocessing.Process):
    def __init__(self, img_queue, rec_recv, interval):
        multiprocessing.Process.__init__(self)
        self.task = rec_recv
        self.img_queue = img_queue
        self.interval = interval

        # print(id(self.img_queue))

    def run(self):
        with mss.mss() as sct:
            mon = sct.monitors[1]
            while "Recording":
                if self.task.poll() and self.task.recv() == "KILL":
                    self.img_queue.put(None)
                    break

                # print("Shot")
                sct_img = sct.grab(mon)
                self.img_queue.put(sct_img)
                # print(sct_img)


class ConvertProcess(multiprocessing.Process):
    def __init__(self, img_queue, buffered_frames, trim_send, length, fps, ext, quality):
        multiprocessing.Process.__init__(self)
        self.img_queue = img_queue
        self.buffered_frames = buffered_frames
        self.trim_send = trim_send
        self.length = length
        self.fps = fps
        self.ext = ext
        self.quality = quality
        self.cnt = 0

        # print(id(self.img_queue))

    def run(self):
        print("Convert process running...")
        while "There are screenshots":
            if self.cnt == self.length * 2 * self.fps:
                self.cnt = self.length
                self.trim_send.send("TRIM")

            sct_img = self.img_queue.get()
            # print("Got an image")
            if sct_img is None:
                self.trim_send.send("KILL")
                break

            buffer = img_to_buffer(sct_img, self.ext, self.quality)
            self.buffered_frames.append(buffer)
            self.cnt += 1


class TrimProcess(multiprocessing.Process):
    def __init__(self, buffered_frames, trim_recv, length, fps):
        multiprocessing.Process.__init__(self)
        self.buffered_frames = buffered_frames
        self.trim_recv = trim_recv
        self.length = length
        self.fps = fps

    def run(self):
        while "Working":
            if self.trim_recv.poll():
                task = self.trim_recv.recv()
                if task == "KILL":
                    break
                elif task == "TRIM":
                    del self.buffered_frames[:self.length*self.fps]


class Capture:
    def __init__(self, display, resolution, fps, length, with_sound: bool, video_encoder: VideoEncoder):
        # Recording options
        self.display = display
        self.quality = resolution  # quality of the saved frames (increase for more ram usage)
        self.ext = "JPEG"
        self.fps = fps
        self.interval = (1 / self.fps) * pow(10, 9)  # interval between frames
        self.length = length
        self.with_sound = with_sound
        self.video_encoder = video_encoder

        # Recorder
        self.sct = mss.mss()

        # Buffer for video
        self.manager = Manager()
        self.buffered_frames = self.manager.list()
        self.exported_frames = self.manager.list()

        # Multiprocessing
        self.img_queue = Queue()
        self.rec_recv, self.rec_send = Pipe(duplex=False)
        self.trim_recv, self.trim_send = Pipe(duplex=False)
        self.snap_recv, self.snap_send = Pipe(duplex=False)

        self.rec_process = RecorderProcess(self.img_queue, self.rec_recv, copy(self.interval))
        self.conv_process = ConvertProcess(self.img_queue, self.buffered_frames, self.trim_send,
                                           copy(self.length), copy(self.fps), copy(self.ext), copy(self.quality))
        self.trim_process = TrimProcess(self.buffered_frames, self.trim_recv, copy(self.length), copy(self.fps))

    @classmethod
    def from_config(cls, config: Config, video_encoder: VideoEncoder):
        return cls(
            config.display,
            config.resolution,
            config.fps,
            config.length,
            config.with_sound,
            video_encoder
        )

    def start_recording(self):
        self.rec_process.start()
        self.conv_process.start()
        self.trim_process.start()

    def stop_recording(self):
        """
        1. check if recording
        2. kill rec and conv processes
        3. clear queue and buffered frames
        4. setup for new recording
        """

        if not self.rec_process.is_alive():
            print("Process is unalived")
            return
        print("Killing process")
        self.rec_send.send("KILL")

        self.rec_process.join()
        self.conv_process.join()
        self.trim_process.join()

        self.img_queue = Queue()

        self.exported_frames = self.manager.list()
        self.buffered_frames = self.manager.list()

        self.rec_process = RecorderProcess(self.img_queue, self.rec_recv, copy(self.interval))
        self.conv_process = ConvertProcess(self.img_queue, self.buffered_frames, self.trim_send,
                                           copy(self.length), copy(self.fps), copy(self.ext), copy(self.quality))
        self.trim_process = TrimProcess(self.buffered_frames, self.trim_recv, copy(self.length), copy(self.fps))

    def get_snapshot(self):
        # print("Get snapshot")
        # print(self.buffered_frames)
        self.exported_frames = self.buffered_frames[:self.length*self.fps]
        return list(self.exported_frames)

    def get_screenshot(self):
        ...
