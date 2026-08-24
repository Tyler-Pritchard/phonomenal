# emoji/tone-symbol preservation in RTF ingestion" as Future Feature
import os
from striprtf.striprtf import rtf_to_text
from phonomenal.storage import get_connection

RAW_COMMENTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "raw", "comments.txt"
)

def load_raw_text():
    with open(RAW_COMMENTS_PATH, "r", encoding="utf-8") as f:
        return f.read()

def split_comments(raw_text):
    blocks = raw_text.split("\n\n")
    comments = [block.strip() for block in blocks if block.strip()]
    return comments

def insert_comments(comments):
    conn = get_connection()
    for comment in comments:
        clean_comment = comment.encode("utf-8", errors="ignore").decode("utf-8")
        conn.execute(
            "INSERT INTO comments (text) VALUES (?)",
            (clean_comment,)
        )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    text = load_raw_text()
    comments = split_comments(text)
    print(f"Found {len(comments)} comments")
    insert_comments(comments)
    print("Inserted into database")
