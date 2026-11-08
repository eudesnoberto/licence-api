"""Assinatura RSA dos tokens de licença offline.

A chave privada deve ser fornecida exclusivamente por variável de ambiente:
LICENSE_SIGNING_PRIVATE_KEY_B64 = Base64(arquivo PEM PKCS#8).
"""
import base64
from functools import lru_cache

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

import config


@lru_cache(maxsize=1)
def _load_private_key():
    encoded = config.LICENSE_SIGNING_PRIVATE_KEY_B64
    if not encoded:
        return None
    try:
        pem = base64.b64decode(encoded, validate=True)
        key = serialization.load_pem_private_key(pem, password=None)
    except Exception as exc:
        raise RuntimeError("LICENSE_SIGNING_PRIVATE_KEY_B64 inválida: forneça Base64 de uma chave PEM PKCS#8.") from exc
    if not isinstance(key, rsa.RSAPrivateKey):
        raise RuntimeError("A chave de assinatura precisa ser RSA.")
    if key.key_size < 3072:
        raise RuntimeError("A chave RSA precisa ter pelo menos 3072 bits.")
    return key


def sign_payload(payload_raw: str) -> str | None:
    """Retorna assinatura RSA PKCS#1 v1.5/SHA-256 em Base64 ou None sem chave."""
    key = _load_private_key()
    if key is None:
        return None
    signature = key.sign(
        payload_raw.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("ascii")
