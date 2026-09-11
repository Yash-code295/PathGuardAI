import os

# Keep CPU libraries lightweight on Render Free
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import torch
import cv2
from pathlib import Path
from model import get_model


# Render Free = CPU
DEVICE = torch.device("cpu")

# Limit PyTorch CPU usage
torch.set_num_threads(1)
torch.set_num_interop_threads(1)


ROOT = Path(__file__).resolve().parent

MODEL_PATH = ROOT / "road_unet.pth"
UPLOADS = ROOT / "uploads"

# outputs is outside backend:
# backend/../outputs
OUT = ROOT.parent / "outputs"

OUT.mkdir(parents=True, exist_ok=True)


print("========================================")
print("PathGuardAI Road Extraction")
print("========================================")
print("Device:", DEVICE)
print("Model:", MODEL_PATH)
print("Uploads:", UPLOADS)
print("Outputs:", OUT)


# -----------------------------------------
# LOAD MODEL
# -----------------------------------------

print("Loading model...")

model = get_model()

checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

model.load_state_dict(checkpoint)

del checkpoint

model.eval()
model.to(DEVICE)

print("Model loaded successfully.")


# -----------------------------------------
# FIND LATEST UPLOADED IMAGE
# -----------------------------------------

uploaded_files = [
    f
    for f in UPLOADS.glob("*")
    if f.is_file()
    and f.suffix.lower() in [".jpg", ".jpeg", ".png"]
]

if not uploaded_files:
    print("No uploaded image found.")
    raise SystemExit(0)


img_path = max(
    uploaded_files,
    key=lambda f: f.stat().st_mtime
)

print("Using uploaded image:", img_path.name)


# -----------------------------------------
# READ IMAGE
# -----------------------------------------

img = cv2.imread(str(img_path))

if img is None:
    print("Could not read uploaded image.")
    raise SystemExit(1)


img_rgb = cv2.cvtColor(
    img,
    cv2.COLOR_BGR2RGB
)


# -----------------------------------------
# RESIZE FOR INFERENCE
# -----------------------------------------

img_resized = cv2.resize(
    img_rgb,
    (128, 128),
    interpolation=cv2.INTER_AREA
)


# -----------------------------------------
# CREATE TENSOR
# -----------------------------------------

x = torch.from_numpy(
    img_resized
).float()

x = x / 255.0

x = x.permute(2, 0, 1)

x = x.unsqueeze(0)

x = x.contiguous()

x = x.to(DEVICE)


# -----------------------------------------
# INFERENCE
# -----------------------------------------

print("Running road extraction...")

with torch.inference_mode():

    pred = model(x)

    pred = torch.sigmoid(pred)

    pred = pred[0, 0].cpu().numpy()


# -----------------------------------------
# CREATE ROAD MASK
# -----------------------------------------

pred_mask = (
    pred > 0.15
).astype("uint8") * 255


output_path = OUT / "pred_mask.png"

cv2.imwrite(
    str(output_path),
    pred_mask
)


# -----------------------------------------
# CLEANUP
# -----------------------------------------

del x
del pred
del img
del img_rgb
del img_resized

print("Prediction saved:", output_path)
print("ROAD EXTRACTION COMPLETE")
print("========================================")