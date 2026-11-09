from .models import Chunk


class FixedSizeChunker:
    def __init__(self, max_chunk_size: int) -> None:
        if (
            not isinstance(max_chunk_size, int)
            or isinstance(max_chunk_size, bool)
            or max_chunk_size <= 0
        ):
            raise ValueError("max_chunk_size must be a positive integer")

        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str, file_path: str) -> list[Chunk]:
        return [
            Chunk(
                file_path=file_path,
                first_character_index=start,
                last_character_index=min(start + self.max_chunk_size, len(text)) - 1,
                text=text[start : start + self.max_chunk_size],
            )
            for start in range(0, len(text), self.max_chunk_size)
        ]