"""
===========================================================
VisionDetect Pro
Professional Visualization Engine
===========================================================

Features
--------
✓ Premium Corner Bounding Boxes
✓ Modern Labels
✓ Object Tracking
✓ Motion Trails
✓ FPS Widget
✓ Recording Indicator
✓ Radar
✓ MiniMap
✓ Notifications

===========================================================
"""

import cv2
import time

from src.ui.colors import (
    WHITE,
    ACCENT,
    ERROR,
    OBJECT_COLORS,
    DEFAULT_COLOR,
)

from src.ui.radar.radar import MiniRadar
from src.ui.minimap.minimap import MiniMap
from src.ui.graphs.fps_graph import FPSGraph
from src.ui.notifications.notifier import NotificationManager

class Visualizer:

    def __init__(self):

        self.radar = MiniRadar()

        self.minimap = MiniMap()

        self.fps_graph = FPSGraph()

        self.notifier = NotificationManager()

        # Professional appearance

        self.corner_length = 18

        self.box_thickness = 2

        self.label_scale = 0.50

        self.label_thickness = 1

        self.track_thickness = 2

    # -----------------------------------------------------

    def draw(self, frame, results):

        if len(results) == 0:
            return frame

        result = results[0]

        if result.boxes is None:
            return frame

        for box in result.boxes:

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0],
            )

            confidence = float(box.conf.item())

            class_id = int(box.cls.item())

            class_name = result.names[class_id]

            if box.id is not None:

                track_id = int(box.id.item())

            else:

                track_id = -1

            color = OBJECT_COLORS.get(
                class_name.lower(),
                DEFAULT_COLOR,
            )

            self.draw_box(
                frame,
                x1,
                y1,
                x2,
                y2,
                color,
            )

            self.draw_label(
                frame,
                x1,
                y1,
                class_name,
                confidence,
                track_id,
                color,
            )

        return frame
    
    # -----------------------------------------------------

    def draw_box(
        self,
        frame,
        x1,
        y1,
        x2,
        y2,
        color,
    ):

        l = self.corner_length
        t = self.box_thickness

        # ==========================
        # Thin Rectangle
        # ==========================

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            1,
            cv2.LINE_AA,
        )

        # ==========================
        # Top Left
        # ==========================

        cv2.line(
            frame,
            (x1, y1),
            (x1 + l, y1),
            color,
            t,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (x1, y1),
            (x1, y1 + l),
            color,
            t,
            cv2.LINE_AA,
        )

        # ==========================
        # Top Right
        # ==========================

        cv2.line(
            frame,
            (x2, y1),
            (x2 - l, y1),
            color,
            t,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (x2, y1),
            (x2, y1 + l),
            color,
            t,
            cv2.LINE_AA,
        )

        # ==========================
        # Bottom Left
        # ==========================

        cv2.line(
            frame,
            (x1, y2),
            (x1 + l, y2),
            color,
            t,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (x1, y2),
            (x1, y2 - l),
            color,
            t,
            cv2.LINE_AA,
        )

        # ==========================
        # Bottom Right
        # ==========================

        cv2.line(
            frame,
            (x2, y2),
            (x2 - l, y2),
            color,
            t,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (x2, y2),
            (x2, y2 - l),
            color,
            t,
            cv2.LINE_AA,
        )

        # ==========================
        # Object Center
        # ==========================

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        cv2.circle(
            frame,
            (cx, cy),
            3,
            color,
            -1,
            cv2.LINE_AA,
        )

    # -----------------------------------------------------

    def draw_label(
        self,
        frame,
        x,
        y,
        class_name,
        confidence,
        track_id,
        color,
    ):

        # ==========================================
        # Label Text
        # ==========================================

        if track_id != -1:
            title = f"{class_name.upper()}  #{track_id}"
        else:
            title = class_name.upper()

        conf = f"{confidence * 100:.0f}%"

        # ==========================================
        # Text Sizes
        # ==========================================

        (w1, h1), _ = cv2.getTextSize(
            title,
            cv2.FONT_HERSHEY_DUPLEX,
            0.48,
            1,
        )

        (w2, h2), _ = cv2.getTextSize(
            conf,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            1,
        )

        width = max(w1, w2) + 20

        height = 42

        # Keep label inside frame

        y = max(height + 5, y)

        # ==========================================
        # Semi-transparent Background
        # ==========================================

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (x, y - height),
            (x + width, y),
            (28, 28, 28),
            -1,
        )

        cv2.addWeighted(
            overlay,
            0.78,
            frame,
            0.22,
            0,
            frame,
        )

        # ==========================================
        # Accent Border
        # ==========================================

        cv2.rectangle(
            frame,
            (x, y - height),
            (x + width, y),
            color,
            1,
            cv2.LINE_AA,
        )

        # Accent line

        cv2.line(
            frame,
            (x, y - height),
            (x + width, y - height),
            color,
            3,
            cv2.LINE_AA,
        )

        # ==========================================
        # Title
        # ==========================================

        cv2.putText(
            frame,
            title,
            (x + 8, y - 23),
            cv2.FONT_HERSHEY_DUPLEX,
            0.48,
            WHITE,
            1,
            cv2.LINE_AA,
        )

        # ==========================================
        # Confidence
        # ==========================================

        cv2.putText(
            frame,
            conf,
            (x + 8, y - 7),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )

    # -----------------------------------------------------

    def draw_tracks(
        self,
        frame,
        tracker,
    ):

        for track_id in tracker.get_track_ids():

            history = tracker.get_track_history(track_id)

            if len(history) < 2:
                continue

            color = ACCENT

            # Only draw recent history
            history = history[-18:]

            for i in range(1, len(history)):

                thickness = max(
                    1,
                    int(self.track_thickness * (i / len(history)))
                )

                cv2.line(
                    frame,
                    history[i - 1],
                    history[i],
                    color,
                    thickness,
                    cv2.LINE_AA,
                )

        return frame

    # -----------------------------------------------------

    def draw_recording(
        self,
        frame,
        recording,
        record_start_time=None,
    ):

        if not recording:
            return frame

        elapsed = 0

        if record_start_time is not None:

            elapsed = int(time.time() - record_start_time)

        minutes = elapsed // 60

        seconds = elapsed % 60

        text = f"REC {minutes:02}:{seconds:02}"

        h, w = frame.shape[:2]

        bx = 15
        by = h - 50
        bw = 175
        bh = 40

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (bx, by),
            (bx + bw, by + bh),
            (25, 25, 25),
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

        cv2.circle(
            frame,
            (bx + 18, by + 20),
            7,
            (0, 0, 255),
            -1,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            text,
            (bx + 34, by + 25),
            cv2.FONT_HERSHEY_DUPLEX,
            0.65,
            WHITE,
            1,
            cv2.LINE_AA,
        )

        return frame

    # -----------------------------------------------------

    def draw_widgets(
        self,
        frame,
        tracker,
        fps,
    ):

        # Update FPS history

        self.fps_graph.update(fps)

        # FPS Graph

        frame = self.fps_graph.draw(frame)

        # Radar

        frame = self.radar.draw(
            frame,
            tracker,
        )

        # MiniMap

        frame = self.minimap.draw(
            frame,
            tracker,
        )

        # Notifications

        frame = self.notifier.draw(frame)

        return frame

    # -----------------------------------------------------

    def notify(
        self,
        message,
        duration=2.5,
    ):
        """
        Show custom notification.
        """

        self.notifier.show(
            message,
            duration=duration,
        )

    # -----------------------------------------------------

    def notify_recording_started(
        self,
    ):
        """
        Recording started notification.
        """

        self.notifier.show(
            "Recording Started",
            duration=2.0,
        )

    # -----------------------------------------------------

    def notify_recording_stopped(
        self,
    ):
        """
        Recording stopped notification.
        """

        self.notifier.show(
            "Recording Stopped",
            duration=2.0,
        )

    # -----------------------------------------------------

    def notify_screenshot(
        self,
    ):
        """
        Screenshot saved notification.
        """

        self.notifier.show(
            "Screenshot Saved",
            duration=2.0,
        )

    # -----------------------------------------------------

    def notify_model_loaded(
        self,
    ):
        """
        Model loaded notification.
        """

        self.notifier.show(
            "YOLO Model Loaded",
            duration=2.5,
        )

    # -----------------------------------------------------

    def notify_tracking_enabled(
        self,
    ):
        """
        Tracking enabled notification.
        """

        self.notifier.show(
            "Object Tracking Enabled",
            duration=2.0,
        )

    # -----------------------------------------------------

    def notify_tracking_disabled(
        self,
    ):
        """
        Tracking disabled notification.
        """

        self.notifier.show(
            "Object Tracking Disabled",
            duration=2.0,
        )