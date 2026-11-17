import json
import time
from pathlib import Path

from tqdm import tqdm

from src.models import Chunk
from src.chunking import PythonChunker, MarkdownChunker, read_files
from src.corpus import find_files


class Indexer:
    def __init__(
        self,
        corpus_folder: str,
        max_chunk_size: int
    ) -> None:
        self.corpus_folder = corpus_folder
        self.max_chunk_size = max_chunk_size

        self.chunkers = {
            ".py": PythonChunker(max_chunk_size),
            ".md": MarkdownChunker(max_chunk_size),
            ".txt": MarkdownChunker(max_chunk_size),
        }

    def build(self) -> list[Chunk]:
        start_time = time.perf_counter()

        files = find_files(
            self.corpus_folder,
            extension={".py", ".md", ".txt"}
        )

        all_chunks = []

        for path in tqdm(files):
            text = read_files(path)

            if text is None:
                continue

            chunker = self.chunkers.get(path.suffix)

            if chunker is None:
                continue

            chunks = chunker.chunk(text, str(path))
            all_chunks.extend(chunks)

        elapsed_time = time.perf_counter() - start_time

        print(f"Total chunks: {len(all_chunks)}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

        return all_chunks


def save_chunks(
    chunks: list[Chunk],
    output_folder: str = "data/processed"
) -> None:
    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)

    output_file = folder / "chunks.json"

    data = [chunk.model_dump() for chunk in chunks]

    output_file.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def load_chunks(
    input_file: str = "data/processed/chunks.json"
) -> list[Chunk]:
    path = Path(input_file)

    data = json.loads(path.read_text(encoding="utf-8"))

    return [Chunk.model_validate(item) for item in data]
