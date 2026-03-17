from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from AWS App Runner + Python!"

@app.route("/health")
def health():
    return {"status": "ok"}