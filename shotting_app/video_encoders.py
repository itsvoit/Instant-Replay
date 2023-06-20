from io import BytesIO

import cv2
import numpy as np

from shotting_app import capture


class Mp4VideoEncoder(capture.VideoEncoder):
    def __init__(self, fps, screen_size=(1920, 1080),
                 file_saver: capture.FileSaver = capture.FileSaver("videos", "video", "mp4")):
        super().__init__(fps, screen_size, file_saver)

    # noinspection PyUnresolvedReferences
    def encode(self, frames: list[capture.Frame]):
        output_path = self.file_saver.get_free_path()

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # todo restrict based on the extension of the FileSaver
        out = cv2.VideoWriter(output_path, fourcc, self.fps, self.screen_size)

        for frame in frames:
            out.write(cv2.cvtColor(np.array(frame.get()), cv2.COLOR_RGB2BGR))
        out.release()


class SomeOtherVideoEncoder(capture.VideoEncoder):
    def __init__(self, fps, screen_size=(1920, 1080),
                 file_saver: capture.FileSaver = capture.FileSaver("videos", "video", "mp4")):
        super().__init__(fps, screen_size, file_saver)

    def encode(self, frames: list[capture.Frame]):
        ...
