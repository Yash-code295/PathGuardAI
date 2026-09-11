from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os
import subprocess
import sys


app = Flask(__name__)
CORS(app)


# -----------------------------------------
# PATHS
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR.parent / "outputs"

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# -----------------------------------------
# RUN PYTHON PIPELINE SCRIPT
# -----------------------------------------

def run_script(script_name):

    try:

        env = os.environ.copy()

        # Keep memory/CPU usage low on Render Free
        env["OMP_NUM_THREADS"] = "1"
        env["MKL_NUM_THREADS"] = "1"
        env["OPENBLAS_NUM_THREADS"] = "1"
        env["VECLIB_MAXIMUM_THREADS"] = "1"
        env["NUMEXPR_NUM_THREADS"] = "1"

        script_path = BASE_DIR / script_name

        print(f"Running: {script_path}")

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(BASE_DIR),
            env=env
        )

        if result.returncode != 0:

            return {
                "success": False,
                "script": script_name,
                "error": result.stderr[-5000:],
                "output": result.stdout[-5000:]
            }

        return {
            "success": True,
            "script": script_name,
            "output": result.stdout[-5000:]
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "script": script_name,
            "error": f"{script_name} exceeded the 180 second timeout."
        }

    except Exception as e:

        return {
            "success": False,
            "script": script_name,
            "error": str(e)
        }


# -----------------------------------------
# HOME
# -----------------------------------------

@app.route("/")
def home():

    return jsonify({
        "message": "PathGuardAI Backend Running"
    })


# -----------------------------------------
# UPLOAD
# -----------------------------------------

@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:

        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "error": "Empty filename"
        }), 400

    save_path = UPLOAD_FOLDER / file.filename

    file.save(str(save_path))

    return jsonify({
        "status": "File uploaded successfully",
        "path": str(save_path)
    })


# -----------------------------------------
# OUTPUT FILES
# -----------------------------------------

@app.route("/outputs/<path:filename>")
def serve_outputs(filename):

    return send_from_directory(
        str(OUTPUT_FOLDER),
        filename
    )


# -----------------------------------------
# PIPELINE ENDPOINTS
# -----------------------------------------

@app.route("/predict")
def predict():

    result = run_script("predict.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


@app.route("/criticality")
def criticality():

    result = run_script("criticality.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


@app.route("/simulate")
def simulate():

    result = run_script("simulation.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


@app.route("/route")
def route():

    result = run_script("routing.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


@app.route("/resilience")
def resilience():

    result = run_script("resilience_score.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


@app.route("/recommendation")
def recommendation():

    result = run_script("recommendation.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


# -----------------------------------------
# RESILIENCE JSON
# -----------------------------------------

@app.route("/resilience-data")
def resilience_data():

    return send_from_directory(
        str(OUTPUT_FOLDER),
        "resilience.json"
    )


# -----------------------------------------
# LOCAL DEVELOPMENT
# -----------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )