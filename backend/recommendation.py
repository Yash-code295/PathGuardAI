import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

score_file = OUT / "resilience.txt"

score = 0

if score_file.exists():
    with open(score_file, "r") as f:
        score = float(f.read().strip())

risk = "Low"
if score < 50:
    risk = "High"
elif score < 75:
    risk = "Medium"

recommendations = []

if risk == "High":
    recommendations = [
        "Prioritize repair of critical road nodes immediately.",
        "Deploy emergency units near vulnerable junctions.",
        "Create alternate temporary road links.",
        "Use generated rescue route for fast evacuation."
    ]

elif risk == "Medium":
    recommendations = [
        "Monitor weak segments continuously.",
        "Strengthen high-centrality road connections.",
        "Prepare alternate traffic diversion plans."
    ]

else:
    recommendations = [
        "Road network stable.",
        "Maintain regular surveillance.",
        "Keep emergency routes updated."
    ]

output = {
    "risk_level": risk,
    "score": score,
    "recommendations": recommendations
}

with open(OUT / "recommendation.json", "w") as f:
    json.dump(output, f, indent=4)

print("Recommendation generated.")