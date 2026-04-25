from flask import Flask, request, jsonify, render_template_string
import json
import random

app = Flask(__name__)

# Load intents
try:
    with open("intents.json") as file:
        data = json.load(file)
except Exception as e:
    print("Error loading intents.json:", e)
    exit(1)


# ✅ Simple matching function (lightweight)
def chatbot_response(user_input):
    user_input = user_input.lower()

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input:
                return random.choice(intent["responses"])

    return "For more details, please contact ODM College office."


# ✅ UI for browser
@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot</title>
    </head>
    <body>
        <h2>Chatbot Test</h2>
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


# ✅ Chat API
@app.route("/chat", methods=["GET", "POST"])
def chat():

    # GET (browser)
    if request.method == "GET":
        msg = request.args.get("message", "")
        if not msg:
            return jsonify({"response": "Use ?message=hello"})
        return jsonify({"response": chatbot_response(msg)})

    # POST (API)
    data_req = request.get_json(silent=True)
    if not data_req or "message" not in data_req:
        return jsonify({"response": "Please send a message."})

    return jsonify({"response": chatbot_response(data_req["message"])})


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))