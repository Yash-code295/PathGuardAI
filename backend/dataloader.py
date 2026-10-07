from pathlib import Path
import cv2
import torch
from torch.utils.data import Dataset

class RoadDataset(Dataset):
    def __init__(self, folder):
        self.folder = Path(folder)
        self.images = sorted(self.folder.glob("*_sat.jpg"))

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        mask_path = self.folder / img_path.name.replace("_sat.jpg", "_mask.png")

        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (256, 256))

        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        mask = cv2.resize(mask, (256, 256))

        image = image / 255.0
        mask = mask / 255.0

        image = torch.tensor(image, dtype=torch.float32).permute(2, 0, 1)
        mask = torch.tensor(mask, dtype=torch.float32).unsqueeze(0)

        return image, mask