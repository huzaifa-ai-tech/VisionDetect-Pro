"""
===========================================================
VisionDetect Pro
Central Configuration
===========================================================
"""

from pathlib import Path

# =========================================================
# Project Information
# =========================================================

PROJECT_NAME = "VisionDetect Pro"
VERSION = "2.0.0"

# =========================================================
# Root Paths
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = ROOT / "src"
MODEL_DIR = ROOT / "models"
OUTPUT_DIR = ROOT / "output"

VIDEO_DIR = OUTPUT_DIR / "videos"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

# =========================================================
# Model
# =========================================================

MODEL_NAME = MODEL_DIR / "yolo11m.pt"

CONFIDENCE = 0.25
IMAGE_SIZE = 960

# =========================================================
# Camera
# =========================================================

DEFAULT_CAMERA = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# =========================================================
# Tracking
# =========================================================

TRACKER = "bytetrack.yaml"

# =========================================================
# Recorder
# =========================================================

VIDEO_CODEC = "mp4v"
VIDEO_FPS = 30

# =========================================================
# Supported File Extensions
# =========================================================

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
)

VIDEO_EXTENSIONS = (
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".flv",
    ".webm",
)

# =========================================================
# Create Output Directories
# =========================================================

for folder in (
    OUTPUT_DIR,
    VIDEO_DIR,
    SCREENSHOT_DIR,
):
    folder.mkdir(parents=True, exist_ok=True)
