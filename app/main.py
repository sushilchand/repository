import sys
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

from app.services.orchestrator import run_catalogue_sync


def run():
    result = run_catalogue_sync()
    print(result)


if __name__ == "__main__":
    run()

