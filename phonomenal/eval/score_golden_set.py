import os
import re

DRAFT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden_set_draft.txt")


def parse_draft():
    with open(DRAFT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    blocks = content.split("---\n")[1:]  # skip header before first ---

    for block in blocks:
        id_match = re.search(r"ID:\s*(\d+)", block)
        claude_match = re.search(r"CLAUDE_SAID:\s*(\S+)", block)
        your_match = re.search(r"YOUR_LABEL:\s*(\S+)", block)

        if id_match and claude_match and your_match:
            entries.append({
                "id": int(id_match.group(1)),
                "claude_said": claude_match.group(1).strip(),
                "your_label": your_match.group(1).strip(),
            })

    return entries


def score(entries):
    total = len(entries)
    agreements = sum(1 for e in entries if e["claude_said"] == e["your_label"])
    disagreements = [e for e in entries if e["claude_said"] != e["your_label"]]

    print(f"Total labeled: {total}")
    print(f"Agreements: {agreements} ({agreements/total:.1%})")
    print(f"Disagreements: {len(disagreements)}\n")

    print("--- Disagreements ---")
    for e in disagreements:
        print(f"#{e['id']}: Claude said '{e['claude_said']}', you said '{e['your_label']}'")


if __name__ == "__main__":
    entries = parse_draft()
    score(entries)