#!/usr/bin/env python3
"""Double-click / command-line launcher for the Desktop Pet.

Running this file directly is the simplest way to start the pet from source:

    python run.py
    python run.py --fast-start
"""
import argparse
import os
import sys

# Make sure the project root is importable when double-clicked.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pet.app import main  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch Desktop Pet")
    parser.add_argument(
        "--fast-start",
        action="store_true",
        help="Skip startup weather fetch to speed up first-load responsiveness.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(main(fast_start=args.fast_start))
