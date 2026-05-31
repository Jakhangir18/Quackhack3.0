"""Flask server for the Touchpoint motor playback demo."""

import threading
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


def play_string(word):
    from output.motors import buzz_word

    buzz_word(word)


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.post("/play")
def play():
    data = request.get_json(silent=True) or {}
    word = str(data.get("word", ""))
    threading.Thread(target=play_string, args=(word,), daemon=True).start()
    return jsonify({"status": "ok"})


def main():
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
