import base64
import time
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from jose import jwt


def _int_to_b64url(n: int, length: int = 32) -> str:
    data = n.to_bytes(length, "big")
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


@pytest.fixture(scope="session")
def test_ec_key():
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    pub_numbers = private_key.public_key().public_numbers()
    jwks = {
        "keys": [
            {
                "kty": "EC",
                "crv": "P-256",
                "x": _int_to_b64url(pub_numbers.x),
                "y": _int_to_b64url(pub_numbers.y),
                "kid": "test-key-1",
                "use": "sig",
                "alg": "ES256",
            }
        ]
    }
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    return {"private_pem": private_pem, "jwks": jwks}


@pytest.fixture(scope="session")
def make_token(test_ec_key):
    def _make(sub: str, active_role: str, expired: bool = False) -> str:
        now = int(time.time())
        payload = {
            "sub": sub,
            "aud": "authenticated",
            "iat": now,
            "exp": now + (-10 if expired else 3600),
            "user_metadata": {"active_role": active_role},
        }
        return jwt.encode(payload, test_ec_key["private_pem"], algorithm="ES256")

    return _make
