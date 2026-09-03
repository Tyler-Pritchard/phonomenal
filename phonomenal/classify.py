import os
from anthropic import Anthropic
from dotenv import load_dotenv
from phonomenal.schemas import ClassificationResult
from phonomenal.storage import get_connection

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SCHEMA_VERSION = 4

CLASSIFICATION_TOOL = {
    "name": "classify_comment",
    "description": "Classify a YouTube comment for use as songwriting material.",
    "input_schema": {
        "type": "object",
        "properties": {
            "categories": {
                "type": "array",
                "items": {
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
                "minItems": 1,
                "description": (
                    "One or two categories that best apply to this comment. Most comments fit exactly one category — "
                    "only choose two if the comment genuinely does both at once (for example, a comment that makes a wry "
                    "observation about something while also implicitly criticizing it). "
                    "When a comment both notices something AND carries an implicit critical undertone, prefer including "
                    "BOTH 'observation' and 'social_commentary' rather than choosing only one — err on the side of "
                    "including both labels in ambiguous cases like this. "
                    "lyric_fragment: reads like a line that could go directly into a song. "
                    "theme: a recurring idea or feeling, not tied to one specific claim. "
                    "observation: a standalone remark or noticing about something, without making an argument or taking a position. "
                    "story: describes a specific event, anecdote, or narrative. "
                    "joke: primarily intended as humor. "
                    "social_commentary: explicitly argues, criticizes, or takes a stance on a political/social issue. "
                    "discard: noise, not usable."
                ),
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
        "required": ["categories", "confidence", "reasoning"],    },
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
    for category in result.categories:
        conn.execute(
            """
            INSERT INTO classifications (comment_id, category, confidence, schema_version, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (comment_id, category, result.confidence, SCHEMA_VERSION, result.reasoning),
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
            print(f"#{comment_id}: {result.categories} (confidence {result.confidence})")
        except Exception as e:
            print(f"#{comment_id}: FAILED — {e}")