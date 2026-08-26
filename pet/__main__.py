"""Allow ``python -m pet`` to launch the app."""
import argparse

from .app import main


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
