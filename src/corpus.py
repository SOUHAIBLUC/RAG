from pathlib import Path


def read_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def find_files(paths: str, extension: list[str]) -> list[Path]:
    path = Path(paths)

    if not path.is_dir():
        raise FileNotFoundError("Corpus folder not found")
    result = []
    for surfi in extension:
        if not surfi.startswith("."):
            surfi = "." + surfi
        result.extend(
            file for file in path.rglob(f"*{surfi}")
            if file.is_file()
            )

    return sorted(set(result))
