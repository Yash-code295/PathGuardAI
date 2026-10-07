import cv2
import networkx as nx
from skimage.morphology import skeletonize
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

img = cv2.imread(str(OUT / "pred_mask.png"), cv2.IMREAD_GRAYSCALE)

if img is None:
    print("pred_mask.png not found")
    exit()

binary = img > 0
skeleton = skeletonize(binary)

points = np.argwhere(skeleton)
point_set = set(map(tuple, points))

G = nx.Graph()

for y, x in points:
    G.add_node((int(x), int(y)))

for y, x in points:
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue

            ny, nx_ = y + dy, x + dx

            if (ny, nx_) in point_set:
                G.add_edge((int(x), int(y)), (int(nx_), int(ny)))

total_nodes = len(G.nodes)
total_edges = len(G.edges)

components = list(nx.connected_components(G))
num_components = len(components)

largest_component = max([len(c) for c in components]) if components else 0

connectivity_score = (largest_component / total_nodes) * 100 if total_nodes > 0 else 0
fragmentation_penalty = num_components * 5

score = max(0, connectivity_score - fragmentation_penalty)

status = "Stable"
if score < 50:
    status = "Vulnerable"
elif score < 75:
    status = "Moderate"

data = {
    "score": round(score, 2),
    "status": status
}

with open(OUT / "resilience.json", "w") as f:
    json.dump(data, f)

with open(OUT / "resilience.txt", "w") as f:
    f.write(str(score))

print("Resilience Score:", score)