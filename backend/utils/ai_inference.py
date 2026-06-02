import logging
import asyncio
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# ==========================================
# 1. AI 모델 전역 로드 (이미지용 / 텍스트용 분리)
# ==========================================
IMAGE_MODEL_NAME = 'clip-ViT-B-32'                  # 이미지를 보는 오리지널 CLIP
TEXT_MODEL_NAME = 'jhgan/ko-sroberta-multitask'   # 한국어를 읽는 다국어 CLIP

try:
    logger.info("AI 모델 로드를 시작합니다. (이미지용과 텍스트용 2개가 로드됩니다)")
    image_model = SentenceTransformer(IMAGE_MODEL_NAME)
    text_model = SentenceTransformer(TEXT_MODEL_NAME)
    logger.info("✅ AI 임베딩 모델 로드 완료 (이미지 & 다국어 텍스트 완벽 지원)")
except Exception as e:
    logger.error(f"❌ AI 모델 로드 실패: {e}")
    image_model = None
    text_model = None


# ==========================================
# 2. 비동기 텍스트 임베딩 함수
# ==========================================
async def embed_text(text: str) -> np.ndarray:
    if text_model is None:
        raise RuntimeError("AI 텍스트 모델이 초기화되지 않았습니다.")

    def _encode_text():
        return text_model.encode(text)

    try:
        vector = await asyncio.to_thread(_encode_text)
        return vector
    except Exception as e:
        logger.error(f"텍스트 벡터 변환 중 오류 발생: {e}")
        raise ValueError("텍스트 분석 중 AI 모델 오류가 발생했습니다.")


# ==========================================
# 3. 비동기 이미지 임베딩 함수
# ==========================================
async def embed_image(image_path: str) -> np.ndarray:
    if image_model is None:
        raise RuntimeError("AI 이미지 모델이 초기화되지 않았습니다.")

    def _encode_image():
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                # 여기서는 image_model(오리지널 CLIP)을 사용합니다!
                return image_model.encode(img)
        except Exception as internal_e:
            raise internal_e

    try:
        vector = await asyncio.to_thread(_encode_image)
        return vector
    except Exception as e:
        logger.error(f"이미지 벡터 변환 중 오류 발생 ({image_path}): {e}")
        raise ValueError("이미지 분석 중 AI 모델 오류가 발생했습니다. 파일이 손상되었는지 확인해주세요.")