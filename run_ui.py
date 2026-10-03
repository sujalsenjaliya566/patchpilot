#!/usr/bin/env python3
"""Convenience launcher: python run_ui.py [--port 5000] [--debug]"""

import argparse
import sys
from pathlib import Path

# Make sure patchpilot src is importable when run from the project root.
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "ui"))

from app import app  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PatchPilot Web UI")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    print(f"  PatchPilot UI  →  http://localhost:{args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=args.debug, threaded=True)
