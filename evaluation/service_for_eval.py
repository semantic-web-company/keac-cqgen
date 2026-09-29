import os
import pandas as pd
from flask import Flask, Response, jsonify
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)

GENERATED_CSV_FILE = os.getenv("GENERATED_QUESTIONS", "generated.csv")

@app.route('/gtg', methods=["GET"])
def gtg():
    """
    GET endpoint used for checking whether the service is up and running.

    :return: "OK" string, if the service is running.
    """
    return "OK"

@app.route('/get_csv', methods=["GET", "POST"])
def get_csv():
    if not os.path.exists(GENERATED_CSV_FILE):
        return jsonify({"error": f"File '{GENERATED_CSV_FILE}' not found"}), 404

    data = pd.read_csv(GENERATED_CSV_FILE)

    return Response(
        response=data.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(GENERATED_CSV_FILE)}"}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)