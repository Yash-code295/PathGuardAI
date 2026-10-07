import cv2
import networkx as nx
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from pathlib import Path
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
    y, x = int(y), int(x)
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            ny, nx_ = y + dy, x + dx
            if (ny, nx_) in point_set:
                G.add_edge((x, y), (nx_, ny))

plt.figure(figsize=(8, 8))
plt.imshow(skeleton, cmap="gray")

if len(G.nodes) > 2 and len(G.edges) > 0:
    centrality = nx.betweenness_centrality(G, k=min(200, len(G.nodes)), seed=42)
    top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:20]

    for node, score in top_nodes:
        plt.scatter(node[0], node[1], c="red", s=35)

    print("Top critical nodes generated.")
else:
    print("Not enough road pixels for criticality.")

plt.title("Critical Road Nodes")
plt.axis("off")

save_path = OUT / "critical_nodes_fixed.png"
plt.savefig(save_path, bbox_inches="tight")
plt.close()

print("Saved:", save_path)