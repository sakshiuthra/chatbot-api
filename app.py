from flask import Flask, request, jsonify, render_template_string
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Load intents safely
try:
    with open("intents.json") as file:
        data = json.load(file)
except Exception as e:
    print("Error loading intents.json:", e)
    exit(1)

patterns = []
tags = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        patterns.append(pattern)
        tags.append(intent["tag"])

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(patterns)

model = LogisticRegression()
model.fit(X, tags)

def chatbot_response(user_input):
    user_vector = vectorizer.transform([user_input])
    prediction = model.predict(user_vector)[0]
    probability = max(model.predict_proba(user_vector)[0])

    if probability < 0.15:
        return "For more details, please contact ODM College office."

    for intent in data["intents"]:
        if intent["tag"] == prediction:
            return random.choice(intent["responses"])


# ✅ Home page (UI for browser testing)
@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot Test</title>
    </head>
    <body>
        <h2>Chatbot Test UI</h2>
        <input type="text" id="msg" placeholder="Type message">
        <button onclick="sendMsg()">Send</button>
        <p id="response"></p>

        <script>
        function sendMsg() {
            let message = document.getElementById("msg").value;

            fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: message })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById("response").innerText = data.response;
            });
        }
        </script>
    </body>
    </html>
    """)


# ✅ Chat route (GET + POST both)
@app.route("/chat", methods=["GET", "POST"])
def chat():
    # For browser testing
    if request.method == "GET":
        user_input = request.args.get("message", "")
        
        if not user_input:
            return jsonify({"response": "Send message like ?message=hello"})
        
        response = chatbot_response(user_input)
        return jsonify({"response": response})

    # For API (POST)
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return jsonify({"response": "Please send a message."})

    user_input = data["message"]
    response = chatbot_response(user_input)

    return jsonify({"response": response})


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))