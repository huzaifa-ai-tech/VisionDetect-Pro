"""
===========================================================
VisionDetect Pro
Web Server
===========================================================

FastAPI server providing:

- GET  /                Web dashboard UI
- GET  /video           MJPEG stream of annotated frames
- GET  /api/stats       Latest pipeline statistics (JSON)
- POST /api/start       Start detection for a source
- POST /api/stop        Stop detection
- POST /api/record      Toggle video recording
- POST /api/screenshot  Capture a screenshot
- GET  /api/sources     Discover available input sources

Run with:
    python -m uvicorn web.server:app --host 0.0.0.0 --port 8000
or:
    python run_web.py
===========================================================
"""

import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from web.pipeline import WebPipeline

from src.utils.config import (
    DEFAULT_CAMERA,
    MODEL_DIR,
    ROOT,
    SCREENSHOT_DIR,
    VIDEO_DIR,
)

# -----------------------------------------------------
# Application state
# -----------------------------------------------------

app = FastAPI(title="VisionDetect Pro Web", version="1.0.0")

pipeline = WebPipeline()

WEB_ROOT = Path(__file__).resolve().parent
STATIC_DIR = WEB_ROOT / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# -----------------------------------------------------
# Request models
# -----------------------------------------------------

class StartRequest(BaseModel):
    source: str | int = DEFAULT_CAMERA
    tracking: bool = True


# -----------------------------------------------------
# Pages
# -----------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(STATIC_DIR / "index.html")


# -----------------------------------------------------
# Video stream
# -----------------------------------------------------

@app.get("/video")
def video_stream():
    """
    MJPEG stream. Newest annotated frame is served as soon
    as it is available.
    """

    def generate():

        while True:

            jpeg = pipeline.get_frame_jpeg()

            if jpeg is None:
                time.sleep(0.1)
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(jpeg)).encode() + b"\r\n"
                b"\r\n"
                + jpeg
                + b"\r\n"
            )

            time.sleep(0.03)

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# -----------------------------------------------------
# Statistics
# -----------------------------------------------------

@app.get("/api/stats")
def api_stats():
    return JSONResponse(pipeline.get_state())


# -----------------------------------------------------
# Controls
# -----------------------------------------------------

@app.post("/api/start")
def api_start(request: StartRequest):
    success, message = pipeline.start(
        request.source,
        tracking=request.tracking,
    )
    return JSONResponse(
        {"success": success, "message": message},
        status_code=200 if success else 400,
    )


@app.post("/api/stop")
def api_stop():
    pipeline.stop()
    return JSONResponse({"success": True, "message": "Stopped"})


@app.post("/api/record")
def api_record():
    success, message = pipeline.toggle_recording()
    return JSONResponse(
        {"success": success, "message": message},
        status_code=200 if success else 400,
    )


@app.post("/api/screenshot")
def api_screenshot():
    success, path = pipeline.capture_screenshot()
    return JSONResponse(
        {"success": success, "path": path},
        status_code=200 if success else 400,
    )


# -----------------------------------------------------
# Source discovery
# -----------------------------------------------------

@app.get("/api/sources")
def api_sources():

    sources = {
        "camera": [],
        "video": [],
        "image": [],
    }

    # Webcams (0-3)
    import cv2
    for index in range(4):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            sources["camera"].append(index)
        cap.release()

    # Videos
    video_dir = ROOT / "test_data" / "videos"
    if video_dir.is_dir():
        sources["video"] = sorted(
            str(p) for p in video_dir.glob("*")
            if p.suffix.lower() in (".mp4", ".avi", ".mov", ".mkv")
        )

    # Images
    image_dir = ROOT / "test_data" / "images"
    if image_dir.is_dir():
        sources["image"] = sorted(
            str(p) for p in image_dir.glob("*")
            if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")
        )

    return JSONResponse(sources)


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


# -----------------------------------------------------
# Cleanup on shutdown
# -----------------------------------------------------

@app.on_event("shutdown")
def on_shutdown():
    pipeline.stop()
