import torch
import cv2
from pathlib import Path
from model import get_model

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "road_unet.pth"
UPLOADS = ROOT / "backend" / "uploads"
OUT = ROOT / "outputs"

OUT.mkdir(exist_ok=True)

model = get_model().to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

uploaded_files = [
    f for f in UPLOADS.glob("*")
    if f.suffix.lower() in [".jpg", ".jpeg", ".png"]
]

if not uploaded_files:
    print("No uploaded image found.")
    exit()

# latest uploaded file by modified time
img_path = max(uploaded_files, key=lambda f: f.stat().st_mtime)
print("Using uploaded image:", img_path.name)

img = cv2.imread(str(img_path))

if img is None:
    print("Could not read uploaded image.")
    exit()

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_resized = cv2.resize(img_rgb, (128, 128))

x = img_resized / 255.0
x = torch.tensor(x, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(DEVICE)

with torch.no_grad():
    pred = model(x)
    pred = torch.sigmoid(pred)[0][0].cpu().numpy()

pred_mask = (pred > 0.15).astype("uint8") * 255

cv2.imwrite(str(OUT / "pred_mask.png"), pred_mask)

print("Prediction saved:", OUT / "pred_mask.png")