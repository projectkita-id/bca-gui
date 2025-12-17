from flask import Flask, request, jsonify
from models import create_record, finish_record
from config import SERVER_HOST, SERVER_POST

app = Flask(__name__)

@app.route("/api/record/start", methods=["POST"])
def start_batch():
    id = create_record()

    return jsonify({
        "status": "ok",
        "record_id": id
    })

@app.route("/api/record/finish", methods=["POST"])
def finish_batch():
    data = request.json()

    if not data or "batch_id" not in data or "items" not in data:
        return jsonify({
            "error": "Invalid payload"
        }), 400
    
    finish_record(
        record_id=data["batch_id"],
        items=data["items"]
    )

    return jsonify({
        "status": "Data updated",
        "total_items": len(data["items"])
    })

if __name__ == "__main__":
    app.run(
        host=SERVER_HOST,
        port=SERVER_POST,
        debug=False
    )