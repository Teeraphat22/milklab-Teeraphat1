from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_scripts_module_exports_main():
    import scripts.morning_report as script

    assert callable(script.main)
