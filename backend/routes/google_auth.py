from fastapi import APIRouter, Depends

from controllers import google_auth_controller as google_auth
from utils.google_auth import require_google_user

router = APIRouter(tags=["Google Auth"])
router.add_api_route("/login", google_auth.google_login_controller, methods=["POST"])
router.add_api_route(
    "/me",
    google_auth.read_google_me_controller,
    methods=["GET"],
    dependencies=[Depends(require_google_user())],
)
router.add_api_route(
    "/admin/me",
    google_auth.read_google_admin_me_controller,
    methods=["GET"],
    dependencies=[Depends(require_google_user(admin_only=True))],
)
