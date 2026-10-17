"""Default FastAPI entrypoint for DiagramFlow backend."""

import sys
from pathlib import Path

# Ensure src/ is on sys.path so 'backend' package is importable directly
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from backend.main import app, create_app

__all__ = ["app", "create_app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
