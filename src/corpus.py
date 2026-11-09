from pathlib import Path
import typing
from pydantic import BaseModel


def read_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def find_files(paths: str, extension: list[str]) -> list[Path]:
    path = Path(paths)

    if not path.is_dir():
        return []

    result = []
    for surfi in extension:
        if not surfi.startswith("."):
            surfi = "." + surfi

        result.extend(
            file for file in path.rglob(f"*{surfi}")
            if file.is_file()
        )

    return sorted(set(result))
