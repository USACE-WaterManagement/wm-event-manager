import jwt
from jwt import PyJWKClient
import os

AUTH_HOST = os.getenv("AUTH_HOST")
AUTH_REALM = os.getenv("AUTH_REALM")

KEYCLOAK_ISSUER = f"{AUTH_HOST}/realms/{AUTH_REALM}"
KEYCLOAK_JWKS = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"


def verify_jwt(token: str) -> dict:
    jwks = PyJWKClient(KEYCLOAK_JWKS)
    key = jwks.get_signing_key_from_jwt(token)
    payload = jwt.decode(token, key, ["RS256"])
    return payload
