from services.embedding_service import (
    create_text_embedding,
    create_image_embedding,
    merge_embeddings
)

from services.vector_search_service import (
    search_dissimilar_vectors
)

from services.image_generation_service import (
    generate_logo_images
)

async def generate_logo_controller(
    image,
    prompt,
    category
):

    # 이미지 벡터 생성
    image_embedding = create_image_embedding(
        image.file
    )

    # 텍스트 벡터 생성
    text_embedding = create_text_embedding(
        prompt
    )

    # 벡터 결합
    merged_embedding = merge_embeddings(
        image_embedding,
        text_embedding
    )

    # 비유사 TOP5 검색
    top5_results = search_dissimilar_vectors(
        merged_embedding,
        top_k=5
    )

    # 로고 생성
    generated_images = generate_logo_images(
        prompt,
        top5_results
    )

    return {
        "success": True,
        "message": "로고 생성 완료",
        "top5": top5_results,
        "generated_images": generated_images
    }