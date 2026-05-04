from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import random

app = Flask(__name__)
CORS(app)

# Load intents
try:
    with open("intents.json") as file:
        data = json.load(file)
except Exception as e:
    print("Error loading intents.json:", e)
    data = {"intents": []}


# Chatbot logic
def chatbot_response(user_input):
    user_input = user_input.lower()

    for intent in data.get("intents", []):
        for pattern in intent.get("patterns", []):
            if pattern.lower() in user_input:
                responses = intent.get("responses", [])
                if responses:
                    return random.choice(responses)

    return "For more details, please contact ODM College office."


# UI (for testing)
@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ODM Chatbot</title>
    </head>
    <body>
        <h2>ODM College Chatbot</h2>
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
            })
            .catch(err => {
                document.getElementById("response").innerText = "Error occurred";
                console.log(err);
            });
        }
        </script>
    </body>
    </html>
    """)


# Main API
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data_req = request.get_json()

        if not data_req or "message" not in data_req:
            return jsonify({"response": "Please send a message."})

        user_msg = data_req["message"]
        bot_reply = chatbot_response(user_msg)

        return jsonify({"response": bot_reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"response": "Server error occurred"})


# Health check
@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)