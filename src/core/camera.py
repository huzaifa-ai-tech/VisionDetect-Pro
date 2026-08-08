"""
===========================================================
VisionDetect Pro
Camera / Input Manager
===========================================================

Supports

- Webcam
- Video
- Image
- Folder of Images

===========================================================
"""

import cv2
from pathlib import Path

from src.utils.config import (
    DEFAULT_CAMERA,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
)


class Camera:

    def __init__(self, source=DEFAULT_CAMERA):

        self.source = source

        self.mode = None

        self.cap = None

        self.images = []

        self.image_index = 0

        self.current_image = None

        self._initialize()

    # -----------------------------------------------------

    def _initialize(self):

        # Webcam
        if isinstance(self.source, int):

            self.mode = "webcam"

            self.cap = cv2.VideoCapture(self.source)

            self.cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                FRAME_WIDTH,
            )

            self.cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                FRAME_HEIGHT,
            )

            return

        source = Path(self.source)

        if not source.exists():

            raise FileNotFoundError(
                f"{source} not found."
            )

        # Image
        if source.is_file() and source.suffix.lower() in IMAGE_EXTENSIONS:

            self.mode = "image"

            self.current_image = cv2.imread(str(source))

            return

        # Video
        if source.is_file() and source.suffix.lower() in VIDEO_EXTENSIONS:

            self.mode = "video"

            self.cap = cv2.VideoCapture(str(source))

            return

        # Folder
        if source.is_dir():

            self.mode = "folder"

            self.images = sorted([
                file
                for file in source.iterdir()
                if file.suffix.lower() in IMAGE_EXTENSIONS
            ])

            return

        raise ValueError("Unsupported source.")

    # -----------------------------------------------------

    def read(self):

        if self.mode in ("webcam", "video"):

            return self.cap.read()

        # Single Image
        if self.mode == "image":

            if self.current_image is None:

                return False, None

            frame = self.current_image.copy()

            self.current_image = None

            return True, frame

        # Folder
        if self.mode == "folder":

            if self.image_index >= len(self.images):

                return False, None

            image_path = self.images[self.image_index]

            frame = cv2.imread(str(image_path))

            self.image_index += 1

            return True, frame

        return False, None

    # -----------------------------------------------------

    def release(self):

        if self.cap is not None:

            self.cap.release()

    # -----------------------------------------------------

    def reset(self):

        if self.mode == "video":

            self.cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                0,
            )

        elif self.mode == "folder":

            self.image_index = 0

        elif self.mode == "image":

            pass

    # -----------------------------------------------------

    def is_opened(self):

        if self.mode in ("video", "webcam"):

            return self.cap.isOpened()

        return True

    # -----------------------------------------------------

    def get_source_type(self):

        return self.mode

    # -----------------------------------------------------

    def frame_size(self):

        if self.mode in ("video", "webcam"):

            width = int(
                self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            )

            height = int(
                self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            )

            return width, height

        if self.current_image is not None:

            h, w = self.current_image.shape[:2]

            return w, h

        return None

    # -----------------------------------------------------

    def fps(self):

        if self.mode in ("video", "webcam"):

            fps = self.cap.get(
                cv2.CAP_PROP_FPS
            )

            if fps <= 0:

                fps = 30

            return fps

        return 30

    # -----------------------------------------------------

    def total_frames(self):

        if self.mode == "video":

            return int(
                self.cap.get(
                    cv2.CAP_PROP_FRAME_COUNT
                )
            )

        return None