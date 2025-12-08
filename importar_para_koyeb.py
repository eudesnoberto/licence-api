#!/usr/bin/env python3
"""
Script para importar dados do banco local para o servidor Koyeb
Baseado em importar_para_render.py
"""

import json
import sqlite3
import requests
from pathlib import Path
import sys

# Configuração
LOCAL_DB_PATH = Path("api/license.db")
BACKUP_JSON = "backup_banco_local.json"
KOYEB_API_URL = "https://shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app"

# Credenciais do admin (ajuste se necessário)
# Se não funcionar, o script pedirá as credenciais
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = None  # Será solicitado se necessário

def get_auth_token():
    """Obtém token de autenticação do Koyeb"""
    print(f"🔐 Autenticando no Koyeb ({KOYEB_API_URL})...")
    
    username = ADMIN_USERNAME
    password = ADMIN_PASSWORD
    
    # Se senha não foi configurada, pedir
    if not password:
        print(f"   💡 Usuário padrão: {username}")
        username_input = input(f"   Usuário admin (Enter para '{username}'): ").strip()
        if username_input:
            username = username_input
        
        password = input(f"   Senha admin: ").strip()
        if not password:
            print("   ❌ Senha é obrigatória!")
            return None
    
    try:
        response = requests.post(
            f"{KOYEB_API_URL}/admin/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                print("✅ Autenticação bem-sucedida!")
                return token
            else:
                print("❌ Token não encontrado na resposta")
                return None
        else:
            print(f"❌ Erro na autenticação: {response.status_code}")
            print(f"   Resposta: {response.text}")
            print(f"\n💡 Dicas:")
            print(f"   - Verifique se o usuário e senha estão corretos")
            print(f"   - O servidor pode ter credenciais diferentes do Render")
            return None
    except Exception as e:
        print(f"❌ Erro ao conectar ao Koyeb: {e}")
        return None

def export_local_db():
    """Exporta dados do banco local para JSON"""
    print(f"📤 Exportando banco local ({LOCAL_DB_PATH})...")
    
    if not LOCAL_DB_PATH.exists():
        print(f"❌ Banco local não encontrado: {LOCAL_DB_PATH}")
        return None
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    data = {
        "users": [],
        "devices": []
    }
    
    # Exportar usuários
    cur.execute("SELECT username, password_hash, email, role FROM users")
    for row in cur.fetchall():
        data["users"].append({
            "username": row["username"],
            "password_hash": row["password_hash"],
            "email": row["email"],
            "role": row["role"]
        })
    
    # Exportar devices (licenças)
    cur.execute("""
        SELECT device_id, owner_name, license_type, status, start_date, end_date,
               cpf, address, email, created_by
        FROM devices
    """)
    for row in cur.fetchall():
        data["devices"].append({
            "device_id": row["device_id"],
            "owner_name": row["owner_name"],
            "license_type": row["license_type"],
            "status": row["status"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "cpf": row["cpf"],
            "address": row["address"],
            "email": row["email"],
            "created_by": row["created_by"] or "admin"  # Default para admin se None
        })
    
    conn.close()
    
    print(f"✅ Exportados {len(data['users'])} usuários e {len(data['devices'])} licenças")
    return data

def create_user_on_koyeb(token, user_data):
    """Cria usuário no Koyeb"""
    try:
        response = requests.post(
            f"{KOYEB_API_URL}/admin/users",
            json={
                "username": user_data["username"],
                "password": "TEMPORARY_PASSWORD",  # Precisa ser definido manualmente ou via reset
                "email": user_data.get("email"),
                "role": user_data.get("role", "user")
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return True
        elif response.status_code == 409:
            print(f"   ⚠️  Usuário {user_data['username']} já existe")
            return True  # Considera sucesso se já existe
        else:
            print(f"   ❌ Erro ao criar usuário {user_data['username']}: {response.status_code}")
            print(f"      Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro ao criar usuário {user_data['username']}: {e}")
        return False

def create_license_on_koyeb(token, license_data):
    """Cria licença no Koyeb"""
    try:
        response = requests.post(
            f"{KOYEB_API_URL}/admin/devices",
            json={
                "device_id": license_data["device_id"],
                "owner_name": license_data.get("owner_name"),
                "license_type": license_data["license_type"],
                "status": license_data.get("status", "active"),
                "start_date": license_data["start_date"],
                "end_date": license_data.get("end_date"),
                "cpf": license_data.get("cpf"),
                "address": license_data.get("address"),
                "email": license_data.get("email"),
                "created_by": license_data.get("created_by", "admin")
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return True
        elif response.status_code == 409:
            # Licença já existe, tentar atualizar created_by
            print(f"   ⚠️  Licença {license_data['device_id']} já existe, atualizando created_by...")
            return update_created_by_on_koyeb(token, license_data["device_id"], license_data.get("created_by", "admin"))
        else:
            print(f"   ❌ Erro ao criar licença {license_data['device_id']}: {response.status_code}")
            print(f"      Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro ao criar licença {license_data['device_id']}: {e}")
        return False

def update_created_by_on_koyeb(token, device_id, created_by):
    """Atualiza o campo created_by de uma licença existente"""
    try:
        response = requests.patch(
            f"{KOYEB_API_URL}/admin/devices/{device_id}/update-created-by",
            json={"created_by": created_by},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"      ⚠️  Não foi possível atualizar created_by (status {response.status_code})")
            return False
    except Exception as e:
        print(f"      ⚠️  Erro ao atualizar created_by: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 Importação de Dados para Koyeb")
    print("=" * 60)
    print()
    
    # 1. Autenticar
    token = get_auth_token()
    if not token:
        print("❌ Falha na autenticação. Abortando.")
        sys.exit(1)
    
    # 2. Exportar dados locais
    data = export_local_db()
    if not data:
        print("❌ Falha ao exportar dados locais. Abortando.")
        sys.exit(1)
    
    # 3. Importar usuários
    print()
    print("👥 Importando usuários...")
    users_created = 0
    users_updated = 0
    
    for user in data["users"]:
        if create_user_on_koyeb(token, user):
            users_created += 1
        else:
            users_updated += 1
    
    print(f"✅ Usuários processados: {users_created} criados/atualizados")
    
    # 4. Importar licenças
    print()
    print("📋 Importando licenças...")
    licenses_created = 0
    licenses_updated = 0
    updated_created_by = 0
    
    for license_data in data["devices"]:
        if create_license_on_koyeb(token, license_data):
            licenses_created += 1
        else:
            licenses_updated += 1
    
    print(f"✅ Licenças processadas: {licenses_created} criadas/atualizadas")
    
    # 5. Resumo
    print()
    print("=" * 60)
    print("📊 RESUMO DA IMPORTAÇÃO")
    print("=" * 60)
    print(f"✅ Usuários: {users_created} processados")
    print(f"✅ Licenças: {licenses_created} processadas")
    print()
    print(f"🌐 Servidor Koyeb: {KOYEB_API_URL}")
    print("=" * 60)

if __name__ == "__main__":
    main()

