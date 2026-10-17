"""Run locally with `uv run --directory backend backend`."""

import uvicorn


def main() -> None:
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
