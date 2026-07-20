"""Entry-point for the morning report workflow."""

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "morning_report.py"

spec = importlib.util.spec_from_file_location(
    "morning_report_root", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load module from {MODULE_PATH}")

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

main = module.main


if __name__ == "__main__":
    sys.exit(main())
