"""
===========================================================
VisionDetect Pro
YOLO Detection & Tracking Engine
===========================================================
"""

import time
import numpy as np
from ultralytics import YOLO

try:

    import torch

    def auto_device():
        try:
            if torch.cuda.is_available():
                return "cuda:0"
        except Exception:
            pass
        return "cpu"

except ImportError:

    def auto_device():
        return "cpu"


class Detector:
    """
    Handles all YOLO inference.

    Supports:
        - Object Detection
        - Object Tracking
        - Model Warmup
        - Dynamic Confidence
    """

    def __init__(
        self,
        model_path: str,
        confidence: float = 0.5,
        tracker: str = "botsort.yaml",
        device: str = None,
        image_size: int = 640,
    ):

        if device is None:
            device = auto_device()

        self.model_path = model_path
        self.confidence = confidence
        self.tracker = tracker
        self.device = device
        self.image_size = image_size

        print("=" * 60)
        print("Loading YOLO Model")
        print("=" * 60)
        print(f"Model       : {model_path}")
        print(f"Confidence  : {confidence}")
        print(f"Tracker     : {tracker}")
        print(f"Device      : {device}")
        print("=" * 60)

        self.model = YOLO(model_path)

    # -----------------------------------------------------

    def warmup(self):
        """
        Run one dummy inference to reduce first-frame latency.
        """

        dummy = np.zeros((640, 640, 3), dtype=np.uint8)

        self.model.predict(
            source=dummy,
            verbose=False,
        )

        print("Model Warmed Up")

    # -----------------------------------------------------

    def detect(self, frame):
        """
        Standard object detection.
        """

        start = time.perf_counter()

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            device=self.device,
            imgsz=self.image_size,
            verbose=False,
        )

        inference_time = (time.perf_counter() - start) * 1000

        return results, inference_time

    # -----------------------------------------------------

    def track(self, frame):
        """
        Multi-object tracking using BoT-SORT / ByteTrack.
        """

        start = time.perf_counter()

        results = self.model.track(
            source=frame,
            conf=self.confidence,
            persist=True,
            tracker=self.tracker,
            device=self.device,
            imgsz=self.image_size,
            verbose=False,
        )

        inference_time = (time.perf_counter() - start) * 1000

        return results, inference_time

    # -----------------------------------------------------

    def predict(self, frame, tracking=False):
        """
        Unified inference API.
        """

        if tracking:
            return self.track(frame)

        return self.detect(frame)

    # -----------------------------------------------------

    def set_confidence(self, confidence: float):

        self.confidence = confidence

    # -----------------------------------------------------

    def get_confidence(self):

        return self.confidence

    # -----------------------------------------------------

    def get_model_name(self):

        return self.model_path

    # -----------------------------------------------------

    def get_tracker_name(self):

        return self.tracker

    # -----------------------------------------------------

    def get_class_names(self):

        return self.model.names

    # -----------------------------------------------------

    def total_classes(self):

        return len(self.model.names)

    # -----------------------------------------------------

    def print_summary(self):

        print("\n")
        print("=" * 60)
        print("Detector Summary")
        print("=" * 60)

        print(f"Model        : {self.model_path}")
        print(f"Classes      : {self.total_classes()}")
        print(f"Confidence   : {self.confidence}")
        print(f"Tracker      : {self.tracker}")
        print(f"Device       : {self.device}")

        print("=" * 60)