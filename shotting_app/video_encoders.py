from io import BytesIO

import cv2
import numpy as np

from . import capture


class Mp4VideoEncoder(capture.VideoEncoder):
    def __init__(self, fps, screen_size=(1920, 1080)):
        super().__init__(fps, screen_size)

    # noinspection PyUnresolvedReferences
    def encode(self, frames: list[capture.Frame], output_path="output.mp4"):
        # output_buffer = BytesIO()

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, self.fps, self.screen_size)

        for frame in frames:
            out.write(cv2.cvtColor(np.array(frame.get()), cv2.COLOR_RGB2BGR))
        out.release()


class SomeOtherVideoEncoder(capture.VideoEncoder):
    def __init__(self, fps, screen_size=(1920, 1080)):
        super().__init__(fps, screen_size)

    def encode(self, frames: list[capture.Frame], output_path):
        ...
