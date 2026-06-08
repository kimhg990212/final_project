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

    response = requests.get(image_url, timeout=60)
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

    logo_prompt = f"""
ONE single logo only.
A single centered icon mark.
Only one symbol in the entire image.
Minimal flat vector logo.
Clean simple outline.
Isolated on plain white background.
No grid, no collage, no logo sheet, no variations, no multiple icons.
No panels, no frames, no mockup.
Professional brand identity logo.
{prompt}
"""

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int(time.time()),
                "steps": 25,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["10", 0],
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
                "width": 512,
                "height": 512,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": logo_prompt,
                "clip": ["10", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "grid, collage, logo sheet, multiple logos, multiple icons, variations, panels, divided layout, tiled layout, split screen, repeated symbols, poster, mockup, packaging, menu board, text, letters, watermark, blurry, low quality, realistic, photo, painting, 3d, complex background",
                "clip": ["10", 1]
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
                "strength_model": 1.0,
                "strength_clip": 1.0,
                "model": ["4", 0],
                "clip": ["4", 1]
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