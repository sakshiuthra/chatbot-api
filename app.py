from flask import Flask, request, jsonify
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Load intents
with open("intents.json") as file:
    data = json.load(file)

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

@app.route("/")
def home():
    return "Chatbot is running!"
    
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
if not user_input:
    return jsonify({"response": "Please send a message."})
    response = chatbot_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))