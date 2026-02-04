import sys
from pathlib import Path


def pytest_configure(config):
    """Add project root to sys.path so tests can import the package."""
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
