from pathlib import Path
import random
import cv2
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "train_split"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

sat_files = sorted(DATA.glob("*_sat.jpg"))
sample = random.choice(sat_files)
mask = DATA / sample.name.replace("_sat.jpg", "_mask.png")

img = cv2.imread(str(sample))
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

msk = cv2.imread(str(mask), cv2.IMREAD_GRAYSCALE)

plt.figure(figsize=(12, 5))

plt.subplot(1, 3, 1)
plt.title("Satellite Image")
plt.imshow(img)
plt.axis("off")

plt.subplot(1, 3, 2)
plt.title("Road Mask")
plt.imshow(msk, cmap="gray")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.title("Overlay")
plt.imshow(img)
plt.imshow(msk, cmap="Reds", alpha=0.4)
plt.axis("off")

save_path = OUT / "visual_check.png"
plt.savefig(save_path, bbox_inches="tight")
print("Saved:", save_path)