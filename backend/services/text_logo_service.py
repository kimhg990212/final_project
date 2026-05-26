from utils.text_logo_keyword_extractor import extract_keywords
from utils.text_logo_prompt_builder import build_logo_prompt
from utils.text_logo_image_generator import generate_logo_image
# 사용자별로 생성한 이미지를 DB에 저장할 수 있게 구조 잡아놓기
def generate_text_logo(user_text:str, user_id:int | None=None):
    keywords = extract_keywords(user_text)
    prompt = build_logo_prompt(keywords)

    image_result = generate_logo_image(prompt)
    
    history_date = {
        "user_id": user_id,
        "user_text": user_text,
        "keywords": keywords,
        "generated_prompt": prompt,
        "image_url": image_result["image_url"],
        "image_status": image_result["status"]
    }
        # TODO : 로그인/DB 연결 후 history_data 저장
        # save_text_logo_history(history_data)
    return history_date


# 이미지 생성하고 반환하기
# def generate_text_logo(user_text: str):
#     keywords = extract_keywords(user_text)
#     prompt = build_logo_prompt(keywords)
    
#     return {
#         "user_text": user_text,
#         "keywords": keywords,
#         "generated_prompt":prompt,
#         "image_url":"/generated_image/sample_logo.png"
        
#     }