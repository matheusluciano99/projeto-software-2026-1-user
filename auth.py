import os
from functools import wraps

import requests
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator
from flask import jsonify

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "dev-x65bk1hkee81c774.us.auth0.com")
AUTH0_AUDIENCE = os.environ.get(
    "AUTH0_AUDIENCE", "https://dev-x65bk1hkee81c774.us.auth0.com/api/v2/"
)
ROLES_CLAIM = os.environ.get("AUTH0_ROLES_CLAIM", "https://social-insper.com/roles")


class Auth0JWTBearerTokenValidator(JWTBearerTokenValidator):
    def __init__(self, domain, audience):
        jwks = requests.get(f"https://{domain}/.well-known/jwks.json").json()
        super().__init__(jwks)
        self.claims_options = {
            "exp": {"essential": True},
            "aud": {"essential": True, "value": audience},
            "iss": {"essential": True, "value": f"https://{domain}/"},
        }


require_auth = ResourceProtector()
require_auth.register_token_validator(
    Auth0JWTBearerTokenValidator(AUTH0_DOMAIN, AUTH0_AUDIENCE)
)


def requires_role(role: str):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = require_auth.acquire_token()
            roles = token.get(ROLES_CLAIM, []) or []
            if role not in roles:
                return jsonify({"message": f"Role {role} required"}), 403
            return f(*args, **kwargs)

        return decorated

    return decorator
