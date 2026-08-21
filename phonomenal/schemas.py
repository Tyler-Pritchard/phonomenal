from pydantic import BaseModel
from typing import Literal


class ClassificationResult(BaseModel):
    category: Literal[
        "lyric_fragment",
        "theme",
        "observation",
        "story",
        "joke",
        "social_commentary",
        "discard",
    ]
    confidence: float
    reasoning: str