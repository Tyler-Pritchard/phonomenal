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

def get_all_categories_by_comment(rows):
    categories_by_comment = {}
    for comment_id, text, category, confidence, notes in rows:
        categories_by_comment.setdefault(comment_id, []).append(category)
    return categories_by_comment

def print_by_category():
    rows = get_classified_comments()
    categories_by_comment = get_all_categories_by_comment(rows)

    current_category = None
    for comment_id, text, category, confidence, notes in rows:
        if category != current_category:
            current_category = category
            print(f"\n{'=' * 60}")
            print(f"CATEGORY: {category}")
            print('=' * 60)

        all_labels = categories_by_comment[comment_id]
        print(f"\n[#{comment_id}] (confidence: {confidence})", end="")
        if len(all_labels) > 1:
            others = [c for c in all_labels if c != category]
            print(f"  [also: {', '.join(others)}]", end="")
        print()
        print(text)


if __name__ == "__main__":
    print_by_category()