import os
from datetime import datetime


def save_to_markdown(flashcards_text: str, topic: str):
    os.makedirs("examples", exist_ok=True)
    safe_topic = topic.lower().replace(" ", "_").replace(",", "").replace("/", "_")
    filename = f"examples/{safe_topic}_flashcards.md"
    header = f"# {topic} - Flashcards\nGenerated on {datetime.now():%Y-%m-%d %H:%M}\n\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + flashcards_text)

    print(f"Saved → {filename}")


# New helper for turning Q1/A1 text into a list (for the web app)
def parse_qa_text(text: str, max_cards: int = 20):
    """Convert Q1/A1 text into list of {'front': ..., 'back': ...}"""
    cards = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    i = 0
    while i < len(lines) - 1:
        q_line = lines[i]
        a_line = lines[i + 1]
        if q_line.startswith("Q") and a_line.startswith("A"):
            question = q_line.split(":", 1)[1].strip() if ":" in q_line else q_line[2:].strip()
            answer = a_line.split(":", 1)[1].strip() if ":" in a_line else a_line[2:].strip()
            cards.append({"front": question, "back": answer})
        i += 2
        if len(cards) >= max_cards:
            break
    return cards or [{"front": "Error parsing", "back": text[:500]}]