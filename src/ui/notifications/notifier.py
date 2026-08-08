"""
===========================================================
VisionDetect Pro
Notification System
===========================================================

Displays temporary notification messages.

Examples
--------
✓ Screenshot Saved
✓ Recording Started
✓ Recording Stopped
✓ High CPU Usage
✓ Low FPS
✓ Model Loaded

===========================================================
"""

import cv2
import time


class NotificationManager:

    def __init__(self):

        self.message = ""

        self.duration = 2.5

        self.start_time = 0

        self.visible = False

        self.background = (38, 43, 50)

        self.border = (255, 212, 0)

        self.text_color = (240, 245, 250)

    # -----------------------------------------------------

    def show(
        self,
        message,
        duration=2.5,
    ):

        self.message = message

        self.duration = duration

        self.start_time = time.time()

        self.visible = True

    # -----------------------------------------------------

    def update(self):

        if not self.visible:
            return

        if time.time() - self.start_time >= self.duration:

            self.visible = False

    # -----------------------------------------------------

    def draw(
        self,
        frame,
    ):

        self.update()

        if not self.visible:
            return frame

        h, w = frame.shape[:2]

        (text_w, text_h), _ = cv2.getTextSize(
            self.message,
            cv2.FONT_HERSHEY_DUPLEX,
            0.65,
            2,
        )

        box_width = text_w + 40

        box_height = 50

        x = (w - box_width) // 2

        y = 20

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (x, y),
            (x + box_width, y + box_height),
            self.background,
            -1,
        )

        cv2.addWeighted(
            overlay,
            0.80,
            frame,
            0.20,
            0,
            frame,
        )

        cv2.rectangle(
            frame,
            (x, y),
            (x + box_width, y + box_height),
            self.border,
            2,
        )

        cv2.putText(
            frame,
            self.message,
            (x + 20, y + 32),
            cv2.FONT_HERSHEY_DUPLEX,
            0.65,
            self.text_color,
            2,
            cv2.LINE_AA,
        )

        return frame

    # -----------------------------------------------------

    def clear(self):

        self.visible = False

        self.message = ""

    # -----------------------------------------------------

    def is_visible(self):

        return self.visible