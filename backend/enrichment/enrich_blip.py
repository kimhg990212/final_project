import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
from io import BytesIO
import re
from collections import Counter
from sqlalchemy import text
from utils.database import engine

BATCH_SIZE = 20000
PROMPT = "a logo showing"   

# === 노이즈 필터링 ===
def clean_caption(caption):
    """BLIP 캡션 정제 — 노이즈 제거"""
    if not caption:
        return ""
    
    caption = caption.strip()
    
    # 1. 너무 짧은 경우 빈 문자열 반환
    if len(caption) < 5:
        return ""
    
    # 2.같은 글자 5번 이상 반복(예: "@@@@@", "aaaaa")인 경우
    if re.search(r'(.)\1{4,}', caption):
        return ""
    
    # 3. 같은 단어 반복 패턴인 경우
    words = caption.split()
    if len(words) >= 6 and len(set(words)) <= 2:
        return ""
    
    # 4. 같은 단어가 전체의 절반 이상인 경우
    if len(words) >= 3:
        if max(Counter(words).values()) > len(words) / 2:
            return ""
    
    return caption


def generate_caption(image_url):
    """이미지 URL에서 BLIP 캡션 생성. 실패 시 빈 문자열."""
    try:
        response = requests.get(image_url, timeout=10) 
        img = Image.open(BytesIO(response.content)).convert("RGB")
        
        inputs = processor(img, PROMPT, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        raw_caption = processor.decode(out[0], skip_special_tokens=True)
        
        return clean_caption(raw_caption.strip()) 
    
    except Exception as e:
        print(f"  실패: {e}")
        return ""

print("BLIP 모델 로드 중...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base") 
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base") 
print("모델 로드 완료\n")

with engine.begin() as conn:
    rows = conn.execute(
        text(f"""
            SELECT id, big_image_url 
            FROM trademark_trends 
            WHERE caption IS NULL AND big_image_url IS NOT NULL AND big_image_url != ''
            LIMIT {BATCH_SIZE}
        """)
    ).fetchall()
   
    print(f"처리할 행: {len(rows)}개\n")
    
    # 각 행마다 별도 트랜잭션으로 commit  
    for i, row in enumerate(rows, 1):
        print(f"[{i}/{len(rows)}] id={row.id} 캡션 생성 중...")
        
        try:
            caption = generate_caption(row.big_image_url)
        except Exception as e:
            print(f"  ⚠️ 예외 발생: {e}")
            caption = None   
            
        if not caption:    
            caption_value = None  
        else:
            caption_value = caption
            
            conn.execute(text("""     
                UPDATE trademark_trends 
                SET caption = :caption 
                WHERE id = :id
            """), {"caption": caption_value, "id": row.id}) 
                  
        preview = (caption[:80] if caption else "(빈 결과 → NULL)")
        print(f"  → {preview}\n")
   
print("=" * 50)
print("완료!")
