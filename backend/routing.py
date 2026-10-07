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

            ny = y + dy
            nx_ = x + dx

            if (ny, nx_) in point_set:
                G.add_edge((x, y), (nx_, ny), weight=1)

plt.figure(figsize=(8, 8))
plt.imshow(skeleton, cmap="gray")

if len(G.nodes) < 2:
    plt.title("Emergency Route Planning: Not enough road pixels")
    print("Not enough nodes for routing")

else:
    components = list(nx.connected_components(G))
    largest_component = max(components, key=len)
    H = G.subgraph(largest_component).copy()

    nodes = list(H.nodes)

    if len(nodes) < 2:
        plt.title("Emergency Route Planning: No valid connected route")
        print("No valid connected route")

    else:
        start = nodes[0]
        end = nodes[-1]

        try:
            path = nx.shortest_path(H, source=start, target=end, weight="weight")

            for node in path:
                plt.scatter(node[0], node[1], c="lime", s=18)

            plt.scatter(start[0], start[1], c="blue", s=80, label="Start")
            plt.scatter(end[0], end[1], c="red", s=80, label="Destination")

            plt.legend()
            plt.title("Emergency Route Planning")

            print("Connected components:", len(components))
            print("Largest component nodes:", len(H.nodes))
            print("Start:", start)
            print("End:", end)
            print("Path length:", len(path))

        except Exception as e:
            plt.title("Emergency Route Planning: Route unavailable")
            print("Routing failed:", e)

plt.axis("off")

save_path = OUT / "emergency_route.png"
plt.savefig(save_path, bbox_inches="tight")
plt.close()

print("Saved:", save_path)