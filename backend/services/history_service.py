from models.history_model import History

from repositories.history_repository import (
    save_generation_history
)

def create_history(
    db,
    prompt,
    category,
    image_path,
    result1,
    result2
):

    history = History(

        prompt=prompt,
        category=category,
        image_path=image_path,
        result_image1=result1,
        result_image2=result2
    )

    return save_generation_history(
        db,
        history
    )