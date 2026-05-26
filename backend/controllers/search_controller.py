from utils.response_utils import (
    success_response,
    error_response
)

from services.embedding_service import (
    create_image_embedding,
    create_text_embedding,
    merge_embeddings
)

from services.vector_search_service import (
    search_dissimilar_vectors
)

async def search_logo_controller(
    image,
    prompt,
    category=None
):

    try:

        # 이미지 벡터 생성
        image_embedding = create_image_embedding(
            image.file
        )

        # 텍스트 벡터 생성
        text_embedding = create_text_embedding(
            prompt
        )

        # 멀티모달 결합
        merged_embedding = merge_embeddings(
            image_embedding,
            text_embedding
        )

        # 비유사 검색
        results = search_dissimilar_vectors(
            merged_embedding,
            top_k=5
        )

        return success_response(

            message="이질적 로고 조회 성공",

            data={
                "category": category,
                "results": results
            }
        )

    except Exception as e:

        return error_response(
            str(e)
        )