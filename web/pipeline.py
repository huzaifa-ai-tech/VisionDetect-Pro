"""
===========================================================
VisionDetect Pro
Web Pipeline
===========================================================

Headless detection pipeline for the web dashboard.

Runs the full detection / tracking / analytics chain in a
background thread and exposes thread-safe snapshots:

- Latest annotated frame (JPEG bytes)
- Latest statistics (JSON-serializable dict)
- Control actions (start / stop / record / screenshot)

===========================================================
"""

import threading
import time

import cv2

from src.core.camera import Camera
from src.core.detector import Detector
from src.core.recorder import Recorder
from src.tracking.tracker import TrackingManager
from src.ui.visualization import Visualizer
from src.utils.analytics import Analytics
from src.monitor.system_monitor import SystemMonitor
from src.utils.config import MODEL_NAME, CONFIDENCE, IMAGE_SIZE, TRACKER


class WebPipeline:

    def __init__(
        self,
        model_path=None,
        confidence=None,
        image_size=None,
    ):

        self.model_path = model_path or MODEL_NAME
        self.confidence = confidence if confidence is not None else CONFIDENCE
        self.image_size = image_size or IMAGE_SIZE

        self.tracking = True

        self.detector = Detector(
            model_path=self.model_path,
            confidence=self.confidence,
            image_size=self.image_size,
            tracker=TRACKER,
        )

        self.detector.warmup()

        self.tracker = TrackingManager()
        self.analytics = Analytics()
        self.monitor = SystemMonitor()
        self.visualizer = Visualizer()
        self.recorder = Recorder()

        self.camera = None
        self.screenshotter = Screenshotter()

        # Shared state (updated by worker, read by web server)
        self._lock = threading.Lock()
        self._frame_jpeg = None
        self._stats = {}
        self._source = None
        self._running = False
        self._error = None

        self._thread = None
        self._stop_event = threading.Event()

    # -----------------------------------------------------
    # Public control
    # -----------------------------------------------------

    def start(self, source, tracking=True):
        """
        Start the pipeline for a given source.

        source : int | str | Path
            Webcam index, image path, video path or folder.
        """

        with self._lock:
            if self._running:
                return False, "Already running"

            self._stop_event.clear()

            try:
                self.camera = Camera(source)
                if not self.camera.is_opened():
                    return False, "Unable to open source"
            except Exception as exc:
                return False, str(exc)

            self.tracking = tracking
            self._source = source
            self._error = None
            self._frame_jpeg = None
            self.analytics.reset()
            self.tracker.reset()
            self._stats = {
                "status": "starting",
                "source": str(source),
                "source_type": self.camera.get_source_type(),
            }

            self._thread = threading.Thread(
                target=self._worker,
                name="WebPipeline",
                daemon=True,
            )

            self._thread.start()
            self._running = True

            return True, "Started"

    def stop(self):
        """
        Stop the pipeline and clean up resources.
        """

        with self._lock:
            self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=10)

        with self._lock:
            if self.camera is not None:
                self.camera.release()

            if self.recorder.recording:
                self.recorder.stop()

            self._running = False
            self.camera = None
            self._stats["status"] = "stopped"

    # -----------------------------------------------------

    def toggle_recording(self):
        with self._lock:
            if self._frame_jpeg is None:
                return False, "No frame available"

            frame = self._last_frame()
            previous = self.recorder.recording
            self.recorder.toggle(frame)

            if not previous and self.recorder.recording:
                self.visualizer.notify_recording_started()
            elif previous and not self.recorder.recording:
                self.visualizer.notify_recording_stopped()

            return True, "recording" if self.recorder.recording else "stopped"

    # -----------------------------------------------------

    def capture_screenshot(self):
        with self._lock:
            if self._frame_jpeg is None:
                return False, None

            frame = self._last_frame()
            path = self.screenshotter.save(frame)
            self.visualizer.notify_screenshot()

            return True, path

    # -----------------------------------------------------

    def is_running(self):
        with self._lock:
            return self._running

    # -----------------------------------------------------

    def get_state(self):
        with self._lock:
            state = dict(self._stats)
            state["running"] = self._running
            state["recording"] = self.recorder.recording
            state["error"] = self._error

            if self.recorder.get_output_file() is not None:
                state["recording_file"] = self.recorder.get_output_file()

            return state

    # -----------------------------------------------------

    def get_frame_jpeg(self):
        with self._lock:
            return self._frame_jpeg

    # -----------------------------------------------------

    def _last_frame(self):
        """
        Decode the most recent annotated frame.
        """

        if self._frame_jpeg is None:
            return None

        import numpy as np

        return cv2.imdecode(
            np.frombuffer(self._frame_jpeg, dtype=np.uint8),
            cv2.IMREAD_COLOR,
        )

    # -----------------------------------------------------
    # Worker
    # -----------------------------------------------------

    def _worker(self):

        try:

            # warm up the visualizer notification
            self.visualizer.notify_model_loaded()

            image_mode = self.camera.get_source_type() in (
                "image",
                "folder",
            )

            use_tracking = self.tracking and not image_mode

            while not self._stop_event.is_set():

                success, frame = self.camera.read()

                if not success or frame is None:
                    break

                annotated = self._process_frame(frame)

                # Encode once for streaming
                ok, buffer = cv2.imencode(
                    ".jpg",
                    annotated,
                    [cv2.IMWRITE_JPEG_QUALITY, 85],
                )

                with self._lock:
                    if ok:
                        self._frame_jpeg = buffer.tobytes()
                    self._stats = self._build_stats()

                # Images / folders advance quickly; keep the
                # stream viewable instead of flashing by.
                if image_mode:
                    time.sleep(0.05)

            with self._lock:
                self._running = False
                self._stats["status"] = "finished"

        except Exception as exc:
            with self._lock:
                self._error = str(exc)
                self._running = False
                self._stats["status"] = "error"
                self._stats["error"] = str(exc)

    # -----------------------------------------------------

    def _process_frame(self, frame):

        results, inference = self.detector.predict(
            frame,
            tracking=self.tracking and not (
                self.camera is not None
                and self.camera.get_source_type() in ("image", "folder")
            ),
        )

        if self.tracking:
            self.tracker.update(results)

        fps = self.analytics.calculate_fps()
        self.analytics.add_inference_time(inference)
        self.analytics.object_statistics(results)

        self.monitor.update()
        self.monitor.set_ai_statistics(
            fps=fps,
            inference_time=inference,
            total_frames=self.analytics.get_total_frames(),
            total_detections=self.analytics.get_total_detections(),
            average_fps=self.analytics.get_average_fps(),
            average_inference=self.analytics.average_inference(),
        )

        frame = self.visualizer.draw(frame, results)

        if self.tracking:
            frame = self.visualizer.draw_tracks(frame, self.tracker)

        frame = self.visualizer.draw_recording(
            frame,
            self.recorder.recording,
            self.recorder.start_time,
        )

        frame = self.visualizer.notifier.draw(frame)

        self.recorder.write(frame)

        return frame

    # -----------------------------------------------------

    def _build_stats(self):

        summary = self.analytics.summary()

        tracker_summary = self.tracker.get_summary()

        class_names = self.detector.get_class_names()

        source_type = (
            self.camera.get_source_type()
            if self.camera is not None
            else None
        )

        image_mode = source_type in ("image", "folder")

        unique_ids = tracker_summary["unique_ids"]

        if image_mode:
            unique_ids = sum(
                self.analytics.session_statistics().values()
            )

        return {
            "status": "running",
            "source": str(self._source),
            "source_type": source_type,
            "tracking": self.tracking,
            "model": str(self.detector.get_model_name()),
            "confidence": self.detector.get_confidence(),
            "current_time": self.analytics.current_time(),
            "fps": round(summary["fps"], 2),
            "avg_fps": summary["avg_fps"],
            "inference_ms": summary["avg_inference"],
            "frames": summary["frames"],
            "total_detections": summary["detections"],
            "active_tracks": tracker_summary["active_tracks"],
            "unique_ids": unique_ids,
            "persons": tracker_summary["persons"],
            "vehicles": tracker_summary["vehicles"],
            "session": summary["session"],
            "objects": self.analytics.current_statistics(),
            "unique_objects": self.analytics.session_statistics(),
            "system": {
                "cpu": self.monitor.get_cpu(),
                "memory": self.monitor.get_memory(),
                "gpu": self.monitor.get_gpu(),
                "uptime": self.monitor.uptime(),
            },
            "class_colors": self._class_color_map(class_names),
        }

    # -----------------------------------------------------

    @staticmethod
    def _class_color_map(class_names):

        palette = [
            (255, 212, 0),
            (0, 255, 255),
            (255, 0, 255),
            (0, 255, 0),
            (255, 128, 0),
            (0, 128, 255),
            (255, 0, 128),
            (128, 0, 255),
        ]

        return {
            str(class_names[i]): list(palette[i % len(palette)])
            for i in range(len(class_names))
        }


class Screenshotter:
    """
    Minimal screenshot capture (writes the current frame to disk).
    """

    def __init__(self):
        from src.utils.config import SCREENSHOT_DIR
        self.output_dir = SCREENSHOT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(self, frame):
        from datetime import datetime

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        path = self.output_dir / f"screenshot_{timestamp}.jpg"

        cv2.imwrite(str(path), frame)

        return str(path)
