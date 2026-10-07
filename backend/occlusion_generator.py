import cv2
import numpy as np
from pathlib import Path
import random
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "dataset" / "train_split"
OUTPUT = ROOT / "dataset" / "occluded_train"

OUTPUT.mkdir(exist_ok=True)

sat_files = sorted(INPUT.glob("*_sat.jpg"))

for img_path in tqdm(sat_files):
    img = cv2.imread(str(img_path))

    for _ in range(random.randint(2, 5)):
        x = random.randint(0, img.shape[1] - 30)
        y = random.randint(0, img.shape[0] - 30)

        w = random.randint(15, 40)
        h = random.randint(15, 40)

        color_type = random.choice([
            (255, 255, 255),   # cloud
            (40, 40, 40),      # shadow
            (0, 100, 0)        # tree
        ])

        cv2.rectangle(img, (x, y), (x+w, y+h), color_type, -1)

    save_img = OUTPUT / img_path.name
    save_mask = OUTPUT / img_path.name.replace("_sat.jpg", "_mask.png")

    cv2.imwrite(str(save_img), img)

    original_mask = INPUT / img_path.name.replace("_sat.jpg", "_mask.png")
    mask = cv2.imread(str(original_mask), cv2.IMREAD_GRAYSCALE)

    cv2.imwrite(str(save_mask), mask)

print("Occluded dataset created.")