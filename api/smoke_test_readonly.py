"""Testes de fumaça somente leitura para MySQL/Aiven e assinatura RSA.

Execute dentro da pasta api: python smoke_test_readonly.py
Não chama init_db(), não executa /verify e não altera registros.
"""
import base64
import sys

import config
from db import _get_mysql_connection
from license_signing import sign_payload
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def main():
    print("[1/3] Verificando configuração TLS...")
    if not config.MYSQL_SSL_ENABLED or not config.MYSQL_SSL_VERIFY_IDENTITY:
        raise RuntimeError("TLS e validação de identidade precisam estar habilitados.")
    if not config.MYSQL_SSL_CA:
        raise RuntimeError("MYSQL_SSL_CA não foi configurada.")
    print("TLS habilitado; CA configurada.")

    print("[2/3] Testando conexão Aiven com consultas somente leitura...")
    conn = _get_mysql_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            if cur.fetchone()["ok"] != 1:
                raise RuntimeError("SELECT 1 retornou resultado inesperado.")
            cur.execute("SELECT COUNT(*) AS total FROM devices")
            total = cur.fetchone()["total"]
        print(f"Conexão TLS OK. Registros em devices: {total} (nenhum registro foi alterado).")
    finally:
        conn.close()

    print("[3/3] Testando assinatura RSA local...")
    signature_b64 = sign_payload('{"smoke_test":"rsa-sha256"}')
    if not signature_b64:
        raise RuntimeError("Chave RSA não carregada; token offline não será emitido.")
    pem = base64.b64decode(config.LICENSE_SIGNING_PRIVATE_KEY_B64, validate=True)
    private_key = serialization.load_pem_private_key(pem, password=None)
    private_key.public_key().verify(
        base64.b64decode(signature_b64, validate=True),
        b'{"smoke_test":"rsa-sha256"}',
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    print("Assinatura RSA-SHA256 criada e verificada com sucesso.")
    print("TESTE CONCLUÍDO: nenhuma licença, usuário ou tabela foi modificada.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FALHA NO TESTE: {exc}", file=sys.stderr)
        raise
