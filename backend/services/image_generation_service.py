import os
import io
import base64
import uuid
import requests
from PIL import Image

SAVE_DIR = "static/generated"
os.makedirs(SAVE_DIR, exist_ok=True)

def build_prompt(brand_description: str, top3_titles: list, style: str = "", mood: str = "", color: str = "") -> str:
    titles_text = ", ".join([t for t in top3_titles if t])

    style_map = {
        "아이콘만": "icon mark only, no text, no letters, pure symbol mark",
        "텍스트만": "logotype wordmark text only, no icon, no symbol",
        "아이콘+텍스트": "icon symbol combined with brand name text",
    }
    mood_map = {
        "모던/미니멀": "modern minimal clean flat design",
        "클래식/전통": "classic traditional elegant timeless design",
        "귀여움/친근함": "cute friendly fun approachable design",
        "고급스러움/럭셔리": "luxury premium sophisticated high-end design",
    }
    color_map = {
        "밝은 계열": "bright light pastel soft color palette",
        "어두운 계열": "dark deep bold rich color palette",
        "단색": "monochrome black and white single color",
        "컬러풀": "vibrant colorful multi-color energetic palette",
    }

    style_text = style_map.get(style, "simple clean icon mark")
    mood_text = mood_map.get(mood, "modern professional design")
    color_text = color_map.get(color, "balanced color palette")

    prompt = (
        f"Professional logo design for {brand_description}. "
        f"Design style inspired by concepts: {titles_text}. "
        f"{style_text}. "
        f"{mood_text}. "
        f"{color_text}. "
        f"Single centered composition. "
        f"Vector flat logo. "
        f"Pure white background. "
        f"No watermark. No text unless specified. "
        f"High quality brand identity design."
    )
    return prompt


async def generate_logo_images(
    brand_description: str,
    top3_titles: list,
    top3_image_urls: list,
    style: str = "",
    mood: str = "",
    color: str = "",
) -> list:
    COLAB_SD_URL = os.getenv("COLAB_SD_URL")

    if not COLAB_SD_URL:
        raise ValueError("COLAB_SD_URL이 .env에 설정되지 않았습니다.")

    prompt = build_prompt(brand_description, top3_titles, style, mood, color)
    print("생성 프롬프트:", prompt)

    form_data = {
        "prompt": prompt,
        "num_images": 1
    }

    response = requests.post(
        f"{COLAB_SD_URL}/generate",
        data=form_data,
        timeout=300
    )
    response.raise_for_status()
    result = response.json()

    if "error" in result:
        raise ValueError(result["error"])

    saved_paths = []
    for img_b64 in result.get("images_b64", []):
        img_bytes = base64.b64decode(img_b64)
        img = Image.open(io.BytesIO(img_bytes))

        filename = f"logo_{uuid.uuid4().hex}.png"
        save_path = os.path.join(SAVE_DIR, filename)
        img.save(save_path)

        saved_paths.append(f"/static/generated/{filename}")

    return saved_paths