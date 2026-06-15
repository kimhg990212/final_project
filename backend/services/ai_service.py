import os
import base64
import requests

COLAB_SD_URL = os.getenv("COLAB_SD_URL")

def generate_from_file_task(file_path: str, prompt: str, result_id: int):

    from utils.database import SessionLocal
    from models.result_model import GeneratedResult

    db = SessionLocal()

    try:
        with open(file_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        response = requests.post(
            f"{COLAB_SD_URL}/generate_file",
            data={
                "prompt": prompt,
                "image_b64": image_b64,
                "num_images": 1,
            },
            timeout=180
        )
        response.raise_for_status()
        result_data = response.json()

        if "error" in result_data:
            raise ValueError(result_data["error"])

        result_image_b64 = result_data["images_b64"][0]

        db.query(GeneratedResult).filter(
            GeneratedResult.id == result_id
        ).update({"result_image": result_image_b64})
        db.commit()

        return result_image_b64

    except Exception as e:
        db.rollback()
        db.query(GeneratedResult).filter(
            GeneratedResult.id == result_id
        ).update({"result_image": f"오류 발생: {str(e)}"})
        db.commit()
        raise e

    finally:
        db.close()