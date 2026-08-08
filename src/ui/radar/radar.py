"""
===========================================================
VisionDetect Pro
Mini Radar
===========================================================

Displays tracked object positions on a small radar.

===========================================================
"""

import cv2


class MiniRadar:

    def __init__(self):

        self.size = 170

        self.margin = 20

        self.offset_y = 125

        self.background = (26, 30, 36)

        self.border = (62, 70, 80)

        self.grid = (46, 52, 60)

        self.dot = (255, 212, 0)

    # -----------------------------------------------------

    def draw(self, frame, tracker):

        h, w = frame.shape[:2]

        x = w - self.size - self.margin
        y = self.offset_y

        # Background
        cv2.rectangle(
            frame,
            (x, y),
            (x + self.size, y + self.size),
            self.background,
            -1,
        )

        # Border
        cv2.rectangle(
            frame,
            (x, y),
            (x + self.size, y + self.size),
            self.border,
            2,
        )

        # Center lines
        cx = x + self.size // 2
        cy = y + self.size // 2

        cv2.line(frame, (cx, y), (cx, y + self.size), self.grid, 1)
        cv2.line(frame, (x, cy), (x + self.size, cy), self.grid, 1)

        # Concentric circles
        cv2.circle(frame, (cx, cy), 25, self.grid, 1)
        cv2.circle(frame, (cx, cy), 50, self.grid, 1)
        cv2.circle(frame, (cx, cy), 75, self.grid, 1)

        # Title
        cv2.putText(
            frame,
            "RADAR",
            (x + 45, y - 5),
            cv2.FONT_HERSHEY_DUPLEX,
            0.55,
            (255, 255, 255),
            1,
        )

        # Draw tracked objects
        tracks = tracker.get_tracks()

        for _, data in tracks.items():

            px, py = data["center"]

            rx = int((px / w) * self.size)
            ry = int((py / h) * self.size)

            cv2.circle(
                frame,
                (x + rx, y + ry),
                4,
                self.dot,
                -1,
            )

        return frame