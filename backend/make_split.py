from pathlib import Path
import shutil
import random

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "dataset" / "train"

TRAIN_SPLIT = ROOT / "dataset" / "train_split"
VAL_SPLIT = ROOT / "dataset" / "val_split"

TRAIN_SPLIT.mkdir(exist_ok=True)
VAL_SPLIT.mkdir(exist_ok=True)

sat_files = sorted(TRAIN.glob("*_sat.jpg"))
random.seed(42)
random.shuffle(sat_files)

val_count = int(len(sat_files) * 0.15)

val_files = sat_files[:val_count]
train_files = sat_files[val_count:]

def copy_pairs(files, dest):
    for sat in files:
        mask = TRAIN / sat.name.replace("_sat.jpg", "_mask.png")
        if mask.exists():
            shutil.copy2(sat, dest / sat.name)
            shutil.copy2(mask, dest / mask.name)

copy_pairs(train_files, TRAIN_SPLIT)
copy_pairs(val_files, VAL_SPLIT)

print("Train split images:", len(list(TRAIN_SPLIT.glob("*_sat.jpg"))))
print("Train split masks:", len(list(TRAIN_SPLIT.glob("*_mask.png"))))
print("Val split images:", len(list(VAL_SPLIT.glob("*_sat.jpg"))))
print("Val split masks:", len(list(VAL_SPLIT.glob("*_mask.png"))))