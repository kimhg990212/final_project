from PIL import Image

import torch
from transformers import CLIPProcessor
from transformers import CLIPModel

import numpy as np

# CLIP 모델 로드
model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)

# 텍스트 벡터화
def create_text_embedding(prompt: str):

    inputs = processor(
        text=[prompt],
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():
        text_features = model.get_text_features(**inputs)

    return text_features[0].numpy()

# 이미지 벡터화
def create_image_embedding(image_file):

    image = Image.open(image_file)

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():
        image_features = model.get_image_features(**inputs)

    return image_features[0].numpy()

# 벡터 결합
def merge_embeddings(
    image_embedding,
    text_embedding
):

    merged = (
        image_embedding * 0.5 +
        text_embedding * 0.5
    )

    return merged.tolist()