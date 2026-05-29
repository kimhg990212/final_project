import os

try:
    import torch
    import open_clip
    from PIL import Image
    
    clip_model, _, clip_preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="openai")
    clip_tokenizer = open_clip.get_tokenizer("ViT-B-32")
    clip_model.eval()
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

def extract_text_from_file(file_path: str) -> str:
    """파일에서 텍스트 추출 또는 이미지 맥락 분석"""
    ext = os.path.splitext(file_path)[1].lower()
    
    # 텍스트 파일 처리
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    # 이미지 파일 처리 (CLIP 모델 활용)
    elif ext in {".png", ".jpg", ".jpeg"}:
        if not CLIP_AVAILABLE:
            raise RuntimeError("라이브러리 로드 실패: torch, open_clip, PIL 설치 여부를 확인하세요.")
            
        try:
            # 이미지 전처리 및 텐서 변환
            img = Image.open(file_path).convert("RGB")
            image_input = clip_preprocess(img).unsqueeze(0)

            # 후보 텍스트 목록 (이 이미지가 무엇인지 추론)
            candidate_texts = [
                "a logo image",
                "a text document",
                "a photo of object",
                "a diagram or chart",
                "a handwritten document",
            ]
            text_input = clip_tokenizer(candidate_texts)

            # CLIP 예측 (GPU/CPU)
            with torch.no_grad():
                image_features = clip_model.encode_image(image_input)
                text_features = clip_model.encode_text(text_input)

                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)
                similarity = (image_features @ text_features.T).squeeze(0)

            best_match_idx = similarity.argmax().item()
            return candidate_texts[best_match_idx]

        except Exception as e:
        
            raise RuntimeError(f"CLIP 이미지 분석 중 오류 발생: {str(e)}")
    
    # 워드 파일 처리
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            raise RuntimeError(f"Word 파일 읽기 실패: {str(e)}")
            
    return ""