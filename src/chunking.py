import ast
import re
import sys
from bisect import bisect_right
from pathlib import Path

from .models import Chunk


def read_files(path: str | Path) -> str | None:
    try:
        with open(path, encoding="utf-8", newline="") as file:
            return file.read()
    except (UnicodeDecodeError, OSError) as e:
        print(f"Warning: Could not read file {path}: {e}", file=sys.stderr)
        return None


def _validate_max_chunk_size(max_chunk_size: int) -> None:
    if (
        not isinstance(max_chunk_size, int)
        or isinstance(max_chunk_size, bool)
        or max_chunk_size <= 0
    ):
        raise ValueError("max_chunk_size must be a positive integer")


def _chunk_at_boundaries(
    text: str, file_path: str, max_chunk_size: int, boundaries: list[int]
) -> list[Chunk]:
    chunks = []
    start = 0

    while start < len(text):
        limit = min(start + max_chunk_size, len(text))
        boundary_index = bisect_right(boundaries, limit) - 1
        if len(text) - start <= max_chunk_size:
            end = len(text)
        elif boundary_index >= 0 and boundaries[boundary_index] > start:
            end = boundaries[boundary_index]
        else:
            newline = text.rfind("\n", start + 1, limit)
            end = newline + 1 if newline >= start else limit

        chunks.append(
            Chunk(
                file_path=file_path,
                first_character_index=start,
                last_character_index=end - 1,
                text=text[start:end],
            )
        )
        start = end

    return chunks


def _line_start_offsets(text: str) -> list[int]:
    offsets = []
    offset = 0
    for line in text.splitlines(keepends=True):
        offsets.append(offset)
        offset += len(line)
    return offsets


class FixedSizeChunker:
    def __init__(self, max_chunk_size: int) -> None:
        _validate_max_chunk_size(max_chunk_size)
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str, file_path: str) -> list[Chunk]:
        return [
            Chunk(
                file_path=file_path,
                first_character_index=start,
                last_character_index=min(start + self.max_chunk_size,
                                         len(text)) - 1,
                text=text[start: start + self.max_chunk_size],
            )
            for start in range(0, len(text), self.max_chunk_size)
        ]


class PythonChunker:
    def __init__(self, max_chunk_size: int) -> None:
        _validate_max_chunk_size(max_chunk_size)
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str, file_path: str) -> list[Chunk]:
        return _chunk_at_boundaries(
            text,
            file_path,
            self.max_chunk_size,
            self._find_boundaries(text),
        )

    def _find_boundaries(self, text: str) -> list[int]:
        line_offsets = _line_start_offsets(text)
        try:
            module = ast.parse(text)
        except SyntaxError:
            return line_offsets[1:]

        boundaries = []
        for node in module.body:
            node_line = node.lineno
            decorators = getattr(node, "decorator_list", [])
            if decorators:
                node_line = min(
                    node_line, *(decorator.lineno for decorator in decorators)
                )
            line_index = node_line - 1
            if 0 < line_index < len(line_offsets):
                boundaries.append(line_offsets[line_index])

        return boundaries


class MarkdownChunker:
    def __init__(self, max_chunk_size: int) -> None:
        _validate_max_chunk_size(max_chunk_size)
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str, file_path: str) -> list[Chunk]:
        return _chunk_at_boundaries(
            text,
            file_path,
            self.max_chunk_size,
            self._find_boundaries(text),
        )

    def _find_boundaries(self, text: str) -> list[int]:
        boundaries = []
        offset = 0
        previous_blank = True
        fence_character = None
        fence_length = 0

        for line in text.splitlines(keepends=True):
            if fence_character is not None:
                closing_fence = re.match(r"^ {0,3}(`+|~+)[ \t]*$", line)
                if (
                    closing_fence
                    and closing_fence.group(1)[0] == fence_character
                    and len(closing_fence.group(1)) >= fence_length
                ):
                    fence_character = None
                previous_blank = not line.strip()
                offset += len(line)
                continue

            opening_fence = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
            heading = re.match(r"^ {0,3}#{1,6}(?:[ \t]+|$)", line)
            if offset > 0 and (
                opening_fence or heading or (line.strip() and previous_blank)
            ):
                boundaries.append(offset)

            if opening_fence:
                fence_character = opening_fence.group(1)[0]
                fence_length = len(opening_fence.group(1))

            previous_blank = not line.strip()
            offset += len(line)

        return boundaries
