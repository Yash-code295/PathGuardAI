import cv2
import networkx as nx
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

img = cv2.imread(str(OUT / "pred_mask.png"), cv2.IMREAD_GRAYSCALE)

binary = img > 0
skeleton = skeletonize(binary)

points = np.argwhere(skeleton)

G = nx.Graph()

for y, x in points:
    G.add_node((x, y))

for y, x in points:
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            ny, nx_ = y + dy, x + dx
            if (ny, nx_) in map(tuple, points) and (ny, nx_) != (y, x):
                G.add_edge((x, y), (nx_, ny))

plt.figure(figsize=(8, 8))
nx.draw(G, node_size=2)

save_path = OUT / "road_graph_fixed.png"
plt.savefig(save_path)

print("Graph saved:", save_path)
print("Nodes:", len(G.nodes))
print("Edges:", len(G.edges))