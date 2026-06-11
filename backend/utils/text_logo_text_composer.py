import os
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont

UPLOAD_DIR = "uploads/images"


def compose_logo_with_text(icon_path: str, logo_name: str):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    icon = Image.open(icon_path).convert("RGBA")
    icon = icon.resize((650, 650))

    canvas = Image.new("RGBA", (1024, 1024), "WHITE")
    canvas.paste(icon, (187, 80), icon)

    draw = ImageDraw.Draw(canvas)

    font_path = "fonts/Pretendard-Bold.ttf"

    try:
        font = ImageFont.truetype(font_path, 90)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), logo_name, font=font)
    text_width = bbox[2] - bbox[0]

    x = (1024 - text_width) // 2
    y = 760

    draw.text(
        (x, y),
        logo_name,
        fill="#222222",
        font=font
    )

    filename = f"text_logo_final_{uuid4().hex}.png"
    save_path = os.path.join(UPLOAD_DIR, filename)

    canvas.convert("RGB").save(save_path)

    return save_path.replace("\\", "/")