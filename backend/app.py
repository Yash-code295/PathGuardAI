from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os
import subprocess
import sys


app = Flask(__name__)
CORS(app)


# =========================================
# PATHS
# =========================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR.parent / "outputs"

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# =========================================
# RUN PYTHON PIPELINE SCRIPT
# =========================================

def run_script(script_name):

    try:

        env = os.environ.copy()

        # -----------------------------------------
        # Keep CPU / memory usage low on Render Free
        # -----------------------------------------

        env["OMP_NUM_THREADS"] = "1"
        env["MKL_NUM_THREADS"] = "1"
        env["OPENBLAS_NUM_THREADS"] = "1"
        env["VECLIB_MAXIMUM_THREADS"] = "1"
        env["NUMEXPR_NUM_THREADS"] = "1"

        script_path = BASE_DIR / script_name

        print("", flush=True)
        print("========================================", flush=True)
        print(f"STARTING SCRIPT: {script_name}", flush=True)
        print(f"SCRIPT PATH: {script_path}", flush=True)
        print("========================================", flush=True)

        # -----------------------------------------
        # Run subprocess
        # -----------------------------------------

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=170,
            cwd=str(BASE_DIR),
            env=env
        )

        # -----------------------------------------
        # PRINT SUBPROCESS OUTPUT TO RENDER LOGS
        # -----------------------------------------

        print("", flush=True)
        print(f"===== {script_name} STDOUT =====", flush=True)

        if result.stdout:
            print(result.stdout, flush=True)
        else:
            print("(no stdout)", flush=True)

        print(f"===== {script_name} STDERR =====", flush=True)

        if result.stderr:
            print(result.stderr, flush=True)
        else:
            print("(no stderr)", flush=True)

        print(
            f"===== {script_name} RETURN CODE: {result.returncode} =====",
            flush=True
        )

        # -----------------------------------------
        # SCRIPT FAILED
        # -----------------------------------------

        if result.returncode != 0:

            print(
                f"❌ {script_name} FAILED",
                flush=True
            )

            return {
                "success": False,
                "script": script_name,
                "error": result.stderr[-5000:],
                "output": result.stdout[-5000:]
            }

        # -----------------------------------------
        # SCRIPT SUCCESS
        # -----------------------------------------

        print(
            f"✅ {script_name} COMPLETED SUCCESSFULLY",
            flush=True
        )

        return {
            "success": True,
            "script": script_name,
            "output": result.stdout[-5000:]
        }

    # -----------------------------------------
    # SUBPROCESS TIMEOUT
    # -----------------------------------------

    except subprocess.TimeoutExpired:

        print(
            f"❌ {script_name} exceeded 170 second timeout.",
            flush=True
        )

        return {
            "success": False,
            "script": script_name,
            "error": f"{script_name} exceeded the 170 second timeout."
        }

    # -----------------------------------------
    # OTHER ERROR
    # -----------------------------------------

    except Exception as e:

        print(
            f"❌ ERROR running {script_name}: {repr(e)}",
            flush=True
        )

        return {
            "success": False,
            "script": script_name,
            "error": str(e)
        }


# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return jsonify({
        "message": "PathGuardAI Backend Running"
    })


# =========================================
# UPLOAD
# =========================================

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

    print(
        f"✅ Uploaded file: {save_path}",
        flush=True
    )

    return jsonify({
        "status": "File uploaded successfully",
        "path": str(save_path)
    })


# =========================================
# OUTPUT FILES
# =========================================

@app.route("/outputs/<path:filename>")
def serve_outputs(filename):

    return send_from_directory(
        str(OUTPUT_FOLDER),
        filename
    )


# =========================================
# ROAD EXTRACTION
# =========================================

@app.route("/predict")
def predict():

    print("🚀 /predict endpoint called", flush=True)

    result = run_script("predict.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


# =========================================
# CRITICALITY
# =========================================

@app.route("/criticality")
def criticality():

    print("🚀 /criticality endpoint called", flush=True)

    result = run_script("criticality.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


# =========================================
# SIMULATION
# =========================================

@app.route("/simulate")
def simulate():

    print("🚀 /simulate endpoint called", flush=True)

    result = run_script("simulation.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


# =========================================
# ROUTING
# =========================================

@app.route("/route")
def route():

    print("🚀 /route endpoint called", flush=True)

    result = run_script("routing.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


# =========================================
# RESILIENCE
# =========================================

@app.route("/resilience")
def resilience():

    print("🚀 /resilience endpoint called", flush=True)

    result = run_script("resilience_score.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


# =========================================
# RECOMMENDATION
# =========================================

@app.route("/recommendation")
def recommendation():

    print("🚀 /recommendation endpoint called", flush=True)

    result = run_script("recommendation.py")

    status_code = 200 if result["success"] else 500

    return jsonify(result), status_code


# =========================================
# RESILIENCE DATA
# =========================================

@app.route("/resilience-data")
def resilience_data():

    return send_from_directory(
        str(OUTPUT_FOLDER),
        "resilience.json"
    )


# =========================================
# LOCAL DEVELOPMENT
# =========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )