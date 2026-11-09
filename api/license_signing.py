"""Assinatura RSA dos tokens de licença offline.

Prefere o Secret File do Render em /etc/secrets/license_signing_private.pem.
LICENSE_SIGNING_PRIVATE_KEY_FILE permite escolher outro caminho. A variável
LICENSE_SIGNING_PRIVATE_KEY_B64 continua como fallback temporário de migração.
"""
import base64
import os
from functools import lru_cache
from pathlib import Path

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

import config


@lru_cache(maxsize=1)
def _load_private_key():
    configured_path = os.getenv("LICENSE_SIGNING_PRIVATE_KEY_FILE", "").strip()
    key_path = Path(configured_path) if configured_path else Path("/etc/secrets/license_signing_private.pem")
    try:
        pem = key_path.read_bytes()
    except FileNotFoundError as exc:
        if configured_path:
            raise RuntimeError("Arquivo da chave RSA configurado não foi encontrado.") from exc
        encoded = config.LICENSE_SIGNING_PRIVATE_KEY_B64
        if not encoded:
            return None
        try:
            pem = base64.b64decode(encoded, validate=True)
        except Exception as decode_exc:
            raise RuntimeError("LICENSE_SIGNING_PRIVATE_KEY_B64 inválida.") from decode_exc
    except OSError as exc:
        raise RuntimeError("Não foi possível ler o arquivo da chave RSA.") from exc

    try:
        key = serialization.load_pem_private_key(pem, password=None)
    except (TypeError, ValueError, UnsupportedAlgorithm) as exc:
        raise RuntimeError("A chave privada RSA não é um PEM válido sem senha.") from exc
    if not isinstance(key, rsa.RSAPrivateKey):
        raise RuntimeError("A chave de assinatura precisa ser RSA.")
    if key.key_size < 3072:
        raise RuntimeError("A chave RSA precisa ter pelo menos 3072 bits.")
    return key


def load_private_key():
    """Retorna a chave RSA carregada, ou None se a assinatura estiver desativada."""
    return _load_private_key()


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
