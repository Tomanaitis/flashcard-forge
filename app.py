import streamlit as st
import os
import json
import io
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
    "Portuguese", "Japanese", "Korean", "Chinese"
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
        st.error(f"Error processing PDF: {e}")
        return ""


# --- Helper Functions for API Call (Simulated for instructional purposes) ---

def call_gemini_api_with_retry(payload: Dict[str, Any], max_retries: int = 5) -> str:
    """
    Simulates calling the Gemini API with exponential backoff and
    returns a JSON string result.

    NOTE: In a real environment, you would replace the simulation below with
    your actual 'fetch' or API call logic, including exponential backoff
    for retries.
    """
    if not API_KEY:
        st.error("API Key not found. Please set the GEMINI_API_KEY environment variable.")
        return '{"candidates": [{"content": {"parts": [{"text": "[]"}]}}]}'

    # --- Start Simulation for Demonstration ---

    # Extracting parameters from the payload to create a dynamic fake response
    system_instruction = payload['systemInstruction']['parts'][0]['text']
    q_lang_match = system_instruction.split("MUST be written in **")[1].split("**")[0]
    a_lang_match = system_instruction.split("MUST be written in **")[2].split("**")[0]

    simulated_response = []

    if q_lang_match == "Spanish" and a_lang_match == "English":
        simulated_response = [
            {"question": "Cuál es el concepto clave de este texto?",
             "answer": "The main concept discussed is the use of multilingual models for cross-language tasks."},
            {"question": "Cómo se llama el modelo de lenguaje utilizado?",
             "answer": "The language model used for generation is Gemini 2.5 Flash."}
        ]
    elif q_lang_match == "French" and a_lang_match == "German":
        simulated_response = [
            {"question": "Quelle est la capitale de l'Allemagne?", "answer": "Die Hauptstadt Deutschlands ist Berlin."},
            {"question": "Comment dit-on 'bonjour' en allemand?", "answer": "Man sagt 'Guten Tag'."}
        ]
    else:  # Default English/Other combinations
        simulated_response = [
            {"question": f"({q_lang_match} Q): What is the Streamlit library used for?",
             "answer": f"({a_lang_match} A): It is used for turning Python scripts into interactive web applications."},
            {"question": f"({q_lang_match} Q): What is a Python virtual environment?",
             "answer": f"({a_lang_match} A): A self-contained directory that keeps specific Python versions and dependencies separate from others."}
        ]

    # Return the JSON string structure expected from the API
    return json.dumps({
        "candidates": [{
            "content": {
                "parts": [{
                    "text": json.dumps(simulated_response)
                }]
            }
        }]
    })

    # --- End Simulation ---


def generate_flashcards(text_input: str, num_cards: int, difficulty: str, q_lang: str, a_lang: str) -> List[
    Dict[str, str]]:
    """Generates flashcards using the Gemini API with multilingual instructions."""

    # 1. Construct the Multilingual System Instruction (CRITICAL CHANGE)
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

        # Extract the raw JSON text payload from the model
        raw_json_text = api_response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text',
                                                                                                             '[]')

        # Clean and parse the final list of flashcards
        flashcards = json.loads(raw_json_text)
        return flashcards

    except Exception as e:
        # In case of API failure or bad JSON response
        st.error(f"An error occurred during API call or parsing: {e}")
        return []


# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="Flashcard Forge ⚡")

st.title("Flashcard Forge ⚡")
st.markdown("Instant AI-powered flashcard generator with multilingual support.")

# Input Method Selection
uploaded_file = st.file_uploader(
    "Upload a PDF file (Optional)",
    type=['pdf']
)

if uploaded_file is not None:
    # PDF is uploaded, extract text from it
    with st.spinner("Extracting text from PDF..."):
        full_text = get_text_from_pdf(uploaded_file)
    st.info(f"Text extracted from **{uploaded_file.name}**. Scroll down to generate flashcards.")
    st.text_area("Extracted Document Text (read-only):", full_text, height=250, disabled=True)
    text_to_process = full_text
else:
    # No PDF, use manual text area input
    text_input = st.text_area(
        "Paste your study material here:",
        height=250,
        placeholder="Paste text from your notes or textbook... (min 50 chars)"
    )
    text_to_process = text_input

# Configuration Panel
st.header("Flashcard Configuration")
with st.container():
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    # 1. Number of Cards
    num_cards = col1.slider("Number of Flashcards", 3, 20, 5)

    # 2. Difficulty Level
    difficulty = col2.selectbox(
        "Difficulty Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    # 3. Question Language
    question_lang = col3.selectbox(
        "Question Language",
        LANGUAGES,
        index=LANGUAGES.index("Spanish") if "Spanish" in LANGUAGES else 0
    )

    # 4. Answer Language
    answer_lang = col4.selectbox(
        "Answer Language",
        LANGUAGES,
        index=LANGUAGES.index("English") if "English" in LANGUAGES else 0
    )

# Generation Button
if st.button("Generate Flashcards", use_container_width=True, type="primary"):
    if not text_to_process or len(text_to_process) < 50:
        st.warning("Please provide at least 50 characters of text (via paste or PDF) to generate flashcards.")
    else:
        with st.spinner(f"Generating {num_cards} flashcards (Q: {question_lang} | A: {answer_lang})..."):
            flashcards = generate_flashcards(text_to_process, num_cards, difficulty, question_lang, answer_lang)

            if flashcards:
                st.success(f"Successfully generated {len(flashcards)} flashcards!")

                # Display Flashcards
                for i, card in enumerate(flashcards):
                    with st.expander(f"**Card {i + 1}** (Q: {question_lang} | A: {answer_lang})", expanded=True):
                        st.markdown(f"**Question:** {card.get('question', 'N/A')}")
                        st.markdown("---")
                        st.markdown(f"**Answer:** {card.get('answer', 'N/A')}")

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
                st.error(
                    "Could not generate flashcards. Please check the console for API errors and ensure your text is comprehensive.")

st.markdown("---")
st.caption("Powered by Google Gemini and Streamlit. Made with ❤️ by @Tomanaitis")
