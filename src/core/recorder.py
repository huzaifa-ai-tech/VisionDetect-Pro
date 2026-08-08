"""
===========================================================
VisionDetect Pro
Video Recorder
===========================================================

Features
--------
- MP4 Recording
- Automatic Timestamp Filename
- Auto Resolution Detection
- Start / Stop Recording
- Recording Duration
- Frame Counter
===========================================================
"""

import cv2
import time
from pathlib import Path
from datetime import datetime

from src.utils.config import (
    VIDEO_DIR,
    VIDEO_CODEC,
    VIDEO_FPS,
)


class Recorder:

    def __init__(self):

        self.writer = None

        self.recording = False

        self.output_path = None

        self.frame_count = 0

        self.start_time = None

    # -----------------------------------------------------

    def start(self, frame):

        if self.recording:
            return

        height, width = frame.shape[:2]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"recording_{timestamp}.mp4"

        self.output_path = Path(VIDEO_DIR) / filename

        fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)

        self.writer = cv2.VideoWriter(
            str(self.output_path),
            fourcc,
            VIDEO_FPS,
            (width, height),
        )

        self.recording = True

        self.frame_count = 0

        self.start_time = time.time()

        print("=" * 60)
        print("Recording Started")
        print(f"File : {self.output_path}")
        print("=" * 60)

    # -----------------------------------------------------

    def stop(self):

        if not self.recording:
            return

        self.writer.release()

        self.writer = None

        self.recording = False

        duration = self.duration()

        print("=" * 60)
        print("Recording Finished")
        print(f"Frames   : {self.frame_count}")
        print(f"Duration : {duration}")
        print(f"Saved To : {self.output_path}")
        print("=" * 60)

    # -----------------------------------------------------

    def toggle(self, frame):

        if self.recording:

            self.stop()

        else:

            self.start(frame)

    # -----------------------------------------------------

    def write(self, frame):

        if not self.recording:
            return

        if self.writer is None:
            return

        self.writer.write(frame)

        self.frame_count += 1

    # -----------------------------------------------------

    def duration(self):

        if self.start_time is None:
            return "00:00:00"

        elapsed = time.time() - self.start_time

        total = int(elapsed)

        hours = total // 3600

        minutes = (total % 3600) // 60

        seconds = total % 60

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # -----------------------------------------------------

    def is_recording(self):

        return self.recording

    # -----------------------------------------------------

    def get_output_file(self):

        return str(self.output_path) if self.output_path else None

    # -----------------------------------------------------

    def get_frame_count(self):

        return self.frame_count

    # -----------------------------------------------------

    def get_status(self):

        return {

            "recording": self.recording,

            "frames": self.frame_count,

            "duration": self.duration(),

            "file": self.get_output_file(),

        }

    # -----------------------------------------------------

    def print_status(self):

        status = self.get_status()

        print("\n========== Recorder ==========")

        print(f"Recording : {status['recording']}")

        print(f"Frames     : {status['frames']}")

        print(f"Duration   : {status['duration']}")

        print(f"File       : {status['file']}")

        print("==============================")