"""JWT Authentication module for Better Auth integration."""

from .dependencies import (
    get_current_user,
    get_current_user_id,
    require_authenticated_user,
    verify_user_owns_resource,
    get_user_id_from_path_and_token,
    require_valid_token_only,
)
from .middleware import (
    JWTAuthMiddleware,
    verify_jwt_token,
    verify_user_access,
)
from .utils import (
    decode_jwt_token,
    extract_user_id_from_token,
    is_token_expired,
    validate_token_for_user,
    create_auth_error_response,
)

__all__ = [
    # Dependencies
    "get_current_user",
    "get_current_user_id",
    "require_authenticated_user",
    "verify_user_owns_resource",
    "get_user_id_from_path_and_token",
    "require_valid_token_only",
    # Middleware
    "JWTAuthMiddleware",
    "verify_jwt_token",
    "verify_user_access",
    # Utils
    "decode_jwt_token",
    "extract_user_id_from_token",
    "is_token_expired",
    "validate_token_for_user",
    "create_auth_error_response",
]
