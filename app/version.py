import re
from pathlib import Path


APP_VERSION = "1.0.1"

# The release image writes the built Git commit here (see Dockerfile). Local runs have no file.
BUILD_COMMIT_FILE = Path(__file__).resolve().parent.parent / "BUILD_COMMIT"


def read_build_commit(path=BUILD_COMMIT_FILE):
    """Return the full lowercase commit SHA recorded at build time, or None."""
    try:
        commit = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return commit if re.fullmatch(r"[0-9a-f]{40}", commit) else None


BUILD_COMMIT = read_build_commit()
