#!/usr/bin/env python3
"""
Script para verificar se um email está cadastrado no banco de dados.
Execute: python verificar_email_usuario.py
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('api/.env')

# Importar módulos do sistema
sys.path.insert(0, 'api')
from db import get_conn, get_cursor, USE_MYSQL

def verificar_email(email: str):
    """Verifica se um email está cadastrado no banco."""
    
    print("\n" + "=" * 60)
    print(f"  🔍 Verificando Email: {email}")
    print("=" * 60)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        
        # Verificar na tabela users
        if USE_MYSQL:
            cur.execute("SELECT id, username, email, role FROM users WHERE email = %s LIMIT 1", (email,))
        else:
            cur.execute("SELECT id, username, email, role FROM users WHERE email = ? LIMIT 1", (email,))
        
        row = cur.fetchone()
        
        if row:
            if USE_MYSQL:
                user_id, username, user_email, role = row['id'], row['username'], row['email'], row['role']
            else:
                user_id, username, user_email, role = row[0], row[1], row[2], row[3]
            
            print(f"\n✅ Email encontrado na tabela 'users':")
            print(f"   ID: {user_id}")
            print(f"   Usuário: {username}")
            print(f"   Email: {user_email}")
            print(f"   Função: {role}")
            return True
        else:
            print(f"\n❌ Email NÃO encontrado na tabela 'users'")
            print(f"\n💡 O email precisa estar cadastrado na tabela 'users' para recuperação de senha.")
            print(f"   Verifique se o usuário tem email cadastrado no perfil.")
            return False

def listar_usuarios():
    """Lista todos os usuários cadastrados."""
    
    print("\n" + "=" * 60)
    print("  📋 Usuários Cadastrados")
    print("=" * 60)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        
        if USE_MYSQL:
            cur.execute("SELECT id, username, email, role FROM users ORDER BY id")
        else:
            cur.execute("SELECT id, username, email, role FROM users ORDER BY id")
        
        rows = cur.fetchall()
        
        if not rows:
            print("\n⚠️  Nenhum usuário encontrado na tabela 'users'")
            return
        
        print(f"\n📊 Total de usuários: {len(rows)}\n")
        
        for row in rows:
            if USE_MYSQL:
                user_id, username, email, role = row['id'], row['username'], row['email'], row['role']
            else:
                user_id, username, email, role = row[0], row[1], row[2], row[3]
            
            email_status = email if email else "❌ SEM EMAIL"
            print(f"   [{user_id}] {username} ({role}) - {email_status}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🔍 VERIFICAÇÃO DE EMAIL NO BANCO DE DADOS")
    print("=" * 60)
    
    # Listar todos os usuários
    listar_usuarios()
    
    # Solicitar email para verificar
    print("\n" + "-" * 60)
    email = input("\n📧 Digite o email para verificar (ou Enter para sair): ").strip()
    
    if email:
        verificar_email(email)
        
        print("\n" + "=" * 60)
        print("  💡 Dicas")
        print("=" * 60)
        print("\n1. O email precisa estar cadastrado na tabela 'users'")
        print("2. Para adicionar email a um usuário:")
        print("   - Acesse o dashboard como admin")
        print("   - Vá em 'Meu Perfil' ou 'Gerenciar Usuários'")
        print("   - Adicione/atualize o email do usuário")
        print("3. Verifique os logs do servidor ao solicitar recuperação")
        print("4. Verifique a pasta de Spam/Lixo Eletrônico")
    
    print("\n" + "=" * 60 + "\n")

