import jwt
from jwt import PyJWKClient

from ..settings import settings

AUTH_HOST = settings.auth_host
AUTH_REALM = settings.auth_realm

KEYCLOAK_ISSUER = f"{AUTH_HOST}/realms/{AUTH_REALM}"
KEYCLOAK_JWKS = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"


def verify_jwt(token: str) -> dict:
    jwks = PyJWKClient(KEYCLOAK_JWKS)
    key = jwks.get_signing_key_from_jwt(token)
    payload = jwt.decode(token, key, ["RS256"])
    return payload
