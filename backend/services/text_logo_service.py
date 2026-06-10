from utils.text_logo_keyword_extractor import extract_keywords
from utils.text_logo_prompt_builder import build_logo_prompt
from utils.text_logo_image_generator import generate_logo_image
from models.text_to_image_result import TextToImageResult

def generate_text_logo(user_text: str, user_id: int, db):
    if user_id is None:
        return {
            "status": "fail",
            "message": "로그인이 필요합니다."
        }
    keywords = extract_keywords(user_text)
    prompt = build_logo_prompt(keywords)
    image_result = generate_logo_image(prompt)
    saved_id = None
    if image_result.get("status") == "success":
        result = TextToImageResult(
            user_id=user_id,
            prompt=user_text,
            image_path=image_result.get("image_path")
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        saved_id = result.id 
    history_data = {
        "id": saved_id,
        "user_id": user_id,
        "user_text": user_text,
        "keywords": keywords,
        "generated_prompt": prompt,
        "image_path": image_result.get("image_path"),
        "image_url": image_result.get("image_url"),
        "image_status": image_result.get("status"),
        "image_message": image_result.get("message"),
        "comfyui_image_url": image_result.get("comfyui_image_url"),
    }

    return history_data
