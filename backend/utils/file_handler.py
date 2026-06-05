import os
import aiofiles
from fastapi import UploadFile, HTTPException, status
from uuid import uuid4

# 업로드 설정 (MVP 기준 로컬 디렉토리 사용)
UPLOAD_DIR = "./uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 허용된 MIME 타입 (요구사항 FR-01-01 기반: PNG, JPG)
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg"}
MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500MB

async def validate_file_and_save(upload_file: UploadFile) -> str:
    """
    업로드된 파일의 유효성을 검증하고 디스크에 스트리밍 방식으로 저장합니다.
    """
    # 1. 파일 형식(MIME Type) 검증 (FR-01-04)
    if upload_file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"지원하지 않는 파일 형식입니다. (지원: PNG, JPG) 입력된 형식: {upload_file.content_type}"
        )

    # 고유한 파일명 생성 (충돌 방지)
    file_extension = upload_file.filename.split(".")[-1]
    unique_filename = f"{uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 2. 파일 크기 검증 (FR-01-02) 및 청크 단위 저장
    # 대용량 파일을 메모리에 한 번에 올리지 않고 aiofiles로 조금씩(chunk) 씁니다.
    actual_size = 0
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await upload_file.read(1024 * 1024):  # 1MB씩 읽기
                actual_size += len(content)
                if actual_size > MAX_FILE_SIZE_BYTES:
                    # 제한 초과 시 즉시 작성 중단 및 파일 삭제
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="파일 크기가 500MB를 초과할 수 없습니다."
                    )
                await out_file.write(content)
    except Exception as e:
        # 실패 시 잔여 파일 정리 (FR-01-06 고려)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"파일 업로드 실패: {str(e)}")

    return file_path