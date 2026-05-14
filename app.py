from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random
import re
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app)

# ================= LOAD INTENTS =================

try:
    with open("intents.json", "r", encoding="utf-8") as file:
        data = json.load(file)

except Exception as e:
    print("Error loading intents.json:", e)
    data = {"intents": []}


# ================= CLEAN TEXT =================

def clean_text(text):

    text = text.lower()

    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    return text.strip()


# ================= SIMILARITY FUNCTION =================

def similarity(a, b):

    return SequenceMatcher(None, a, b).ratio()


# ================= CHATBOT LOGIC =================

def chatbot_response(user_input):

    user_input = clean_text(user_input)

    best_match = None
    best_response = None
    highest_score = 0

    # =========================================
    # STEP 1 → SIMILARITY MATCHING
    # =========================================

    for intent in data.get("intents", []):

        patterns = intent.get("patterns", [])
        responses = intent.get("responses", [])

        for pattern in patterns:

            pattern_clean = clean_text(pattern)

            score = similarity(user_input, pattern_clean)

            print(f"USER: {user_input}")
            print(f"PATTERN: {pattern_clean}")
            print(f"SCORE: {score}")

            if score > highest_score:

                highest_score = score
                best_match = pattern_clean

                if responses:
                    best_response = random.choice(responses)

    # =========================================
    # STEP 2 → IF GOOD SIMILARITY FOUND
    # =========================================

    if highest_score >= 0.65:

        print("SIMILARITY MATCH FOUND")
        return best_response

    # =========================================
    # STEP 3 → FALLBACK TO PATTERN MATCHING
    # =========================================

    for intent in data.get("intents", []):

        patterns = intent.get("patterns", [])
        responses = intent.get("responses", [])

        for pattern in patterns:

            pattern_clean = clean_text(pattern)

            # substring matching
            if pattern_clean in user_input:

                print("PATTERN MATCH FOUND")
                return random.choice(responses)

            # word matching
            user_words = set(user_input.split())
            pattern_words = set(pattern_clean.split())

            if user_words & pattern_words:

                print("WORD MATCH FOUND")
                return random.choice(responses)

    # =========================================
    # FINAL DEFAULT RESPONSE
    # =========================================

    return "For more details, please contact ODM College office."


# ================= CHAT API =================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data_req = request.get_json()

        if not data_req or "message" not in data_req:

            return jsonify({
                "response": "Please send a message."
            })

        user_msg = data_req["message"]

        bot_reply = chatbot_response(user_msg)

        return jsonify({
            "response": bot_reply
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "response": "Server error occurred"
        })


# ================= HEALTH CHECK =================

@app.route("/health")
def health():

    return "OK"


# ================= RUN APP =================

if __name__ == "__main__":

    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )