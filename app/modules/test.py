import clip
import torch
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"

model, preprocess = clip.load("ViT-B/32", device=device)

labels = ["road", "bridge", "building", "tunnel", "damaged infrastructure"]

def classify(path):
    image = preprocess(Image.open(path)).unsqueeze(0).to(device)

    text = clip.tokenize(labels).to(device)

    with torch.no_grad():
        logits_per_image, _ = model(image, text)
        probs = logits_per_image.softmax(dim=-1)

    return labels[probs.argmax()]

print(classify(path="../static/uploads/image.jpg"))