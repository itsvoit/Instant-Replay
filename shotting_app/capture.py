

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
		self.display = display
		self.resolution = resolution
		self.fps = fps
		self.length = length
		self.with_sound = with_sound
		self.video_encoder = video_encoder

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
		...

	def stop_recording(self):
		...

	def get_snapshot(self):
		...

	def get_screenshot(self):
		...

