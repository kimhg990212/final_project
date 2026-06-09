# ──────────────────────────────────────────────
# 셀 1: 멀티모달 다운
# ──────────────────────────────────────────────
# pip install diffusers transformers accelerate safetensors fastapi uvicorn pyngrok python-multipart torch
# ──────────────────────────────────────────────
# 셀 2: SDXL Base 단일 모델 (메모리 최적화 + 고품질)
# ──────────────────────────────────────────────
# import os, io, base64, threading
# import torch
# from PIL import Image
# from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
# from flask import Flask, request, jsonify

# os.system("fuser -k 8000/tcp 2>/dev/null; sleep 1")
# os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# print("모델 로딩 중...")
# pipe = StableDiffusionXLPipeline.from_pretrained(
#     "stabilityai/stable-diffusion-xl-base-1.0",
#     torch_dtype=torch.float16,
#     variant="fp16",
#     use_safetensors=True,
# )
# pipe.scheduler = DPMSolverMultistepScheduler.from_config(
#     pipe.scheduler.config, use_karras_sigmas=True
# )
# pipe.enable_model_cpu_offload()
# pipe.enable_attention_slicing(1)
# pipe.enable_vae_tiling()
# print("✅ 모델 로드 완료")

# app = Flask(__name__)

# NEGATIVE_PROMPT = (
#     "multiple logos, grid, collage, frames, watermark, signature, "
#     "blurry, low quality, distorted, noisy, grainy, pixelated, "
#     "multiple images, side by side, tiled, mosaic, panel, border, "
#     "background pattern, shadow, gradient background, ugly, deformed, "
#     "realistic photo, human face, hands, complex background"
# )

# @app.route("/generate", methods=["POST"])
# def generate():
#     try:
#         prompt     = request.form.get("prompt", "a professional logo")
#         num_images = int(request.form.get("num_images", 1))

#         results = []
#         for i in range(num_images):
#             print(f"[{i+1}/{num_images}] 생성 중...")
#             torch.cuda.empty_cache()

#             output = pipe(
#                 prompt=prompt,
#                 guidance_scale=12.0,
#                 num_inference_steps=50,
#                 negative_prompt=NEGATIVE_PROMPT,
#                 width=1024,
#                 height=1024,
#             ).images[0]

#             buf = io.BytesIO()
#             output.save(buf, format="PNG")
#             results.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
#             print(f"[{i+1}/{num_images}] ✅ 완료")

#         return jsonify({"images_b64": results})

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"status": "ok"})

# t = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000))
# t.daemon = True
# t.start()
# print("🚀 Flask 서버 실행 중 (port 8000)")
# # ──────────────────────────────────────────────
# 셀 3: ngrok 터널
# ──────────────────────────────────────────────
# from pyngrok import ngrok
# import time, requests

# ngrok.set_auth_token("3EHkgXfCcPwIFKlUUZthANMYcjJ_7PWLNZyncrpiooiyuf9WS")  # ← 토큰은 여기에만

# time.sleep(5)  # Flask 서버 시작 대기

# public_url = ngrok.connect(8000).public_url
# print(f"✅ ngrok URL: {public_url}")
# print(f"👉 .env의 COLAB_SD_URL 에 이 값을 붙여넣으세요:\n   {public_url}")

# # 헬스체크
# try:
#     r = requests.get(f"{public_url}/health", timeout=10)
#     print(f"서버 상태: {r.json()}")
# except Exception as e:
#     print(f"헬스체크 실패 (서버 아직 시작 중일 수 있음): {e}")