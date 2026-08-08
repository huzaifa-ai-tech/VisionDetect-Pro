"""
===========================================================
VisionDetect Pro
Analytics Engine
===========================================================

Provides

- FPS Calculation
- Average FPS
- Session Duration
- Unique Object Statistics
- Inference Statistics
- Detection Counter
- Current Time

===========================================================
"""

import time
from datetime import datetime
from collections import defaultdict


class Analytics:

    def __init__(self):

        self.start_time = time.time()

        self.last_frame_time = time.time()

        self.current_fps = 0.0

        self.average_fps = 0.0

        self.total_frames = 0

        self.total_detections = 0

        self.inference_times = []

        # Objects visible in CURRENT frame
        self.current_objects = {}

        # Unique tracked IDs during entire session
        #
        # Example:
        # {
        #   "car": {1,2,5},
        #   "person": {7,8},
        # }
        #
        self.unique_tracks = defaultdict(set)

    # --------------------------------------------------

    def reset(self):
        """
        Reset all session statistics for a new source.
        """

        self.start_time = time.time()

        self.last_frame_time = time.time()

        self.current_fps = 0.0

        self.average_fps = 0.0

        self.total_frames = 0

        self.total_detections = 0

        self.inference_times.clear()

        self.current_objects = {}

        self.unique_tracks.clear()

    # --------------------------------------------------

    def calculate_fps(self):

        current = time.time()

        elapsed = current - self.last_frame_time

        if elapsed > 0:

            instant_fps = 1.0 / elapsed

            self.current_fps = (
                self.current_fps * 0.90
                + instant_fps * 0.10
            )

        self.last_frame_time = current

        self.total_frames += 1

        total_time = current - self.start_time

        if total_time > 0:

            self.average_fps = (
                self.total_frames / total_time
            )

        return self.current_fps

    # --------------------------------------------------

    def add_inference_time(self, inference_ms):

        self.inference_times.append(
            inference_ms
        )

        if len(self.inference_times) > 300:

            self.inference_times.pop(0)

    # --------------------------------------------------

    def average_inference(self):

        if not self.inference_times:

            return 0

        return sum(self.inference_times) / len(
            self.inference_times
        )

    # --------------------------------------------------

    def max_inference(self):

        if not self.inference_times:

            return 0

        return max(self.inference_times)

    # --------------------------------------------------

    def min_inference(self):

        if not self.inference_times:

            return 0

        return min(self.inference_times)

    # --------------------------------------------------

    def session_duration(self):

        seconds = int(
            time.time() - self.start_time
        )

        hours = seconds // 3600

        minutes = (seconds % 3600) // 60

        secs = seconds % 60

        return f"{hours:02}:{minutes:02}:{secs:02}"

    # --------------------------------------------------

    def current_time(self):

        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # --------------------------------------------------

    def object_statistics(self, results):

        counter = defaultdict(int)

        if len(results) == 0:

            self.current_objects = {}

            return {}

        result = results[0]

        if result.boxes is None:

            self.current_objects = {}

            return {}

        for index, box in enumerate(result.boxes):

            class_id = int(box.cls.item())

            class_name = result.names[class_id]

            counter[class_name] += 1

            self.total_detections += 1

            # -----------------------------------------
            # Unique Object Counting
            # -----------------------------------------

            if box.id is not None:

                track_id = int(box.id.item())

                self.unique_tracks[class_name].add(
                    track_id
                )

            else:

                # fallback when tracking disabled

                fake_id = (
                    f"{self.total_frames}_"
                    f"{class_name}_"
                    f"{index}"
                )

                self.unique_tracks[class_name].add(
                    fake_id
                )

        self.current_objects = dict(counter)

        return self.current_objects
        # --------------------------------------------------

    def session_statistics(self):
        """
        Return unique tracked objects detected
        during the entire session.
        """

        return {
            class_name: len(track_ids)
            for class_name, track_ids
            in self.unique_tracks.items()
        }

    # --------------------------------------------------

    def current_statistics(self):
        """
        Return objects in current frame.
        """

        return self.current_objects

    # --------------------------------------------------

    def get_total_frames(self):

        return self.total_frames

    # --------------------------------------------------

    def get_total_detections(self):

        return self.total_detections

    # --------------------------------------------------

    def get_average_fps(self):

        return round(
            self.average_fps,
            2,
        )

    # --------------------------------------------------

    def summary(self):

        return {

            "frames": self.total_frames,

            "detections": self.total_detections,

            "fps": round(
                self.current_fps,
                2,
            ),

            "avg_fps": round(
                self.average_fps,
                2,
            ),

            "avg_inference": round(
                self.average_inference(),
                2,
            ),

            "max_inference": round(
                self.max_inference(),
                2,
            ),

            "min_inference": round(
                self.min_inference(),
                2,
            ),

            "session": self.session_duration(),

            "unique_objects": self.session_statistics(),

        }

    # --------------------------------------------------

    def print_summary(self):

        s = self.summary()

        print("\n========== Analytics ==========")

        print(f"Frames            : {s['frames']}")

        print(f"Detections        : {s['detections']}")

        print(f"Current FPS       : {s['fps']}")

        print(f"Average FPS       : {s['avg_fps']}")

        print(f"Average Infer(ms) : {s['avg_inference']}")

        print(f"Max Infer(ms)     : {s['max_inference']}")

        print(f"Min Infer(ms)     : {s['min_inference']}")

        print(f"Session Time      : {s['session']}")

        print("\nUnique Objects")

        print("---------------------------")

        unique = self.session_statistics()

        if len(unique) == 0:

            print("No objects detected.")

        else:

            for name, count in sorted(unique.items()):

                print(f"{name:<15}: {count}")

        print("===============================")