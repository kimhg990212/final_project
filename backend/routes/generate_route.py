from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from controllers.generate_controller import (
    generate_logo_controller
)

router = APIRouter(
    prefix="/generate",
    tags=["Generate"]
)

@router.post("/logo")

async def generate_logo(

    image: UploadFile = File(...),
    prompt: str = Form(...),
    category: str = Form(...)

):

    return await generate_logo_controller(
        image=image,
        prompt=prompt,
        category=category
    )