import os
from anthropic import Anthropic
from dotenv import load_dotenv
from phonomenal.schemas import ClassificationResult
from phonomenal.storage import get_connection

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

def save_classification(comment_id, result):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO classifications (comment_id, category, confidence, schema_version, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (comment_id, result.category, result.confidence, SCHEMA_VERSION, result.reasoning),
    )
    conn.commit()
    conn.close()

def get_unclassified_comments():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT comments.id, comments.text
        FROM comments
        LEFT JOIN classifications ON comments.id = classifications.comment_id
        WHERE classifications.id IS NULL
        """
    ).fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    unclassified = get_unclassified_comments()
    print(f"Found {len(unclassified)} comments to classify.")

    for comment_id, comment_text in unclassified:
        try:
            result = classify_comment(comment_text)
            save_classification(comment_id, result)
            print(f"#{comment_id}: {result.category} (confidence {result.confidence})")
        except Exception as e:
            print(f"#{comment_id}: FAILED — {e}")