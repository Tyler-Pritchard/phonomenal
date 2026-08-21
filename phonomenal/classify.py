import os
from anthropic import Anthropic
from dotenv import load_dotenv
from phonomenal.schemas import ClassificationResult

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SCHEMA_VERSION = 1

CLASSIFICATION_TOOL = {
    "name": "classify_comment",
    "description": "Classify a YouTube comment for use as songwriting material.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": [
                    "lyric_fragment",
                    "theme",
                    "observation",
                    "story",
                    "joke",
                    "social_commentary",
                    "discard",
                ],
            },
            "confidence": {
                "type": "number",
                "description": "How confident you are in this category, from 0 to 1.",
            },
            "reasoning": {
                "type": "string",
                "description": "A brief explanation of why this category was chosen.",
            },
        },
        "required": ["category", "confidence", "reasoning"],
    },
}


def classify_comment(comment_text):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        tools=[CLASSIFICATION_TOOL],
        tool_choice={"type": "tool", "name": "classify_comment"},
        messages=[
            {
                "role": "user",
                "content": f"Classify this YouTube comment:\n\n{comment_text}",
            }
        ],
    )

    tool_use_block = response.content[0]
    result = ClassificationResult(**tool_use_block.input)
    return result


if __name__ == "__main__":
    test_comment = "I write things that come to my mind, dude."
    result = classify_comment(test_comment)
    print(result)