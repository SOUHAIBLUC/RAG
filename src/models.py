from pydantic import BaseModel, Field, model_validator
from typing import List
import uuid

class MinimalSource(BaseModel):

    file_path: str
    first_character_index: int
    last_character_index: int

class Chunk(MinimalSource):

    text: str
    @model_validator(mode='after')
    def validator_index(self):
        if self.first_character_index < 0 or self.last_character_index < 0:
            raise ValueError("Character indices cannot be negative")
        if self.last_character_index < self.first_character_index:
            raise ValueError("Last character index cannot be before first character index")

        return self

class UnansweredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda:
                          str(uuid.uuid4()))
    question: str
class AnsweredQuestion(UnansweredQuestion):
    sources: List[MinimalSource]
    answer: str

class RagDataset(BaseModel):
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]

class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]

class MinimalAnswer(MinimalSearchResults):
    answer: str
    
class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int

class StudentSearchResultsAndAnswer(BaseModel):
    search_results: List[MinimalAnswer]
    k: int