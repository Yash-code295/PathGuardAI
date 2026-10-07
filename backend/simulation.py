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
point_set = set(map(tuple, points))

G = nx.Graph()

for y, x in points:
    G.add_node((x, y))

for y, x in points:
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            ny, nx_ = y + dy, x + dx
            if (ny, nx_) in point_set and (ny, nx_) != (y, x):
                G.add_edge((x, y), (nx_, ny))

before_components = nx.number_connected_components(G)

centrality = nx.betweenness_centrality(G)
critical_node = max(centrality, key=centrality.get)

G_after = G.copy()
G_after.remove_node(critical_node)

after_components = nx.number_connected_components(G_after)

resilience_drop = after_components - before_components

plt.figure(figsize=(8, 8))
plt.imshow(skeleton, cmap="gray")
plt.scatter(critical_node[0], critical_node[1], c="red", s=80)
plt.title(f"Disaster Simulation: Critical Node Removed\nComponents: {before_components} → {after_components}")
plt.axis("off")

save_path = OUT / "disaster_simulation.png"
plt.savefig(save_path, bbox_inches="tight")

print("Saved:", save_path)
print("Before components:", before_components)
print("After components:", after_components)
print("Resilience impact:", resilience_drop)
print("Removed critical node:", critical_node)