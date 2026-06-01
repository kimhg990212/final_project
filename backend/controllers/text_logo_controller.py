from services.text_logo_service import generate_text_logo

def generate_logo_controller(request):
    return generate_text_logo(
        user_text=request.text,
        user_id=request.user_id
    )