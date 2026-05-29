from diffusers import StableDiffusionPipeline

import torch

# 모델 로드
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float32
)

# GPU 사용 가능 시 GPU 사용
if torch.cuda.is_available():
    pipe = pipe.to("cuda")

def generate_logo_images(
    prompt,
    top5_results
):

    # 비유사 특징 기반 프롬프트 생성
    enhanced_prompt = f'''
    Create a unique logo design.

    User Prompt:
    {prompt}

    Requirements:
    - highly original
    - minimal design
    - avoid common logo structures
    - modern typography
    - geometric style
    '''

    generated_images = []

    # 2개 생성
    for i in range(2):

        image = pipe(
            enhanced_prompt,
            num_inference_steps=25
        ).images[0]

        file_path = (
            f"app/static/generated/logo_{i}.png"
        )

        image.save(file_path)

        generated_images.append(file_path)

    return generated_images