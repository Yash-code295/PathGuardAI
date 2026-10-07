from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "dataset" / "train"
VALID = ROOT / "dataset" / "valid"

def inspect(folder):
    sat = sorted(folder.glob("*_sat.jpg"))
    masks = sorted(folder.glob("*_mask.png"))

    print(f"\nChecking: {folder.name}")
    print("Satellite images:", len(sat))
    print("Masks:", len(masks))

    print("\nFirst 5 satellite:")
    for x in sat[:5]:
        print(x.name)

    print("\nFirst 5 masks:")
    for x in masks[:5]:
        print(x.name)

inspect(TRAIN)
inspect(VALID)