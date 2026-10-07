from dataloader import RoadDataset

train_data = RoadDataset("../dataset/train_split")

print("Total samples:", len(train_data))

image, mask = train_data[0]

print("Image shape:", image.shape)
print("Mask shape:", mask.shape)