import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env")) 

import pytesseract
from PIL import Image
import requests
from io import BytesIO
import re
from sqlalchemy import text
from utils.database import engine

MIN_CONFIDENCE = 70  # 기본 임계값
MIN_IMAGE_SIZE = 300
BATCH_SIZE = 20000

TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")
if not TESSERACT_CMD:
    raise ValueError("TESSERACT_CMD 환경변수를 .env에 설정하세요")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# === 노이즈 필터링 ===
def clean_ocr_text(text_value):
    """OCR 결과 정제 — 노이즈 제거"""
    if not text_value:
        return ""
    
    text_value = text_value.strip()
    
    # 1. 너무 짧은 경우 
    if len(text_value) < 2:
        return ""
    
    # 2. 특수문자만 있는 경우(@@@@, !!!! 등) 
    if re.fullmatch(r'[^\w가-힣]+', text_value):
        return ""
    
    # 3. 같은 문자 반복인(aaaaa) 경우
    if re.fullmatch(r'(.)\1{4,}', text_value):
        return ""
    
    # 4. 자음/모음만 있는 경우(한글 깨짐) 
    if re.fullmatch(r'[ㄱ-ㅎㅏ-ㅣ\s]+', text_value):
        return ""
    
    return text_value

def run_ocr(image_url, min_confidence=MIN_CONFIDENCE):
    """
    이미지 URL에서 OCR 실행. 신뢰도 70% 이상 단어만 추출. 데이터 정제까지 적용
    Args:
          image_url: KIPRIS 이미지 URL (big_image_url)
          min_confidence: 신뢰도 임계값 (0~100, 기본 70)
    
    Returns:
          OCR 결과 텍스트 (실패 시 빈 문자열)
    """
    try:
        # 이미지 다운로드
        response = requests.get(image_url, timeout=10)  
        img = Image.open(BytesIO(response.content)).convert("RGB")
    
        # 작으면 확대
        if img.width < MIN_IMAGE_SIZE or img.height < MIN_IMAGE_SIZE:
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
        
        # OCR 실행 
        data = pytesseract.image_to_data(
            img, # PIL Image 객체 (다운로드한 이미지)
            lang="kor+eng",  # 사용할 OCR 언어 
            output_type=pytesseract.Output.DICT   # 반환 형식 지정(딕셔너리)
        )
        
        # 신뢰도 70% 이상 단어만 모으기
        words = []
        for i, word in enumerate(data['text']):
            word = word.strip()
            if not word:
                continue
            confidence = int(data['conf'][i])
            if confidence >= min_confidence:
                words.append(word)
        
        # 단어들 공백으로 연결
        raw_text = ' '.join(words)
        
        # 노이즈 정제 후 반환
        return clean_ocr_text(raw_text)    
    
    except Exception as e:
        print(f"  실패: {e}")
        return ""


# OCR 재처리
with engine.begin() as conn:
    rows = conn.execute(text(f"""
        SELECT id, big_image_url 
        FROM trademark_trends 
        WHERE ocr_text IS NULL AND big_image_url IS NOT NULL
        LIMIT {BATCH_SIZE} 
    """)).fetchall()
    
    print(f"처리할 행: {len(rows)}개\n")
    
    for i, row in enumerate(rows, 1):
        print(f"[{i}/{len(rows)}] id={row.id} OCR 중...")
        ocr_text = run_ocr(row.big_image_url)
        
        # 빈 결과면 NULL로 (추후 데이터 정제 재처리 가능하게)
        ocr_value = ocr_text if ocr_text else None    
    
        conn.execute(text("""
            UPDATE kipris_trademarks 
            SET ocr_text = :ocr_text 
            WHERE id = :id
        """), {"ocr_text": ocr_value, "id": row.id}) 
        
        preview = ocr_text[:60] if ocr_text else "(빈 결과)"
        print(f"  → {preview}\n")

print("=" * 50)
print("완료!")
