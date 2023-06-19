import multiprocessing
import os
import time
from abc import abstractmethod
from copy import copy
from io import BytesIO
from multiprocessing import Queue, Pipe, Manager

import cv2
import mss
import numpy as np
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


class VideoEncoder:
    def __init__(self, fps, screen_size):
        self.fps = fps
        self.screen_size = screen_size

    @abstractmethod
    def encode(self, frames: list[Frame], output_path):
        pass


class RecorderProcess(multiprocessing.Process):
    def __init__(self, img_queue, rec_recv, interval, display, verbose=True):
        multiprocessing.Process.__init__(self)
        self.task = rec_recv
        self.img_queue = img_queue
        self.interval = interval
        self.display = display
        self.verbose = verbose
        self.previous_shot = 0

    def run(self):
        if self.verbose:
            print("[Capture/Record] Recording process running...")
        with mss.mss() as sct:
            mon = sct.monitors[self.display]
            self.previous_shot = time.perf_counter_ns()
            while "Recording":
                if self.task.poll() and self.task.recv() == "KILL":
                    self.img_queue.put(None)
                    break
                while time.perf_counter_ns() < self.previous_shot + self.interval:
                    pass

                self.previous_shot = time.perf_counter_ns()
                sct_img = sct.grab(mon)
                self.img_queue.put(sct_img)

        if self.verbose:
            print("[Capture/Record] Recording process finishing...")


class ConvertProcess(multiprocessing.Process):
    def __init__(self, img_queue, buffered_frames, trim_send, length, fps, format_, quality, verbose=True):
        multiprocessing.Process.__init__(self)
        self.img_queue = img_queue
        self.frames = buffered_frames
        self.trim_signal = trim_send
        self.length = length
        self.fps = fps
        self.format_ = format_
        self.quality = quality
        self.cnt = 0
        self.verbose = verbose

    def run(self):
        if self.verbose:
            print("[Capture/Convert] Converting process running...")
        while "There are screenshots":
            if self.cnt == self.length * self.fps * 2:
                self.cnt = self.length * self.fps
                self.trim_signal.send("TRIM")

            sct_img = self.img_queue.get()
            # print("Got an image")
            if sct_img is None:
                self.trim_signal.send("KILL")
                break

            frame = Frame(sct_img, self.format_, self.quality)
            self.frames.append(frame)
            self.cnt += 1
        if self.verbose:
            print("[Capture/Convert] Converting process finishing...")


class TrimProcess(multiprocessing.Process):
    def __init__(self, buffered_frames, trim_recv, length, fps, verbose=True):
        multiprocessing.Process.__init__(self)
        self.buffered_frames = buffered_frames
        self.trim_recv = trim_recv
        self.length = length
        self.fps = fps
        self.verbose = verbose

    def run(self):
        if self.verbose:
            print("[Capture/Trim] Trimming process running...")
        while "Working":
            if self.trim_recv.poll():
                task = self.trim_recv.recv()
                if task == "KILL":
                    break
                elif task == "TRIM":
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
        self.format_ = "JPEG"
        self.fps = fps
        self.interval = (1 / self.fps) * pow(10, 9)  # interval between frames
        self.length = length
        self.with_sound = with_sound
        self.video_encoder = video_encoder
        self.verbose = verbose

        # Buffer for video
        self.manager = Manager()
        self.buffered_frames = self.manager.list()

        # Multiprocessing
        self.img_queue = Queue()
        self.rec_recv, self.rec_send = Pipe(duplex=False)
        self.trim_recv, self.trim_send = Pipe(duplex=False)
        self.snap_recv, self.snap_send = Pipe(duplex=False)

        self.rec_process = RecorderProcess(self.img_queue, self.rec_recv, copy(self.interval), copy(self.display))
        self.conv_process = ConvertProcess(self.img_queue, self.buffered_frames, self.trim_send,
                                           copy(self.length), copy(self.fps), copy(self.format_), copy(self.quality))
        self.trim_process = TrimProcess(self.buffered_frames, self.trim_recv, copy(self.length), copy(self.fps))

        if self.verbose:
            print("[Capture] Initialized Capture object")

    @classmethod
    def from_config(cls, config: Config, video_encoder: VideoEncoder):
        return cls(
            video_encoder,
            config.display,
            config.resolution,
            config.fps,
            config.length,
            config.with_sound
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
            if self.verbose:
                print("[Capture] Process is unalived")
            return
        if self.verbose:
            print("[Capture] Killing processes...")
        self.rec_send.send("KILL")

        self.rec_process.join()
        self.conv_process.join()
        self.trim_process.join()

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
        return self.video_encoder.encode(frames, os.path.join(self.output_dir, "output.mp4"))

    def get_screenshot(self):
        return self.buffered_frames[-1]
