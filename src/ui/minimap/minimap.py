"""
===========================================================
VisionDetect Pro
MiniMap Component
===========================================================

Bird's-eye overview of tracked objects.

===========================================================
"""

import cv2


class MiniMap:

    def __init__(self):

        self.width = 220
        self.height = 140

        self.margin = 20

        self.background = (26, 30, 36)
        self.border = (62, 70, 80)

        self.grid = (46, 52, 60)

    # -----------------------------------------------------

    def draw(self, frame, tracker):

        h, w = frame.shape[:2]

        x = w - self.width - self.margin
        y = h - self.height - self.margin

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
            "MINIMAP",
            (x + 55, y - 6),
            cv2.FONT_HERSHEY_DUPLEX,
            0.55,
            (255, 255, 255),
            1,
        )

        # Grid
        for i in range(1, 4):

            gx = x + (self.width // 4) * i

            cv2.line(
                frame,
                (gx, y),
                (gx, y + self.height),
                self.grid,
                1,
            )

        for i in range(1, 3):

            gy = y + (self.height // 3) * i

            cv2.line(
                frame,
                (x, gy),
                (x + self.width, gy),
                self.grid,
                1,
            )

        # Draw tracked objects
        tracks = tracker.get_tracks()

        for _, data in tracks.items():

            cx, cy = data["center"]

            px = int((cx / w) * self.width)
            py = int((cy / h) * self.height)

            name = data["class_name"]

            if name == "person":
                color = (0, 255, 0)

            elif name in (
                "car",
                "truck",
                "bus",
                "motorcycle",
                "bicycle",
            ):
                color = (255, 200, 0)

            else:
                color = (255, 255, 255)

            cv2.circle(
                frame,
                (x + px, y + py),
                4,
                color,
                -1,
            )

        return frame