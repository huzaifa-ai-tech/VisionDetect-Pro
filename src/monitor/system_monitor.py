"""
===========================================================
VisionDetect Pro
System Performance Monitor
===========================================================

Features
--------
- CPU Usage
- RAM Usage
- GPU Availability
- Session Uptime
- Total Frames
- Total Detections
===========================================================
"""

import time

import psutil

try:
    import pynvml

    pynvml.nvmlInit()
    _NVML_AVAILABLE = True

except Exception:
    pynvml = None
    _NVML_AVAILABLE = False


class SystemMonitor:

    def __init__(self):

        self.start_time = time.time()

        self.cpu = 0.0

        self.memory = 0.0

        self.gpu = "N/A"

        self.gpu_util = 0.0

        self.gpu_memory = 0.0

        self.gpu_memory_used = 0.0

        self.fps = 0.0

        self.inference = 0.0

        self.total_frames = 0

        self.total_detections = 0

        self.average_fps = 0.0

        self.average_inference = 0.0

        self._init_gpu()

    # -----------------------------------------------------

    def _init_gpu(self):

        if not _NVML_AVAILABLE:
            return

        try:

            count = pynvml.nvmlDeviceGetCount()

            if count > 0:

                handle = pynvml.nvmlDeviceGetHandleByIndex(0)

                name = pynvml.nvmlDeviceGetName(handle)

                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

                self.gpu = name

                self.gpu_memory = memory.total / (1024 ** 3)

        except Exception:

            self.gpu = "N/A"

    # -----------------------------------------------------

    def _update_gpu(self):

        if not _NVML_AVAILABLE or self.gpu == "N/A":
            return

        try:

            handle = pynvml.nvmlDeviceGetHandleByIndex(0)

            self.gpu_util = pynvml.nvmlDeviceGetUtilizationRates(
                handle
            ).gpu

            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

            self.gpu_memory_used = memory.used / (1024 ** 3)

        except Exception:

            self.gpu_util = 0.0

            self.gpu_memory_used = 0.0

    # -----------------------------------------------------

    def update(self):

        self.cpu = psutil.cpu_percent(interval=None)

        self.memory = psutil.virtual_memory().percent

        self._update_gpu()

    # -----------------------------------------------------

    def get_cpu(self):

        return round(self.cpu, 1)

    # -----------------------------------------------------

    def get_memory(self):

        return round(self.memory, 1)

    # -----------------------------------------------------

    def get_gpu(self):

        return self.gpu

    # -----------------------------------------------------

    def get_gpu_util(self):

        return round(self.gpu_util, 1)

    # -----------------------------------------------------

    def get_gpu_memory(self):

        if self.gpu == "N/A":
            return 0.0

        return round(self.gpu_memory_used, 1)

    # -----------------------------------------------------

    def uptime(self):

        seconds = int(
            time.time() - self.start_time
        )

        hours = seconds // 3600

        minutes = (seconds % 3600) // 60

        secs = seconds % 60

        return f"{hours:02}:{minutes:02}:{secs:02}"

    # -----------------------------------------------------

    def set_ai_statistics(
        self,
        fps,
        inference_time,
        total_frames,
        total_detections,
        average_fps,
        average_inference,
    ):
        """
        Update AI performance statistics.
        """

        self.fps = round(fps, 2)

        self.inference = round(
            inference_time,
            2,
        )

        self.total_frames = total_frames

        self.total_detections = total_detections

        self.average_fps = round(
            average_fps,
            2,
        )

        self.average_inference = round(
            average_inference,
            2,
        )

    # -----------------------------------------------------

    def summary(self):
        """
        Return all system information.
        """

        return {

            "cpu": self.get_cpu(),

            "memory": self.get_memory(),

            "gpu": self.get_gpu(),

            "gpu_util": self.get_gpu_util(),

            "gpu_memory": self.get_gpu_memory(),

            "uptime": self.uptime(),

            "fps": getattr(self, "fps", 0),

            "inference": getattr(
                self,
                "inference",
                0,
            ),

            "frames": getattr(
                self,
                "total_frames",
                0,
            ),

            "detections": getattr(
                self,
                "total_detections",
                0,
            ),

            "average_fps": getattr(
                self,
                "average_fps",
                0,
            ),

            "average_inference": getattr(
                self,
                "average_inference",
                0,
            ),

        }

    # -----------------------------------------------------

    def print_summary(self):

        info = self.summary()

        print("\n========== System Monitor ==========")

        print(f"CPU Usage          : {info['cpu']} %")

        print(f"RAM Usage          : {info['memory']} %")

        print(f"GPU                : {info['gpu']}")

        print(f"GPU Utilization    : {info['gpu_util']} %")

        print(f"GPU Memory (GB)    : {info['gpu_memory']}")

        print(f"Current FPS        : {info['fps']}")

        print(f"Average FPS        : {info['average_fps']}")

        print(f"Inference          : {info['inference']} ms")

        print(f"Average Inference  : {info['average_inference']} ms")

        print(f"Frames             : {info['frames']}")

        print(f"Detections         : {info['detections']}")

        print(f"Uptime             : {info['uptime']}")

        print("====================================")