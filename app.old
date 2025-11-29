import streamlit as st
from dotenv import load_dotenv
from main import generate_flashcards
import pypdf

# Load environment variables (like API keys)
load_dotenv()

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="Flashcard Forge", page_icon="⚡", layout="centered")
st.title("⚡ Lightning Flashcard Forge")
st.markdown("**Instant AI flashcards • Text • PDF • Powered by Gemini Flash**")

# ==================== TABS ====================
# Tab 1: Text / Topic, Tab 2: PDF Upload
tab1, tab2 = st.tabs(["Text / Topic", "PDF Upload"])


# ========================================================
#                    HELPER FUNCTIONS
# ========================================================

def extract_pdf(uploaded_file) -> str:
    """Extract text from uploaded PDF."""
    text_chunks = []
    try:
        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
            except Exception:
                pass
    except Exception as e:
        st.error(f"PDF extraction failed: {e}")
        return ""

    return "\n\n".join(text_chunks).strip()


def display_cards(cards, title: str):
    """Show cards + download button."""
    if not cards:
        st.warning("No flashcards generated.")
        return

    st.success(f"✨ Generated {len(cards)} flashcards!")

    for idx, card in enumerate(cards, start=1):
        # Only show the first part of the question on the expander title
        q_preview = card['front'][:80] + ('...' if len(card['front']) > 80 else '')
        with st.expander(f"Card {idx}: {q_preview}"):
            st.markdown(f"**Q:** {card['front']}")
            st.divider()
            st.markdown(f"**A:** {card['back']}")

    # Create Markdown content for download
    md = "\n\n---\n\n".join(
        f"**Q:** {c['front']}\n\n**A:** {c['back']}"
        for c in cards
    )

    st.download_button(
        "📥 Download as Markdown",
        md,
        file_name=f"{title}_flashcards.md",
        mime="text/markdown",
        use_container_width=True
    )


# ========================================================
#                        TAB 1 — TEXT
# ========================================================

with tab1:
    topic = st.text_area(
        "Topic/Text Input",
        height=150,
        placeholder="Explain quantum computing basics...",
        key="text_topic"
    )

    col1, col2 = st.columns(2)
    with col1:
        num_cards = st.slider("Number of Cards", 5, 30, 12, key="text_amount")
    with col2:
        level = st.selectbox("Difficulty Level",
                             ["beginner", "intermediate", "advanced"],
                             index=1,
                             key="text_level")

    if st.button("🔥 Generate from Text", type="primary", use_container_width=True, key="btn_text_generate"):
        if not topic.strip():
            st.error("Enter some text first!")
        else:
            with st.spinner("🤖 Generating flashcards..."):
                cards = generate_flashcards(topic, num_cards, level)
            display_cards(cards, "Text_Input")

# ========================================================
#                      TAB 2 — PDF
# ========================================================

with tab2:
    pdf = st.file_uploader("Choose PDF", type=["pdf"], key="pdf_upload")

    col1, col2 = st.columns(2)
    with col1:
        pdf_count = st.slider("Number of Cards", 5, 40, 20, key="pdf_amount")
    with col2:
        pdf_level = st.selectbox("Difficulty Level",
                                 ["beginner", "intermediate", "advanced"],
                                 index=1,
                                 key="pdf_level_select")

    if pdf and st.button("🔥 Generate from PDF", type="primary", use_container_width=True, key="btn_pdf_generate"):
        with st.spinner("📖 Extracting text..."):
            pdf_text = extract_pdf(pdf)

        if not pdf_text:
            st.error("No readable text in PDF.")
        else:
            st.success(f"Extracted {len(pdf_text.split()):,} words.")

            with st.spinner("🤖 Generating flashcards..."):
                title = pdf.name.replace(".pdf", "").replace(" ", "_")
                # Truncate text to fit model context window (20k is a safe guess)
                truncated = pdf_text[:20000]
                cards = generate_flashcards(truncated, pdf_count, pdf_level)

            display_cards(cards, title)

# Footer
st.markdown("---")
st.caption("⚡ Flashcard Forge • Powered by Gemini Flash • 2025 Edition")
