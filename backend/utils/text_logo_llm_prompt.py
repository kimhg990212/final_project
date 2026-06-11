import os
from openai import OpenAI

api_key = os.getenv("OPENAI_TEXT_LOGO_KEY")

if not api_key:
    raise ValueError("OPENAI_TEXT_LOGO_KEY가 .env에 없습니다.")

client = OpenAI(api_key=api_key)


def generate_logo_prompt(user_text: str):
    system_prompt = """
You are an award-winning logo designer and brand identity expert.

Your task is to create a highly detailed image-generation prompt for a professional logo.

Requirements:
- modern vector logo
- premium brand identity
- memorable and unique symbol
- strong silhouette
- scalable design
- clean geometric construction
- balanced composition
- minimal flat design
- elegant negative space usage
- commercial branding quality
- professional color palette
- visually simple but distinctive
- single centered icon only
- white background

Strict rules:
- no text
- no letters
- no words
- no typography
- no watermark
- no signature
- no mockup
- no collage
- no logo sheet
- no multiple logos

The prompt should describe:
1. Symbol concept
2. Visual style
3. Shape language
4. Color palette
5. Branding feeling

Return only the final English prompt.
"""

    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""
            Business Description:
            {user_text}

            Generate a professional logo prompt.
            Focus on brand identity, symbolism, simplicity and commercial usability.
            """
            }
        ]
    )

    return response.output_text.strip()