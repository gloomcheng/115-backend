"""Make the exercise root importable, so `from main import app` and
`from harness.events import EventLog` work no matter where pytest is started
from.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
