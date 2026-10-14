# QueryMate — AI Query Chatbot

A small, beginner-friendly chatbot project built with **Python, Flask, TF-IDF NLP, and a predefined JSON knowledge base**.

## Features

- **NLP-based question matching:** TF-IDF vectorization and cosine similarity match user wording to known questions and examples.
- **Predefined knowledge base:** edit `knowledge_base.json` to add topics, example questions, and answers.
- **Context-aware follow-ups:** Flask session remembers the last matched topic, so a user can ask “tell me more” and receive details about that topic.
- **Responsive chat UI:** HTML, CSS, and JavaScript frontend with quick-question suggestions.
- **Safe fallback:** the chatbot admits when it cannot match a question instead of inventing an answer.

> Note: this is a lightweight NLP retrieval chatbot, not a large language model. It does not learn automatically and cannot access real orders, accounts, or live services.

## Run locally (Windows / VS Code)

1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Open Terminal and create a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## Add your own FAQ

Edit `knowledge_base.json`. Each entry uses this structure:

```json
{
  "id": "hours",
  "topic": "Opening hours",
  "question": "what are your opening hours",
  "examples": ["when are you open", "business hours"],
  "answer": "We are open Monday to Friday, 9 AM to 5 PM.",
  "details": "Our standard opening hours are Monday to Friday, 9 AM to 5 PM."
}
```

Keep `id` unique. Restart the app after changing the knowledge base.

## How it works

1. The app combines each FAQ question and its example phrases into a text corpus.
2. `TfidfVectorizer` converts the phrases into numerical vectors.
3. Cosine similarity finds the closest match for each incoming question.
4. If the best match is below a confidence threshold, the app returns a fallback response.
5. The last matched topic is stored in the Flask session to handle certain short follow-up questions.

## Before production use

- Replace `app.secret_key` with a strong secret stored in an environment variable.
- Turn off Flask debug mode.
- Add authentication, rate limiting, logging controls, tests, and privacy disclosures as needed.
- Do not use the demo answers as real company policies without updating the knowledge base.
