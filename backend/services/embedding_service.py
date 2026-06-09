from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import numpy as np

# 이미지 임베딩용 CLIP 모델
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# 텍스트 임베딩용 모델 (FAISS 인덱스와 동일한 모델)
text_model = SentenceTransformer("jhgan/ko-sroberta-multitask")

# 텍스트 벡터화
def create_text_embedding(prompt: str):
    vector = text_model.encode(prompt)
    return vector

# 이미지 벡터화
def create_image_embedding(image_file):
    image = Image.open(image_file)
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)
    return image_features[0].numpy()

# 벡터 결합
def merge_embeddings(image_embedding, text_embedding):
    merged = (image_embedding * 0.5 + text_embedding * 0.5)
    return merged.tolist()