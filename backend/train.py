import os
import torch
import segmentation_models_pytorch as smp
from torch.utils.data import DataLoader, Subset
from tqdm import tqdm
from dataloader import RoadDataset
from model import get_model

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", DEVICE)

train_data = RoadDataset("../dataset/occluded_train")
val_data = RoadDataset("../dataset/val_split")

# Stronger training but still manageable on CPU
train_data = Subset(train_data, range(1500))
val_data = Subset(val_data, range(300))

train_loader = DataLoader(train_data, batch_size=1, shuffle=True)
val_loader = DataLoader(val_data, batch_size=1, shuffle=False)

model = get_model().to(DEVICE)

loss_fn = smp.losses.DiceLoss(mode="binary")
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

EPOCHS = 5

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    loop = tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}")

    for images, masks in loop:
        images = images.to(DEVICE)
        masks = masks.to(DEVICE)

        preds = model(images)
        loss = loss_fn(preds, masks)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        loop.set_postfix(loss=loss.item())

    avg_loss = total_loss / len(train_loader)
    print(f"Epoch {epoch+1} Average Loss: {avg_loss:.4f}")

os.makedirs("../models", exist_ok=True)
torch.save(model.state_dict(), "../models/road_unet.pth")

print("Model saved: ../models/road_unet.pth")