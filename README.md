Flashcard Forge ⚡
Instant AI-powered flashcard generator
A lightweight web application for creating study materials from custom text or PDF documents.
Live web app → https://flashcard-forge-gfm2ad4o5wgugkwfmgpqv5.streamlit.app/
No install · No signup · Works on any device
Powered by Google Gemini 2.0 Flash (latest 2025 model)
Core Features
Input Flexibility: Generate flashcards from plain text input or uploaded PDF files.
Quantity & Difficulty: Generate between 4–20 perfect flashcards in seconds, customized by difficulty (Beginner, Intermediate, Advanced).
Export Ready: One-click download of all generated flashcards as clean Markdown (.md) files.
Secure: Your Gemini API key is managed securely via the backend and is never exposed to the client or browser.
CLI Support: The core logic also works locally via the command line (python main.py).
Try it now
https://flashcard-forge-gfm2ad4o5wgugkwfmgpqv5.streamlit.app/
Local Installation (Optional)
If you want to run the app locally, follow these steps:
Clone the repository:
git clone [https://github.com/Tomanaitis/flashcard-forge.git](https://github.com/Tomanaitis/flashcard-forge.git)
cd flashcard-forge


Install dependencies:
pip install -r requirements.txt


Set up your API Key:
Create a file named .env in the project root and add your Gemini API key:
cp .env.example .env
# Open .env and insert your key
GEMINI_API_KEY="YOUR_API_KEY_HERE"


Run the application:
streamlit run app.py

Alternatively, you can run the CLI version:
python main.py


Tech Stack
Google Gemini 2.0 Flash (2025)
Role: Core intelligence for text synthesis and QA generation.
Streamlit
Role: Web interface and deployment platform.
Pure Python
Role: Lightweight, fast, and scalable backend logic.
pypdf
Role: Used for reliable text extraction from PDF documents.
Made with ❤️ by @Tomanaitis
Star this repo if it helps you study – it really motivates me!
