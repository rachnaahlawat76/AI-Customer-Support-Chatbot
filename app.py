from flask import Flask, render_template, request, jsonify, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get("CHATBOT_SECRET_KEY", "change-this-secret-key-for-production")

KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
with open(KB_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE_BASE = json.load(f)

# Build a lightweight NLP index from the predefined questions and example phrases.
documents = []
document_to_entry = []
for entry in KNOWLEDGE_BASE:
    for phrase in [entry["question"]] + entry.get("examples", []):
        documents.append(phrase)
        document_to_entry.append(entry)

vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), strip_accents="unicode")
matrix = vectorizer.fit_transform(documents)

FOLLOW_UPS = {
    "it": "Could you tell me what 'it' refers to?",
    "that": "What would you like to know more about?",
    "more": "Sure — which part would you like me to explain in more detail?",
    "why": "Which point are you asking why about?",
    "how": "What would you like to know how to do?"
}

def clean_text(text):
    return re.sub(r"\s+", " ", (text or "").strip())

def find_answer(message):
    query = clean_text(message)
    if not query:
        return {"answer": "Please type a question so I can help.", "topic": None, "confidence": 0.0}

    # Context-aware handling for short follow-ups.
    previous_topic = session.get("last_topic")
    normalized = query.lower().strip(" ?!.")
    if previous_topic and normalized in {"more", "tell me more", "explain more", "details", "more details"}:
        previous = next((x for x in KNOWLEDGE_BASE if x["id"] == previous_topic), None)
        if previous:
            return {
                "answer": previous.get("details", previous["answer"]),
                "topic": previous["id"],
                "confidence": 1.0
            }

    if normalized in FOLLOW_UPS:
        return {"answer": FOLLOW_UPS[normalized], "topic": previous_topic, "confidence": 0.0}

    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, matrix).ravel()
    best_index = int(scores.argmax())
    score = float(scores[best_index])
    entry = document_to_entry[best_index]

    # Conservative threshold prevents confidently returning unrelated answers.
    if score < 0.16:
        if previous_topic:
            previous = next((x for x in KNOWLEDGE_BASE if x["id"] == previous_topic), None)
            if previous and any(word in normalized for word in ["it", "this", "that", "they", "them", "more"]):
                return {
                    "answer": f"We were discussing {previous['topic']}. {previous.get('details', previous['answer'])}",
                    "topic": previous["id"],
                    "confidence": score
                }
        return {
            "answer": "I’m not sure I understood that. Try asking about account help, pricing, returns, delivery, contact details, or getting started.",
            "topic": None,
            "confidence": score
        }

    session["last_topic"] = entry["id"]
    return {"answer": entry["answer"], "topic": entry["id"], "confidence": score}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = clean_text(payload.get("message", ""))
    result = find_answer(message)
    return jsonify(result)

@app.route("/api/reset", methods=["POST"])
def reset_context():
    session.pop("last_topic", None)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
