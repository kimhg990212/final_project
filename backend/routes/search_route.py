from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from controllers.search_controller import (
    search_logo_controller
)

router = APIRouter(

    prefix="/search",
    tags=["Search"]
)

@router.post("/logo")

async def search_logo(

    image: UploadFile = File(...),

    prompt: str = Form(...),

    category: str = Form(None)
):

    return await search_logo_controller(

        image=image,

        prompt=prompt,

        category=category
    )