import errno
import os
import re
from abc import abstractmethod
from pprint import pprint

import dxcam
from PIL import Image

from shotting_app import values


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


if __name__ == "__main__":
    cam = dxcam.create(output_idx=0, output_color=values.CAPTURE_MODE)
    i = cam.grab()

    encoder = PngEncoder(FileSaver("test", "photo_test", "png"))
    encoder.encode(i, (1920, 1080))
