#!/usr/bin/env python3
"""
Script para verificar e garantir que a licença do usuário sergio está no Render
"""

import requests
import json
from getpass import getpass

RENDER_API_URL = "https://licence-api-zsbg.onrender.com"

# Dados da licença do sergio do backup
LICENCA_SERGIO = {
    "device_id": "02592614b69110a201bf84c68d1c9247",
    "owner_name": "Sergio Lucindo Santos",
    "cpf": "30403459826",
    "email": "sergiolsl21@hotmail.com",
    "address": "Rua, 26 das Rosas - Montanhão - São Bernardo do Campo/SP - CEP 09784-165 - casa",
    "license_type": "vitalicia"
}

print("🔍 Verificando licença do usuário sergio no Render...\n")

# Login
print("🔐 Fazendo login...")
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
    
    # Verificar se licença já existe
    print("📋 Verificando se licença já existe...")
    devices_response = requests.get(
        f"{RENDER_API_URL}/admin/devices",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    
    if devices_response.status_code == 200:
        devices = devices_response.json().get("items", [])
        device_id = LICENCA_SERGIO["device_id"]
        
        # Procurar licença
        licenca_existe = False
        for device in devices:
            if device.get("device_id") == device_id:
                licenca_existe = True
                print(f"✅ Licença encontrada!")
                print(f"   Device ID: {device.get('device_id')}")
                print(f"   Nome: {device.get('owner_name')}")
                print(f"   Tipo: {device.get('license_type')}")
                print(f"   Status: {device.get('status')}")
                print(f"   Email: {device.get('email')}")
                break
        
        if not licenca_existe:
            print(f"⚠️  Licença NÃO encontrada. Criando...\n")
            
            # Criar licença
            create_response = requests.post(
                f"{RENDER_API_URL}/admin/devices/create",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=LICENCA_SERGIO,
                timeout=30
            )
            
            if create_response.status_code in [200, 201]:
                print(f"✅ Licença criada com sucesso!")
                print(f"   Device ID: {LICENCA_SERGIO['device_id']}")
                print(f"   Nome: {LICENCA_SERGIO['owner_name']}")
                print(f"   Tipo: {LICENCA_SERGIO['license_type']}")
                print(f"   Email: {LICENCA_SERGIO['email']}")
            else:
                print(f"❌ Erro ao criar licença: {create_response.text}")
        else:
            print(f"\n✅ Licença do sergio já está no Render!")
    
    else:
        print(f"❌ Erro ao buscar licenças: {devices_response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Erro de conexão: {e}")
    exit(1)

print("\n✅ Verificação concluída!")



