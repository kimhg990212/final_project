import os
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont
import math

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_DIR = "uploads/images"


# 텍스트 색깔 랜덤으로 관련 깊은 색 정하기
def extract_text_color(image_path):
    img = Image.open(image_path).convert("RGB")

    # 크기 줄여서 연산량 감소
    img = img.resize((100, 100))

    colors = img.getcolors(10000)

    # 흰색 제외
    filtered = []

    for count, color in colors:
        r, g, b = color

        if r > 240 and g > 240 and b > 240:
            continue

        filtered.append((count, color))

    if not filtered:
        return "#222222"

    # 가장 많이 나온 색
    dominant = max(filtered, key=lambda x: x[0])[1]

    r, g, b = dominant

    # 텍스트용으로 조금 더 진하게
    r = max(0, int(r * 0.7))
    g = max(0, int(g * 0.7))
    b = max(0, int(b * 0.7))

    return (r, g, b)


def compose_logo_with_text(image_path: str, logo_text: str):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    text_color = extract_text_color(image_path)

    icon = Image.open(image_path).convert("RGBA")

    # 위쪽 아이콘 부분만 자르기
    icon = icon.crop((0, 0, icon.width, int(icon.height * 0.7)))

    icon = icon.resize((430, 430))

    canvas = Image.new("RGBA", (1024, 1024), "WHITE")

    # 이미지 위치: 기존 120보다 위로
    canvas.paste(icon, ((1024-430)//2, 130), icon)

    draw = ImageDraw.Draw(canvas)
    
    font_path = os.path.join(
        BASE_DIR,
        "font",
        "KimjungchulScript-Bold.otf"
    )
    font = ImageFont.truetype(font_path, 100)

    bbox = draw.textbbox((0, 0), logo_text, font=font)
    text_width = bbox[2] - bbox[0]

    x = (1024 - text_width) // 2

    # 텍스트 위치: 기존 690보다 위로
    y = 560

    draw.text(
        (x, y),
        logo_text,
        fill=text_color,
        font=font
    )

    filename = f"text_logo_final_{uuid4().hex}.png"
    save_path = os.path.join(UPLOAD_DIR, filename)

    canvas.convert("RGB").save(save_path)

    return save_path.replace("\\", "/")