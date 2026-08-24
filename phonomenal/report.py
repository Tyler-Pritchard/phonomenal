from phonomenal.storage import get_connection


def get_classified_comments():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT comments.id, comments.text, classifications.category,
               classifications.confidence, classifications.notes
        FROM comments
        JOIN classifications ON comments.id = classifications.comment_id
        ORDER BY classifications.category, classifications.confidence DESC
        """
    ).fetchall()
    conn.close()
    return rows


def print_by_category():
    rows = get_classified_comments()

    current_category = None
    for comment_id, text, category, confidence, notes in rows:
        if category != current_category:
            current_category = category
            print(f"\n{'=' * 60}")
            print(f"CATEGORY: {category}")
            print('=' * 60)

        print(f"\n[#{comment_id}] (confidence: {confidence})")
        print(text)


if __name__ == "__main__":
    print_by_category()