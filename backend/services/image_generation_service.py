import os
import io
import base64
import uuid
import requests
from PIL import Image

SAVE_DIR = "static/generated"
os.makedirs(SAVE_DIR, exist_ok=True)


def translate_to_english(text: str) -> str:
    """OpenAI API로 한국어 브랜드 설명을 영어로 번역. 실패 시 원문 반환."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or len(api_key) < 20:
        print("OPENAI_API_KEY 미설정, 원문 사용")
        return text
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Translate the following Korean brand description to concise English "
                            "suitable for an image generation prompt. Output only the translation."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                "max_tokens": 150,
            },
            timeout=15,
        )
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("번역 실패, 원문 사용:", e)
        return text


def get_color_hint(url: str) -> str | None:
    """이미지 URL에서 배경 제외 주요 색상을 hex 코드로 추출."""
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize((80, 80))
        quantized = img.quantize(colors=6).convert("RGB")
        palette = quantized.getcolors(maxcolors=10000) or []
        palette.sort(key=lambda x: x[0], reverse=True)
        # 흰색/밝은 배경 제외
        non_white = [
            (cnt, rgb) for cnt, rgb in palette
            if not (rgb[0] > 220 and rgb[1] > 220 and rgb[2] > 220)
        ]
        if not non_white:
            return None
        r, g, b = non_white[0][1]
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception as e:
        print(f"색상 추출 실패 ({url}):", e)
        return None


def get_init_image_b64(url: str) -> str | None:
    """1등 이미지를 768x768로 리사이즈 후 base64로 변환."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize((768, 768))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"1등 이미지 로드 실패 ({url}):", e)
        return None


def build_prompt(
    brand_description: str,
    top3_titles: list,
    top3_captions: list = None,
    style: str = "",
    color_hints: list = None,
) -> str:
    style_map = {
        "이미지": "icon mark only, no text, no letters, pure graphic symbol",
        "이미지+텍스트": "icon symbol combined with brand name text, logotype with emblem",
    }

    style_text = style_map.get(style, "simple clean icon mark, no text")

    # caption이 있으면 시각 묘사 사용, 없으면 제목 텍스트로 폴백
    visual_refs = []
    if top3_captions:
        visual_refs = [c.strip() for c in top3_captions if c and c.strip()]
    if not visual_refs and top3_titles:
        visual_refs = [t for t in top3_titles if t]

    visual_text = " | ".join(visual_refs[:3]) if visual_refs else ""

    hint_text = ""
    if color_hints:
        valid_hints = [h for h in color_hints if h]
        if valid_hints:
            hint_text = f"Incorporate accent color tones: {', '.join(valid_hints)}. "

    prompt = (
        f"Professional logo design for '{brand_description}'. "
        f"Visual style inspired by these reference designs: {visual_text}. "
        f"{style_text}. "
        f"{hint_text}"
        f"Single centered composition on pure white background. "
        f"Flat vector graphic. Clean edges. No watermark. No noise. "
        f"High quality printable brand identity."
    )
    return prompt


async def generate_logo_images(
    brand_description: str,
    top3_titles: list,
    top3_image_urls: list,
    top3_captions: list = None,
    style: str = "",
) -> list:
    COLAB_SD_URL = os.getenv("COLAB_SD_URL")
    if not COLAB_SD_URL:
        raise ValueError("COLAB_SD_URL이 .env에 설정되지 않았습니다.")

    # 브랜드 설명 영어 번역
    print("브랜드 설명 번역 중...")
    brand_en = translate_to_english(brand_description)
    print("번역 결과:", brand_en)

    # 2·3등 이미지에서 색상 힌트 추출 (1등은 init_image로 사용)
    color_hints = []
    for url in top3_image_urls[1:]:
        hint = get_color_hint(url)
        if hint:
            color_hints.append(hint)
    print("색상 힌트:", color_hints)

    prompt = build_prompt(brand_en, top3_titles, top3_captions, style, color_hints)
    print("생성 프롬프트:", prompt)

    # 1등 이미지를 init_image로 전달
    image_b64 = None
    if top3_image_urls:
        print("1등 이미지 로드 중:", top3_image_urls[0])
        image_b64 = get_init_image_b64(top3_image_urls[0])
        print("init_image 준비 완료" if image_b64 else "init_image 로드 실패, 텍스트만으로 생성")

    form_data = {
        "prompt": prompt,
        "num_images": 3,
    }
    if image_b64:
        form_data["image_b64"] = image_b64

    response = requests.post(
        f"{COLAB_SD_URL}/generate",
        data=form_data,
        timeout=300,
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
