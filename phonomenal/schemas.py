from pydantic import BaseModel
from typing import Literal, List


class ClassificationResult(BaseModel):
    categories: List[Literal[
        "lyric_fragment",
        "theme",
        "observation",
        "story",
        "joke",
        "social_commentary",
        "discard",
    ]]
    confidence: float
    reasoning: str