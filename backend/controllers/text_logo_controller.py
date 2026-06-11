from services.text_logo_service import generate_text_logo

def generate_logo_controller(request, db):
    return generate_text_logo(
        logo_name=request.logo_name,
        user_text=request.text,
        user_id=request.user_id,
        db=db
    )