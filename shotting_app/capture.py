import multiprocessing
import time
from io import BytesIO
from multiprocessing import Queue, Process

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
		self.buffered_frames = Queue(self.length*2)

		# Multiprocessing
		self.queue_img = Queue()
		self.shut_sig, self.shut_rec = multiprocessing.Pipe(duplex=False)
		self.trim_sig, self.trim_recv = multiprocessing.Pipe(duplex=False)
		self.rec = Process(target=self._record)
		self.conv = Process(target=self._convert)
		self.trim = Process(target=self._trim)

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
		self.rec.start()
		self.conv.start()

	def stop_recording(self):
		# check if recording
		# kill rec and conv processes
		# clear queue and buffered frames
		# setup for new recording
		...

	def get_snapshot(self):
		...

	def get_screenshot(self):
		...

	def _record(self):
		with self.sct as sct:
			mon = sct.monitors[1]
			prev_time = time.perf_counter_ns()
			while "Recording":
				while time.perf_counter_ns() < prev_time + self.interval:
					pass
				sct_img = sct.grab(mon)
				self.queue_img.put(sct_img)
				prev_time += self.interval

	def _convert(self):
		cnt = 0
		while "There are screenshots":
			if cnt == self.length:
				self.trim_sig.send(True)

			sct_img = self.queue_img.get()
			if sct_img is None:
				break

			buffer = self._img_to_buffer(sct_img)
			self.buffered_frames.put(buffer)
			cnt += 1

	def _trim(self):
		while "Recording":
			if self.trim_recv.recv():
				for _ in range(self.length):
					self.buffered_frames.get_nowait()

	def _img_to_buffer(self, sct_img):
		img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
		buffer = BytesIO()
		img.save(buffer, self.ext, quality=self.quality)
		return buffer

