"""
===========================================================
VisionDetect Pro
Web Dashboard Launcher
===========================================================

Starts the FastAPI web server on http://127.0.0.1:8000

Usage:
    python run_web.py [--host 0.0.0.0] [--port 8000]
===========================================================
"""

import argparse

import uvicorn


def main():

    parser = argparse.ArgumentParser(
        description="VisionDetect Pro Web Dashboard"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port (default: 8000)",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("VisionDetect Pro Web Dashboard")
    print("=" * 60)
    print(f"URL  : http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    uvicorn.run(
        "web.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
