#!/usr/bin/env python3
"""
Script para corrigir o created_by da licença do sergio
"""

import requests
from getpass import getpass

RENDER_API_URL = "https://licence-api-zsbg.onrender.com"

DEVICE_ID = "02592614b69110a201bf84c68d1c9247"

print("🔧 Corrigindo created_by da licença do sergio...\n")

# Login como admin
print("🔐 Fazendo login como admin...")
username = input("   Usuário admin (Enter para 'admin'): ").strip() or "admin"
password = getpass("   Senha admin (Enter para usar padrão): ").strip() or "Stage.7997"

try:
    login_response = requests.post(
        f"{RENDER_API_URL}/admin/login",
        json={"username": username, "password": password},
        timeout=60
    )
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.text}")
        exit(1)
    
    token = login_response.json()["token"]
    print("✅ Login realizado com sucesso!\n")
    
    # Atualizar created_by
    print("📝 Atualizando created_by para 'sergio'...")
    
    update_response = requests.post(
        f"{RENDER_API_URL}/admin/devices/update-created-by",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "device_id": DEVICE_ID,
            "created_by": "sergio"
        },
        timeout=30
    )
    
    if update_response.status_code == 200:
        print("✅ created_by atualizado com sucesso!")
        print(f"   Device ID: {DEVICE_ID}")
        print(f"   created_by: sergio")
        print(f"\n✅ Agora o sergio verá a licença quando fizer login!")
    elif update_response.status_code == 404:
        print("❌ Endpoint não encontrado. O código precisa ser atualizado no Render.")
        print("\n💡 SOLUÇÃO:")
        print("   1. Faça commit e push do código atualizado para GitHub")
        print("   2. O Render vai fazer deploy automaticamente")
        print("   3. Execute este script novamente")
    else:
        print(f"❌ Erro ao atualizar: {update_response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Erro de conexão: {e}")
    exit(1)

print("\n✅ Processo concluído!")



