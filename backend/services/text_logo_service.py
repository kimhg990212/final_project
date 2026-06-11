# from utils.text_logo_keyword_extractor import extract_keywords
# from utils.text_logo_prompt_builder import build_logo_prompt
from utils.text_logo_image_generator import generate_logo_image
from models.text_to_image_result import TextToImageResult
from utils.text_logo_text_composer import compose_logo_with_text
from utils.text_logo_llm_prompt import generate_logo_prompt

def generate_text_logo(logo_name: str, user_text: str, user_id: int, db):
    if user_id is None:
        return {
            "status": "fail",
            "message": "로그인이 필요합니다."
        }

    # keywords = extract_keywords(user_text)
    # prompt = build_logo_prompt(keywords)
    prompt = generate_logo_prompt(user_text)
    image_result = generate_logo_image(prompt)

    final_image_path = None
    saved_id = None

    if image_result.get("status") == "success":
        final_image_path = compose_logo_with_text(
            image_path=image_result.get("image_path"),
            logo_text=logo_name
        )

        result = TextToImageResult(
            user_id=user_id,
            prompt=user_text,
            image_path=final_image_path
        )

        db.add(result)
        db.commit()
        db.refresh(result)
        saved_id = result.id

    history_data = {
        "id": saved_id,
        "user_id": user_id,
        "logo_text": logo_name,
        "user_text": user_text,
        "generated_prompt": prompt,
        "image_path": final_image_path,
        "image_url": final_image_path,
        "image_status": image_result.get("status"),
        "image_message": image_result.get("message"),
        "comfyui_image_url": image_result.get("comfyui_image_url"),
        "original_image_path": image_result.get("image_path")
    }

    return history_data