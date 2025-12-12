#!/usr/bin/env python3
"""
Script para adicionar ou atualizar email de um usuário.
Execute: python adicionar_email_usuario.py
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('api/.env')

# Importar módulos do sistema
sys.path.insert(0, 'api')
from db import get_conn, get_cursor, USE_MYSQL

def adicionar_email_usuario(username: str, email: str):
    """Adiciona ou atualiza email de um usuário na tabela users."""
    
    print("\n" + "=" * 60)
    print(f"  📧 Adicionando Email ao Usuário")
    print("=" * 60)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        
        # Verificar se usuário existe
        if USE_MYSQL:
            cur.execute("SELECT id, username, email FROM users WHERE username = %s LIMIT 1", (username,))
        else:
            cur.execute("SELECT id, username, email FROM users WHERE username = ? LIMIT 1", (username,))
        
        row = cur.fetchone()
        
        if not row:
            # Usuário não existe, criar
            print(f"\n⚠️  Usuário '{username}' não encontrado na tabela 'users'")
            criar = input(f"Deseja criar o usuário '{username}' com email '{email}'? (s/n): ").strip().lower()
            
            if criar != 's':
                print("❌ Operação cancelada")
                return False
            
            # Criar usuário (sem senha por enquanto, será necessário definir depois)
            print(f"\n⚠️  ATENÇÃO: Será criado um usuário sem senha.")
            print(f"   Você precisará definir a senha depois ou usar 'Alterar Senha' no dashboard.")
            confirmar = input("Continuar? (s/n): ").strip().lower()
            
            if confirmar != 's':
                print("❌ Operação cancelada")
                return False
            
            # Hash de senha temporário (usuário precisará alterar)
            import hashlib
            temp_password_hash = hashlib.sha256(f"user-salt::temp123".encode("utf-8")).hexdigest()
            
            if USE_MYSQL:
                cur.execute(
                    "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                    (username, temp_password_hash, email, 'admin')
                )
            else:
                cur.execute(
                    "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                    (username, temp_password_hash, email, 'admin')
                )
            
            conn.commit()
            print(f"✅ Usuário '{username}' criado com email '{email}'")
            print(f"⚠️  IMPORTANTE: Defina uma senha no dashboard usando 'Alterar Senha'")
            return True
        else:
            # Usuário existe, atualizar email
            if USE_MYSQL:
                user_id, user_username, user_email = row['id'], row['username'], row['email']
            else:
                user_id, user_username, user_email = row[0], row[1], row[2]
            
            print(f"\n✓ Usuário encontrado:")
            print(f"   ID: {user_id}")
            print(f"   Usuário: {user_username}")
            print(f"   Email atual: {user_email if user_email else '❌ SEM EMAIL'}")
            
            if user_email == email:
                print(f"\n✓ O email já está cadastrado como '{email}'")
                return True
            
            # Atualizar email
            if USE_MYSQL:
                cur.execute("UPDATE users SET email = %s WHERE username = %s", (email, username))
            else:
                cur.execute("UPDATE users SET email = ? WHERE username = ?", (email, username))
            
            conn.commit()
            print(f"✅ Email atualizado para '{email}'")
            return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  📧 ADICIONAR EMAIL A USUÁRIO")
    print("=" * 60)
    
    username = input("\n👤 Digite o nome de usuário: ").strip()
    if not username:
        print("❌ Nome de usuário é obrigatório")
        sys.exit(1)
    
    email = input("📧 Digite o email: ").strip()
    if not email:
        print("❌ Email é obrigatório")
        sys.exit(1)
    
    # Validar formato de email básico
    if '@' not in email or '.' not in email.split('@')[1]:
        print("❌ Formato de email inválido")
        sys.exit(1)
    
    success = adicionar_email_usuario(username, email)
    
    if success:
        print("\n" + "=" * 60)
        print("  ✅ SUCESSO!")
        print("=" * 60)
        print(f"\n✓ Email '{email}' adicionado/atualizado para usuário '{username}'")
        print(f"\n💡 Agora você pode usar a recuperação de senha com este email!")
    else:
        print("\n" + "=" * 60)
        print("  ❌ FALHA")
        print("=" * 60)
    
    print("\n" + "=" * 60 + "\n")

