import os
from dotenv import load_dotenv
import google.generativeai as genai
from prompts import FLASHCARD_PROMPT
from utils import save_to_markdown, parse_qa_text

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found! Add it in Streamlit Secrets or your local .env file.")

# Use the real working model in 2025
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")


def generate_flashcards(topic: str, num_cards: int = 10, difficulty: str = "intermediate"):
    prompt = FLASHCARD_PROMPT.format(
        topic=topic,
        num_cards=num_cards,
        difficulty=difficulty.capitalize()
    )

    print(f"Generating {num_cards} flashcards about: {topic}...")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Parse into cards for web + return them
    cards = parse_qa_text(raw_text, num_cards)

    # CLI: still show and save exactly like before
    if __name__ == "__main__":
        pretty_text = "\n".join([f"Q{i + 1}: {c['front']}\nA{i + 1}: {c['back']}\n" for i, c in enumerate(cards)])
        print("\nYour flashcards:\n")
        print(pretty_text)
        save_to_markdown(pretty_text, topic)

    return cards  # This is what app.py needs!


# Keep your old CLI working perfectly
if __name__ == "__main__":
    print("Flashcard Forge – AI Flashcard Generator (2025)\n")
    topic = input("Enter topic → ").strip() or "Python functions"
    difficulty = input("Difficulty (beginner/intermediate/advanced) → ").strip() or "intermediate"
    generate_flashcards(topic, num_cards=10, difficulty=difficulty)