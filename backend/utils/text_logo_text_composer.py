import os
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont
from PIL import Image
UPLOAD_DIR = "uploads/images"

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
    icon = icon.resize((520, 520))

    canvas = Image.new("RGBA", (1024, 1024), "WHITE")
    canvas.paste(icon, (252, 120), icon)

    draw = ImageDraw.Draw(canvas)

    font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 120)

    bbox = draw.textbbox((0, 0), logo_text, font=font)
    text_width = bbox[2] - bbox[0]

    x = (1024 - text_width) // 2
    y = 690

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