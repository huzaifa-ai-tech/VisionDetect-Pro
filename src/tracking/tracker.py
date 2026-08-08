"""
===========================================================
VisionDetect Pro
Tracking Manager
===========================================================

Maintains:

- Active Tracks
- Unique IDs
- Class Statistics
- Track History
- Future Line Crossing Support
- Future Heatmap Support

===========================================================
"""

from collections import defaultdict


class TrackingManager:

    def __init__(self):

        # Active objects in current frame
        self.active_tracks = {}

        # All IDs ever seen
        self.unique_ids = set()

        # Count by class (unique track IDs per class)
        self.class_counts = defaultdict(int)

        # Track IDs already counted per class
        self.class_track_ids = defaultdict(set)

        # Track IDs ever seen as person / vehicle
        self.person_track_ids = set()
        self.vehicle_track_ids = set()

        # Store movement history
        self.track_history = defaultdict(list)

        # Maximum stored points per object
        self.max_history = 40

    # -----------------------------------------------------

    def update(self, results):
        """
        Update tracker using YOLO tracking results.
        """

        self.active_tracks.clear()

        if len(results) == 0:
            return

        result = results[0]

        if result.boxes is None:
            return

        for box in result.boxes:

            if box.id is None:
                continue

            track_id = int(box.id.item())

            class_id = int(box.cls.item())

            confidence = float(box.conf.item())

            class_name = result.names[class_id]

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            center = (center_x, center_y)

            # Store active track
            self.active_tracks[track_id] = {

                "id": track_id,

                "class_id": class_id,

                "class_name": class_name,

                "confidence": confidence,

                "bbox": (
                    x1,
                    y1,
                    x2,
                    y2,
                ),

                "center": center,

            }

            # Count class (once per unique track ID)
            if track_id not in self.class_track_ids[class_name]:
                self.class_track_ids[class_name].add(track_id)
                self.class_counts[class_name] += 1

            # Categorize track ID (once per category)
            if class_name == "person":
                self.person_track_ids.add(track_id)
            elif class_name in {
                "car",
                "truck",
                "bus",
                "motorcycle",
                "bicycle",
            }:
                self.vehicle_track_ids.add(track_id)

            # Save unique ID
            self.unique_ids.add(track_id)

            # Save trajectory
            self.track_history[track_id].append(center)

            if len(self.track_history[track_id]) > self.max_history:

                self.track_history[track_id].pop(0)

    # -----------------------------------------------------

    def reset(self):

        self.active_tracks.clear()

        self.unique_ids.clear()

        self.class_counts.clear()

        self.class_track_ids.clear()

        self.person_track_ids.clear()

        self.vehicle_track_ids.clear()

        self.track_history.clear()

    # -----------------------------------------------------

    def get_tracks(self):

        return self.active_tracks

    # -----------------------------------------------------

    def get_track(self, track_id):

        return self.active_tracks.get(track_id)

    # -----------------------------------------------------

    def get_track_history(self, track_id):

        return self.track_history.get(track_id, [])

    # -----------------------------------------------------

    def get_total_unique(self):

        return len(self.unique_ids)

    # -----------------------------------------------------

    def get_active_count(self):

        return len(self.active_tracks)

    # -----------------------------------------------------

    def get_class_counts(self):

        return dict(self.class_counts)

    # -----------------------------------------------------

    def get_person_count(self):

        return len(self.person_track_ids)

    # -----------------------------------------------------

    def get_vehicle_count(self):

        return len(self.vehicle_track_ids)

    # -----------------------------------------------------

    def get_track_ids(self):

        return list(self.active_tracks.keys())

    # -----------------------------------------------------

    def get_summary(self):

        return {

            "active_tracks": self.get_active_count(),

            "unique_ids": self.get_total_unique(),

            "persons": self.get_person_count(),

            "vehicles": self.get_vehicle_count(),

            "classes": self.get_class_counts(),

        }

    # -----------------------------------------------------

    def print_summary(self):

        summary = self.get_summary()

        print("\n========== Tracking Summary ==========")

        print(f"Active Tracks : {summary['active_tracks']}")

        print(f"Unique IDs    : {summary['unique_ids']}")

        print(f"Persons       : {summary['persons']}")

        print(f"Vehicles      : {summary['vehicles']}")

        print("Classes")

        for cls, count in summary["classes"].items():

            print(f"  {cls:<15} {count}")

        print("======================================")