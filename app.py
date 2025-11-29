import streamlit as st
import os
import json
import io
import requests  # <-- REQUIRED FOR LIVE API CALLS
from pypdf import PdfReader
from typing import List, Dict, Any

# --- API Configuration and Constants ---
# The GEMINI_API_KEY should be set in your Streamlit secrets or environment variables.
API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Using the specified model for text generation
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

# Languages available for selection
LANGUAGES = [
    "English", "Spanish", "French", "German", "Italian",
    "Portuguese", "Japanese", "Korean", "Chinese", "Lithuanian"
]


# --- PDF Processing Function ---

def get_text_from_pdf(uploaded_file: io.BytesIO) -> str:
    """Extracts text content from an uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        # Display error to the user in the UI
        st.error(f"Error processing PDF: {e}")
        return ""


# --- Helper Functions for Live API Call ---

def call_gemini_api_with_retry(payload: Dict[str, Any], max_retries: int = 5) -> str:
    """
    Calls the Gemini API using the requests library with exponential backoff.
    """
    if not API_KEY:
        st.error("API Key not found. Please set the GEMINI_API_KEY environment variable.")
        # Return an empty JSON structure on failure
        return '{"candidates": [{"content": {"parts": [{"text": "[]"}]}}]}'

    headers = {
        'Content-Type': 'application/json'
    }

    # URL includes the API Key via query parameter
    full_url = f"{API_URL}?key={API_KEY}"

    for attempt in range(max_retries):
        try:
            response = requests.post(full_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.text

        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors
            st.error(f"API HTTP Error (Attempt {attempt + 1}): {e.response.status_code} - {e.response.text}")
            if e.response.status_code in [429, 500, 503] and attempt < max_retries - 1:
                # Exponential backoff for rate limiting or server errors
                wait_time = 2 ** attempt
                # print(f"Retrying in {wait_time} seconds...")
                # time.sleep(wait_time) # removed time.sleep due to streamlit context
                continue
            else:
                raise e
        except requests.exceptions.RequestException as e:
            # Handle other request errors (e.g., network issues)
            st.error(f"API Request Error (Attempt {attempt + 1}): {e}")
            raise e

    return '{"candidates": [{"content": {"parts": [{"text": "[]"}]}}]}'  # Should not be reached


def generate_flashcards(text_input: str, num_cards: int, difficulty: str, q_lang: str, a_lang: str) -> List[
    Dict[str, str]]:
    """Generates flashcards using the Gemini API with multilingual instructions."""

    # 1. Construct the Multilingual System Instruction
    system_prompt = f"""
    You are an expert educational flashcard generator.
    Your task is to create exactly {num_cards} unique flashcards based on the provided text.

    The questions for the flashcards **MUST** be written in **{q_lang}**.
    The answers for the flashcards **MUST** be written in **{a_lang}**.
    The content difficulty must be {difficulty}.

    The output MUST be in a single, unadorned JSON array format.
    The array must contain objects, and each object must have only two keys: 'question' and 'answer'. 
    DO NOT include any explanation or markdown formatting (like ```json) outside of the array.
    """

    # 2. Construct the User Query (Context)
    user_query = f"Generate flashcards based on the following text: \n\n---\n\n{text_input}"

    # 3. Construct the API Payload for Structured Output
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "question": {"type": "STRING"},
                        "answer": {"type": "STRING"}
                    },
                    "propertyOrdering": ["question", "answer"]
                }
            }
        },
    }

    # 4. Call the API and Process the Response
    try:
        response_json_string = call_gemini_api_with_retry(payload)

        # Parse the API response structure
        api_response = json.loads(response_json_string)

        # Extract the raw JSON text payload from the model safely
        raw_json_text = api_response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text',
                                                                                                             '[]')

        # Clean and parse the final list of flashcards
        flashcards = json.loads(raw_json_text)
        return flashcards

    except Exception as e:
        # Display the specific error that caused the issue
        st.error(f"An error occurred during API call or parsing: {e}")
        return []


# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="Flashcard Forge ⚡")

st.title("Flashcard Forge ⚡")
st.markdown("Instant AI-powered flashcard generator with multilingual support.")

# --- Input Handling (PDF or Text Area) ---

# Input Method Selection
uploaded_file = st.file_uploader(
    "Upload a PDF file (Optional)",
    type=['pdf']
)

# Text storage variable
text_to_process = ""

# Default text for new users
default_text_example = ""

if uploaded_file is not None:
    # PDF is uploaded, extract text from it
    with st.spinner(f"Extracting text from PDF: {uploaded_file.name}..."):
        full_text = get_text_from_pdf(uploaded_file)

    if full_text:
        st.success(f"Text extracted from **{uploaded_file.name}**. Scroll down to configure cards.")
        st.text_area("Extracted Document Text (read-only):", full_text, height=250, disabled=True)
        text_to_process = full_text
    else:
        st.warning("Could not extract enough text from the PDF. Please try a different file.")
else:
    # No PDF, use manual text area input
    text_input = st.text_area(
        "Paste any study material, notes, or key concepts below to instantly generate custom flashcards.",
        default_text_example,
        height=250,
        placeholder="Paste text from your notes or textbook..."
    )
    text_to_process = text_input

# --- Configuration Panel ---
st.header("Flashcard Configuration")
with st.container():
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    # 1. Number of Cards
    num_cards = col1.slider("Number of Flashcards", 3, 20, 10)  # Defaulting to 10 cards

    # 2. Difficulty Level
    difficulty = col2.selectbox(
        "Difficulty Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    # 3. Question Language
    question_lang = col3.selectbox(
        "Question Language",
        LANGUAGES,
        index=LANGUAGES.index("Lithuanian") if "Lithuanian" in LANGUAGES else 0
    )

    # 4. Answer Language
    answer_lang = col4.selectbox(
        "Answer Language",
        LANGUAGES,
        index=LANGUAGES.index("English") if "English" in LANGUAGES else 0
    )

# Generation Button
if st.button("Generate Flashcards", use_container_width=True, type="primary"):
    if not text_to_process or not text_to_process.strip():
        st.warning("Please provide some text (via paste or PDF) to generate flashcards.")
    else:
        with st.spinner(f"Generating {num_cards} flashcards (Q: {question_lang} | A: {answer_lang})..."):
            flashcards = generate_flashcards(text_to_process, num_cards, difficulty, question_lang, answer_lang)

            if flashcards:
                st.success(f"Successfully generated {len(flashcards)} flashcards!")

                # Display Flashcards with answers hidden behind a second expander
                for i, card in enumerate(flashcards):
                    # Outer expander for the question
                    with st.expander(f"**Card {i + 1}:** {card.get('question', 'N/A')} **(Q: {question_lang})**",
                                     expanded=False):
                        #st.markdown(f"**Question:** {card.get('question', 'N/A')}")

                        # Nested expander to hide the answer
                        with st.expander("👉 Show Answer", expanded=False):
                            st.markdown(f"**Answer:** {card.get('answer', 'N/A')} **(A: {answer_lang})**")

                # Download Button (Markdown format)
                markdown_output = ""
                for i, card in enumerate(flashcards):
                    markdown_output += f"### Card {i + 1}\n"
                    markdown_output += f"**Q ({question_lang}):** {card.get('question', 'N/A')}\n"
                    markdown_output += f"**A ({answer_lang}):** {card.get('answer', 'N/A')}\n\n"

                st.download_button(
                    label="⬇️ Download Flashcards (Markdown)",
                    data=markdown_output,
                    file_name="flashcards_multilingual.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            else:
                st.error("Could not generate flashcards. Please check your API Key and ensure your text is clear.")

st.markdown("---")
st.caption("Powered by Google Gemini and Streamlit. Made with ❤️ by @Tomanaitis")
