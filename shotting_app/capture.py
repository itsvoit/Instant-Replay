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


rec_send, rec_recv = Pipe(duplex=False)
trim_send, trim_recv = Pipe(duplex=False)
snap_send, snap_recv = Pipe(duplex=False)


class RecorderProcess(multiprocessing.Process):
    def __init__(self, img_queue, interval):
        multiprocessing.Process.__init__(self)
        self.task = rec_recv
        self.img_queue = img_queue
        self.sct = mss.mss()
        self.interval = interval

    def run(self):
        with self.sct as sct:
            mon = sct.monitors[1]
            while "Recording":
                if self.task.poll() and self.task.recv() == "KILL":
                    self.img_queue.put(None)
                    break

                sct_img = sct.grab(mon)
                self.img_queue.put(sct_img)


class ConvertProcess(multiprocessing.Process):
    def __init__(self, img_queue, buffered_frames, length, ext, quality):
        multiprocessing.Process.__init__(self)
        self.img_queue = img_queue
        self.buffered_frames = buffered_frames
        self.trim_send = trim_send
        self.length = length
        self.ext = ext
        self.quality = quality
        self.cnt = 0

    def _convert(self):
        while "There are screenshots":
            if self.cnt == self.length * 2:
                self.cnt = self.length
                self.trim_send.send("TRIM")

            sct_img = self.img_queue.get()
            if sct_img is None:
                self.trim_send.send("KILL")
                break

            buffer = img_to_buffer(sct_img, self.ext, self.quality)
            self.buffered_frames.append(buffer)
            self.cnt += 1


class TrimProcess(multiprocessing.Process):
    def __init__(self, buffered_frames, length):
        multiprocessing.Process.__init__(self)
        self.buffered_frames = buffered_frames
        self.trim_recv = trim_recv
        self.length = length

    def _trim(self):
        while "Working":
            if self.trim_recv.poll():
                task = self.trim_recv.recv()
                if task == "KILL":
                    break
                elif task == "TRIM":
                    del self.buffered_frames[:self.length]


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

        self.rec_process = RecorderProcess(self.img_queue, copy(self.interval))
        self.conv_process = ConvertProcess(self.img_queue, self.buffered_frames,
                                           copy(self.length), copy(self.ext), copy(self.quality))
        self.trim_process = TrimProcess(self.buffered_frames, copy(self.length))

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
        RecorderProcess(self.img_queue, copy(self.interval))

        ConvertProcess(self.img_queue, self.buffered_frames, copy(self.length), copy(self.ext), copy(self.quality)).start()

        TrimProcess(self.buffered_frames, copy(self.length)).start()

        # self.rec_process.start()
        # self.conv_process.start()
        # self.trim_process.start()

    def stop_recording(self):
        """
        1. check if recording
        2. kill rec and conv processes
        3. clear queue and buffered frames
        4. setup for new recording
        """

        if not self.rec_process.is_alive():

            return
        rec_send.send("KILL")

        self.rec_process.join()
        self.conv_process.join()
        self.trim_process.join()

        self.img_queue = Queue()

        self.exported_frames = self.manager.list()
        self.buffered_frames = self.manager.list()

        self.rec_process = RecorderProcess(self.img_queue, copy(self.interval))
        self.conv_process = ConvertProcess(self.img_queue, self.buffered_frames,
                                           copy(self.length), copy(self.ext), copy(self.quality))
        self.trim_process = TrimProcess(self.buffered_frames, copy(self.length))

    def get_snapshot(self):
        self.exported_frames = self.buffered_frames[:self.length]
        return list(self.exported_frames)

    def get_screenshot(self):
        ...
