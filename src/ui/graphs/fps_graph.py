"""
===========================================================
VisionDetect Pro
FPS Graph Component
===========================================================

Displays a live FPS history graph.

===========================================================
"""

import cv2
from collections import deque


class FPSGraph:

    def __init__(self):

        self.width = 220
        self.height = 90

        self.margin = 20

        self.offset_y = 20

        self.max_points = 60

        self.history = deque(maxlen=self.max_points)

        self.background = (26, 30, 36)
        self.border = (62, 70, 80)
        self.grid = (46, 52, 60)

        self.line_color = (255, 212, 0)

    # -----------------------------------------------------

    def update(self, fps):

        self.history.append(float(fps))

    # -----------------------------------------------------

    def draw(self, frame):

        h, w = frame.shape[:2]

        x = w - self.width - self.margin
        y = self.offset_y

        # Background

        cv2.rectangle(
            frame,
            (x, y),
            (x + self.width, y + self.height),
            self.background,
            -1,
        )

        # Border

        cv2.rectangle(
            frame,
            (x, y),
            (x + self.width, y + self.height),
            self.border,
            2,
        )

        # Title

        cv2.putText(
            frame,
            "FPS HISTORY",
            (x + 45, y - 6),
            cv2.FONT_HERSHEY_DUPLEX,
            0.55,
            (200, 208, 216),
            1,
        )

        # Grid

        for i in range(1, 4):

            gy = y + i * (self.height // 4)

            cv2.line(
                frame,
                (x, gy),
                (x + self.width, gy),
                self.grid,
                1,
            )

        if len(self.history) < 2:
            return frame

        max_fps = max(max(self.history), 1)

        step = self.width / (self.max_points - 1)

        points = []

        for i, value in enumerate(self.history):

            px = int(x + i * step)

            py = int(
                y + self.height
                - (value / max_fps) * self.height
            )

            points.append((px, py))

        for i in range(1, len(points)):

            cv2.line(
                frame,
                points[i - 1],
                points[i],
                self.line_color,
                2,
            )

        # Current FPS

        cv2.putText(
            frame,
            f"{self.history[-1]:.1f}",
            (x + 170, y + 18),
            cv2.FONT_HERSHEY_DUPLEX,
            0.55,
            (255, 212, 0),
            1,
        )

        return frame