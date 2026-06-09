from utils.response_utils import success_response, error_response
from services.image_generation_service import generate_logo_images
from utils.database import SessionLocal
from sqlalchemy import text

async def generate_logo_controller(
    trademark_ids: list,
    brand_description: str,
    style: str = "",
    mood: str = "",
    color: str = "",
):
    try:
        with SessionLocal() as db:
            result = db.execute(
                text("""
                    SELECT id, title, classification_code, image_url, big_image_url
                    FROM kipris_trademarks
                    WHERE id IN :ids
                """),
                {"ids": tuple(trademark_ids)}
            )
            rows = result.mappings().all()

        if not rows:
            return error_response("상표 정보를 찾을 수 없습니다.")

        titles = [row["title"] for row in rows if row["title"]]
        image_urls = [
            row["image_url"] or row["big_image_url"]
            for row in rows
            if row["image_url"] or row["big_image_url"]
        ]

        generated_images = await generate_logo_images(
            brand_description=brand_description,
            top3_titles=titles,
            top3_image_urls=image_urls,
            style=style,
            mood=mood,
            color=color,
        )

        return success_response(
            message="로고 생성 완료",
            data={"generated_images": generated_images}
        )

    except Exception as e:
        return error_response(str(e))