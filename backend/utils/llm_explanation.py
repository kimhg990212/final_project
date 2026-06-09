import asyncio
import base64
import json
import logging
import mimetypes
import os
import re
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_LLM_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_LLM_MODEL = "gpt-4o-mini"


def _encode_image_as_data_url(image_path: str) -> Optional[str]:
    if not image_path or not os.path.exists(image_path):
        return None

    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _normalize_trademark_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", value).lower()


def _find_overlapping_text(left: Optional[str], right: Optional[str]) -> str:
    left_norm = _normalize_trademark_text(left)
    right_norm = _normalize_trademark_text(right)
    if not left_norm or not right_norm:
        return ""

    common_chars = []
    for char in left_norm:
        if char in right_norm and char not in common_chars:
            common_chars.append(char)

    common_chunks = []
    for size in range(min(len(left_norm), len(right_norm)), 1, -1):
        for start in range(0, len(left_norm) - size + 1):
            chunk = left_norm[start : start + size]
            if chunk in right_norm and chunk not in common_chunks:
                common_chunks.append(chunk)
        if common_chunks:
            break

    parts = []
    if common_chunks:
        parts.append("겹치는 문자열: " + ", ".join(f"'{chunk}'" for chunk in common_chunks[:3]))
    if common_chars:
        parts.append("겹치는 글자: " + ", ".join(f"'{char}'" for char in common_chars[:6]))
    return ". ".join(parts)


def _fallback_reasons(
    *,
    trademark_name_query: Optional[str],
    description_query: Optional[str],
    text_query: Optional[str],
    trademark_name: str,
    name_score: float,
    description_score: float,
    text_score: float,
    image_score: float,
    matched_keywords: list[str],
) -> Dict[str, object]:
    overlap_text = _find_overlapping_text(trademark_name_query, trademark_name)
    keyword_text = ", ".join(matched_keywords) if matched_keywords else ""
    text_reasons = []
    if trademark_name_query:
        if overlap_text:
            text_reasons.append(
                f"입력 상표명 '{trademark_name_query}'와 기존 상표명 '{trademark_name}'에서 {overlap_text}."
            )
        else:
            text_reasons.append(
                f"입력 상표명 '{trademark_name_query}'와 기존 상표명 '{trademark_name}'은 직접 겹치는 글자는 제한적이지만, "
                "텍스트 인덱스에서 표기 흐름이 가까운 후보로 잡혔습니다."
            )
    if description_query:
        text_reasons.append(
            "추가 설명의 표현이 기존 상표의 상표명, OCR 텍스트, 이미지 캡션 정보와 일부 연결됩니다."
        )
    if keyword_text:
        text_reasons.append(f"입력 키워드 중 {keyword_text} 항목이 기존 상표 정보와 직접 맞물립니다.")
    text_reason = " ".join(text_reasons) if text_reasons else "텍스트 입력이 없어 텍스트 기반 근거는 계산되지 않았습니다."
    image_reason = (
        f"업로드 이미지와 '{trademark_name}'의 등록 이미지는 전체 윤곽, 심볼 배치, 문자와 도형의 구성 같은 시각 특징이 가깝게 잡혔습니다."
        if image_score > 0
        else "이미지 입력이 없거나 이미지 유사도 기여가 낮아 시각 근거는 제한적입니다."
    )

    return {
        "text_reason": text_reason,
        "image_reason": image_reason,
        "llm_generated": False,
    }


def _extract_json_object(content: str) -> Dict[str, str]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(content[start : end + 1])


def _sanitize_reason_text(value: Optional[str]) -> str:
    if not value:
        return ""

    text = re.sub(r"\d+(?:\.\d+)?\s*%", "", value)
    sentences = re.split(r"(?<=[.!?。！？])\s+", text.strip())
    filtered = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip() and not any(word in sentence for word in ("점수", "기여도", "퍼센트"))
    ]
    return " ".join(filtered).strip() or text.strip()


async def generate_detection_reason(
    *,
    trademark_name_query: Optional[str],
    description_query: Optional[str],
    text_query: Optional[str],
    uploaded_image_path: Optional[str],
    trademark_name: str,
    application_number: str,
    trademark_image_url: str,
    ocr_text: str,
    caption: str,
    name_score: float,
    description_score: float,
    text_score: float,
    image_score: float,
    total_score: float,
    image_contribution_pct: float,
    text_contribution_pct: float,
    name_contribution_pct: float,
    description_contribution_pct: float,
    matched_keywords: list[str],
) -> Dict[str, object]:
    fallback = _fallback_reasons(
        trademark_name_query=trademark_name_query,
        description_query=description_query,
        text_query=text_query,
        trademark_name=trademark_name,
        name_score=name_score,
        description_score=description_score,
        text_score=text_score,
        image_score=image_score,
        matched_keywords=matched_keywords,
    )

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback

    api_url = os.getenv("LLM_API_URL", DEFAULT_LLM_API_URL)
    model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
    uploaded_image_data_url = _encode_image_as_data_url(uploaded_image_path)

    system_prompt = (
        "너는 한국 상표 도용 탐지 결과를 설명하는 분석가다. "
        "사용자에게 법률 단정이 아니라 유사도 판단 근거를 짧고 명확하게 설명한다. "
        "추측은 피하고, 입력 데이터에서 확인 가능한 부분만 말한다. "
        "설명 문장에는 숫자, 퍼센트, 점수, 기여도를 절대 쓰지 않는다."
    )
    overlap_text = _find_overlapping_text(trademark_name_query, trademark_name)
    user_text = f"""
아래 도용 탐지 결과를 설명해줘.

[사용자 입력]
- 상표명 입력: {trademark_name_query or "없음"}
- 추가 설명 입력: {description_query or "없음"}
- 통합 텍스트: {text_query or "없음"}

[탐지된 기존 상표]
- 상표명: {trademark_name}
- 출원번호: {application_number}
- OCR 텍스트: {ocr_text or "없음"}
- 이미지 캡션: {caption or "없음"}
- 매칭 키워드: {", ".join(matched_keywords) if matched_keywords else "없음"}
- 상표명 글자 겹침: {overlap_text or "직접 겹치는 글자가 제한적임"}

[작성 규칙]
- 화면에 유사도와 기여도가 이미 따로 표시되므로 설명에는 숫자, 퍼센트, 점수, 기여도 표현을 쓰지 마.
- image_reason은 색, 윤곽, 심볼 형태, 문자 배치, 여백, 구도 등 실제 이미지에서 보이는 유사한 부분을 설명해.
- text_reason은 상표명에서 어떤 글자나 문자열이 겹치는지, 또는 표기 흐름이 어떻게 가까운지 설명해.
- 확실히 보이지 않는 시각 요소는 단정하지 말고 "제한적"이라고 말해.

반드시 JSON만 반환해.
형식:
{{
  "image_reason": "이미지에서 어떤 부분이 유사한지 1~2문장. 숫자와 점수 표현 금지.",
  "text_reason": "상표명에서 어떤 글자나 문자열이 겹치는지 1~2문장. 숫자와 점수 표현 금지."
}}
"""

    content = [{"type": "text", "text": user_text}]
    if uploaded_image_data_url:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": uploaded_image_data_url},
            }
        )
    if trademark_image_url:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": trademark_image_url},
            }
        )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        "temperature": 0.2,
        "max_tokens": 450,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    def _request_llm():
        response = requests.post(api_url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        return response.json()

    try:
        data = await asyncio.to_thread(_request_llm)
        message_content = data["choices"][0]["message"]["content"]
        parsed = _extract_json_object(message_content)
        return {
            "image_reason": _sanitize_reason_text(parsed.get("image_reason")) or fallback["image_reason"],
            "text_reason": _sanitize_reason_text(parsed.get("text_reason")) or fallback["text_reason"],
            "llm_generated": True,
        }
    except Exception as exc:
        logger.warning("LLM 탐지 근거 생성 실패: %s", exc)
        return fallback
