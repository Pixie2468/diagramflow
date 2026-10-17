"""Default FastAPI entrypoint at project root."""

import sys
from pathlib import Path

# Ensure backend/src is on sys.path
backend_src = Path(__file__).resolve().parent / "backend" / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

from backend.main import app, create_app

__all__ = ["app", "create_app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
