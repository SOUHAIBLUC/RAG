import re



import re


def camel_handl(text: str) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z])([A-Z][a-z])", r"\1 \2", text)
    return text


def tokenize(text: str) -> list[str]:
    txt = camel_handl(text)
    txt = txt.lower()

    result = re.split(r"[^a-z0-9]+", txt)
    result = [token for token in result if token]

    if text.strip():
        result.append(text.lower())

    return result

class BM25:
    def __init__(
        self,
        chunks: list[Chunk],
        k1: float = 1.5,
        b: float = 0.75
    ) -> None:
        
		
    def search(
        self,
        query: str,
        k: int
    ) -> list[tuple[int, float]]: