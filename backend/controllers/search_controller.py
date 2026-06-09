from utils.categories import get_nice_codes, get_all_categories
from utils.response_utils import success_response, error_response
from services.embedding_service import create_text_embedding
from services.vector_search_service import search_dissimilar_by_category
import traceback

def get_categories_controller():
    categories = get_all_categories()
    return success_response(
        message="카테고리 목록 조회 성공",
        data={"categories": categories}
    )

async def search_logo_controller(
    category_name: str,
    brand_description: str
):
    try:
        print("1. 카테고리:", category_name)
        nice_codes = get_nice_codes(category_name)
        print("2. 니스코드:", nice_codes)

        if not nice_codes:
            return error_response("유효하지 않은 카테고리입니다.")

        print("3. 임베딩 시작")
        text_embedding = create_text_embedding(brand_description)
        print("4. 임베딩 완료")

        results = search_dissimilar_by_category(
            query_vector=text_embedding,
            nice_codes=nice_codes,
            top_k=3
        )
        print("5. 검색 완료 결과수:", len(results))

        return success_response(
            message="비유사 로고 조회 성공",
            data={
                "category": category_name,
                "nice_codes": nice_codes,
                "results": results
            }
        )

    except Exception as e:
        print("에러 발생 상세:", traceback.format_exc())
        return error_response(str(e))