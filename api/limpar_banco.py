#!/usr/bin/env python3
"""
Script para limpar todos os dados do banco de dados SQLite.
Mantém apenas a estrutura das tabelas e recria o usuário admin padrão.
"""

import sqlite3
from pathlib import Path
import config
from db import _hash_admin_password

DB_PATH = Path(config.DB_PATH)


def limpar_banco():
    """Limpa todos os dados do banco de dados."""
    if not DB_PATH.exists():
        print(f"Banco de dados não encontrado: {DB_PATH}")
        return

    print(f"Conectando ao banco de dados: {DB_PATH}")
    
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        
        # Lista de tabelas para limpar
        tabelas = [
            "devices",
            "blocked_devices",
            "access_logs",
            "license_history",
            "admin_users",
        ]
        
        print("\nLimpando dados das tabelas...")
        for tabela in tabelas:
            try:
                cur.execute(f"DELETE FROM {tabela}")
                count = cur.rowcount
                print(f"  ✓ {tabela}: {count} registro(s) removido(s)")
            except sqlite3.OperationalError as e:
                print(f"  ✗ {tabela}: Erro - {e}")
        
        # Recria o usuário admin padrão
        print("\nRecriando usuário admin padrão...")
        default_user = getattr(config, "ADMIN_DEFAULT_USER", "admin")
        default_pass = getattr(config, "ADMIN_DEFAULT_PASSWORD", "admin123")
        
        cur.execute(
            "INSERT INTO admin_users (username, password_hash, must_change_password) VALUES (?, ?, 1)",
            (default_user, _hash_admin_password(default_pass)),
        )
        print(f"  ✓ Usuário admin criado: {default_user} / {default_pass}")
        
        conn.commit()
        print("\n✓ Banco de dados limpo com sucesso!")
        print(f"  Total de tabelas limpas: {len(tabelas)}")
        print(f"  Usuário admin padrão recriado: {default_user}")


if __name__ == "__main__":
    print("=" * 60)
    print("LIMPEZA DO BANCO DE DADOS")
    print("=" * 60)
    print()
    
    resposta = input("Tem certeza que deseja limpar TODOS os dados? (sim/nao): ")
    
    if resposta.lower() in ["sim", "s", "yes", "y"]:
        limpar_banco()
    else:
        print("\nOperação cancelada.")




