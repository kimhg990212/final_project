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
        "아이콘만": "icon mark only, no text, no letters",
        "텍스트만": "logotype text only, no icon",
        "아이콘+텍스트": "icon with brand name text combined",
    }
    mood_map = {
        "모던/미니멀": "modern minimal clean design",
        "클래식/전통": "classic traditional elegant design",
        "귀여움/친근함": "cute friendly approachable design",
        "고급스러움/럭셔리": "luxury premium sophisticated design",
    }
    color_map = {
        "밝은 계열": "bright light pastel color palette",
        "어두운 계열": "dark deep rich color palette",
        "단색": "monochrome single color design",
        "컬러풀": "vibrant colorful multi-color design",
    }

    style_text = style_map.get(style, "")
    mood_text = mood_map.get(mood, "")
    color_text = color_map.get(color, "")

    prompt = f"""
    Professional logo design.
    Brand concept: {brand_description}.
    Inspired by the style characteristics of: {titles_text}.
    {style_text}.
    {mood_text}.
    {color_text}.
    Single centered composition.
    Clean vector design.
    Isolated on plain white background.
    No watermark, no multiple logos.
    High quality brand identity.
    """
    return prompt.strip()


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

    image_b64 = None
    if top3_image_urls:
        try:
            response = requests.get(top3_image_urls[0], timeout=10)
            response.raise_for_status()
            image_b64 = base64.b64encode(response.content).decode("utf-8")
        except Exception:
            image_b64 = None

    form_data = {
        "prompt": prompt,
        "num_images": 1
    }
    if image_b64:
        form_data["image_b64"] = image_b64

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