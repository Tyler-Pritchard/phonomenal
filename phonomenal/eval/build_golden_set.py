import json
import os
from phonomenal.storage import get_connection

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden_set_draft.txt")

CATEGORIES = [
    "lyric_fragment",
    "theme",
    "observation",
    "story",
    "joke",
    "social_commentary",
    "discard",
]


def export_draft():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT comments.id, comments.text, classifications.category
        FROM comments
        JOIN classifications ON comments.id = classifications.comment_id
        ORDER BY comments.id
        """
    ).fetchall()
    conn.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(f"# Categories: {', '.join(CATEGORIES)}\n")
        f.write("# Edit CLAUDE_SAID / YOUR_LABEL below each comment. Leave YOUR_LABEL blank to skip for now.\n\n")
        for comment_id, text, claude_category in rows:
            f.write(f"---\n")
            f.write(f"ID: {comment_id}\n")
            f.write(f"TEXT: {text}\n")
            f.write(f"CLAUDE_SAID: {claude_category}\n")
            f.write(f"YOUR_LABEL: \n\n")

    print(f"Wrote {len(rows)} comments to {OUTPUT_PATH}")


if __name__ == "__main__":
    export_draft()