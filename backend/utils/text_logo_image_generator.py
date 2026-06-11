import os
import time
import uuid
import requests
from uuid import uuid4

UPLOAD_DIR = "uploads/images"


def save_image_from_url(image_url: str):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"text_logo_{uuid4().hex}.png"
    save_path = os.path.join(UPLOAD_DIR, filename)

    headers = {
        "ngrok-skip-browser-warning": "true"
    }

    response = requests.get(image_url, headers=headers, timeout=60)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path.replace("\\", "/")


def generate_logo_image(prompt: str):
    comfyui_url = os.getenv("COMFYUI_URL")

    if not comfyui_url:
        return {
            "image_path": None,
            "image_url": None,
            "status": "error",
            "message": "COMFYUI_URL이 .env에 설정되지 않았습니다."
        }

    comfyui_url = comfyui_url.rstrip("/")

    headers = {
        "ngrok-skip-browser-warning": "true"
    }

    logo_prompt = f"""
cute mascot logo,
professional vector logo,
flat logo design,
modern brand identity,
commercial vector icon,
clean geometric shapes,
minimal flat design,
harmonious brand color palette,
aesthetic color combination,
soft premium colors,
well-balanced contrast,
modern brand identity,
award winning logo design,
sharp edges,
centered composition,
white background,
icon only,
no text,
no letters,
no words,
no typography,
no brand name,
single centered symbol,

{prompt}
""".strip()

    negative_prompt = """
ugly colors,
oversaturated,
neon colors,
words,
watermark,
logo sheet,
multiple logos,
collage,
grid,
photo,
realistic,
3d render,
painting,
blurry,
low quality,
distorted,
messy composition
text,
letters,
words,
typography,
brand name,
caption,
watermark,
signature,
random letters,
fake text,
misspelled text,
""".strip()

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int(time.time()),
                "steps": 30,
                "cfg": 7,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["11", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "sd_xl_base_1.0.safetensors"
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": logo_prompt,
                "clip": ["11", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_prompt,
                "clip": ["11", 1]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": "text_to_image"
            }
        },
        "10": {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": "logo_sdxl.safetensors",
                "strength_model": 0.8,
                "strength_clip": 0.8,
                "model": ["4", 0],
                "clip": ["4", 1]
            }
        },
        "11": {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": "Vector_illustration_XL.safetensors",
                "strength_model": 0.5,
                "strength_clip": 0.5,
                "model": ["10", 0],
                "clip": ["10", 1]
            }
        }
    }

    try:
        prompt_response = requests.post(
            f"{comfyui_url}/prompt",
            json={
                "prompt": workflow,
                "client_id": str(uuid.uuid4())
            },
            headers=headers,
            timeout=30
        )

        if prompt_response.status_code != 200:
            return {
                "image_path": None,
                "image_url": None,
                "status": "error",
                "message": prompt_response.text
            }

        prompt_id = prompt_response.json().get("prompt_id")

        for _ in range(300):
            history_response = requests.get(
                f"{comfyui_url}/history/{prompt_id}",
                headers=headers,
                timeout=30
            )

            history = history_response.json()

            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})

                for node_output in outputs.values():
                    images = node_output.get("images")

                    if images:
                        image = images[0]
                        filename = image["filename"]
                        subfolder = image.get("subfolder", "")
                        image_type = image.get("type", "output")

                        comfy_image_url = (
                            f"{comfyui_url}/view"
                            f"?filename={filename}"
                            f"&subfolder={subfolder}"
                            f"&type={image_type}"
                        )

                        local_image_path = save_image_from_url(comfy_image_url)

                        return {
                            "image_path": local_image_path,
                            "image_url": local_image_path,
                            "comfyui_image_url": comfy_image_url,
                            "status": "success",
                            "message": "이미지 생성이 완료되었습니다."
                        }

            time.sleep(1)

        return {
            "image_path": None,
            "image_url": None,
            "status": "timeout",
            "message": "이미지 생성 완료를 기다리다 시간이 초과되었습니다."
        }

    except requests.RequestException as e:
        return {
            "image_path": None,
            "image_url": None,
            "status": "error",
            "message": f"이미지 생성 또는 저장 중 오류가 발생했습니다: {str(e)}"
        }