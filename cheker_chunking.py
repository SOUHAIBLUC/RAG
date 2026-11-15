
from src.corpus import find_files
from src.models import Chunk
from src.chunking import read_files, PythonChunker, MarkdownChunker
from tqdm import tqdm


def check_file(original_text: str, max_chunk_size: int, chunks: list[Chunk])-> list[str]:
    problems = []

    # 1. Check empty text
    if not original_text and chunks:
        problems.append("Empty text should have no chunks")

    # 2. Check each chunk
    for i, chunk in enumerate(chunks):

        # Check text against offsets
        expected_text = original_text[chunk.first_character_index:chunk.last_character_index + 1]

        if chunk.text != expected_text:
            problems.append(f"Chunk {i + 1}: text does not match offsets")

        # Check maximum size
        if len(chunk.text) > max_chunk_size:
            problems.append(f"Chunk {i + 1}: exceeds maximum size")

        # Check coverage
        if i == 0:
            if chunk.first_character_index != 0:
                problems.append(f"Chunk {i + 1}: must start at index 0")
        else:
            previous_chunk = chunks[i - 1]

            if chunk.first_character_index != previous_chunk.last_character_index + 1:
                problems.append(
                    f"Chunk {i + 1}: gap or overlap with previous chunk"
                )

    # 3. Check last chunk
    if chunks and chunks[-1].last_character_index != len(original_text) - 1:
        problems.append("Last chunk does not end at the last character")

    return problems


def main() -> None:
    corpus_folder = "data/raw/vllm-0.10.1"
    max_chunk_size = 2000

    chunkers = {
        ".py": PythonChunker(max_chunk_size),
        ".md": MarkdownChunker(max_chunk_size),
        ".txt": MarkdownChunker(max_chunk_size),
    }

    files = find_files(corpus_folder, extension={".py", ".md", ".txt"})
    print(f"Found files: {len(files)}")

    skipped_count = 0
    skipped_paths = []
    total_characters = 0
    files_read = 0
    all_problems = []

    for path in tqdm(files):
        text = read_files(path)

        if text is None:
            skipped_count += 1
            skipped_paths.append(path)
            continue

        files_read += 1
        total_characters += len(text)

        chunker = chunkers.get(path.suffix)

        if chunker is None:
            continue

        chunks = chunker.chunk(text, str(path))

        problems = check_file(text, max_chunk_size, chunks)

        for problem in problems:
            all_problems.append(f"{path}: {problem}")

    print(f"Files read: {files_read}")
    print(f"Files skipped: {skipped_count}")
    print(f"Total characters: {total_characters}")

    print(f"Validation problems: {len(all_problems)}")

    for problem in all_problems:
        print(problem)


if __name__ == "__main__":
    main()