from flask import Flask, jsonify, request
from googleapiclient.errors import HttpError

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, Vercel!"

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Your upload logic here
        return jsonify({"status": "success"}), 200
    except HttpError as e:
        print(f"Google API error: {e}")
        return jsonify({"error": "Failed to upload"}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
