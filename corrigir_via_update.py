#!/usr/bin/env python3
"""
Script para corrigir created_by via endpoint de update existente
"""

import requests
from getpass import getpass

RENDER_API_URL = "https://licence-api-zsbg.onrender.com"

DEVICE_ID = "02592614b69110a201bf84c68d1c9247"

print("🔧 Corrigindo created_by da licença do sergio...\n")

# Login como admin
print("🔐 Fazendo login como admin...")
username = "admin"
password = "Stage.7997"
print(f"   Usuário: {username}")
print(f"   Senha: {'*' * len(password)}")

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
    
    # Buscar dados atuais
    print("📋 Buscando dados da licença...")
    devices_response = requests.get(
        f"{RENDER_API_URL}/admin/devices",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    
    if devices_response.status_code != 200:
        print(f"❌ Erro ao buscar licenças: {devices_response.text}")
        exit(1)
    
    devices = devices_response.json().get("items", [])
    licenca = None
    
    for device in devices:
        if device.get("device_id") == DEVICE_ID:
            licenca = device
            break
    
    if not licenca:
        print(f"❌ Licença não encontrada!")
        exit(1)
    
    print(f"✅ Licença encontrada:")
    print(f"   Device ID: {licenca.get('device_id')}")
    print(f"   Nome: {licenca.get('owner_name')}")
    print(f"   created_by atual: {licenca.get('created_by', 'N/A')}\n")
    
    # Atualizar incluindo created_by
    print("📝 Atualizando licença com created_by='sergio'...")
    
    update_data = {
        "device_id": DEVICE_ID,
        "owner_name": licenca.get("owner_name"),
        "cpf": licenca.get("cpf"),
        "email": licenca.get("email"),
        "address": licenca.get("address"),
        "license_type": licenca.get("license_type"),
        "created_by": "sergio"  # Adicionar created_by na atualização
    }
    
    update_response = requests.post(
        f"{RENDER_API_URL}/admin/devices/create",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=update_data,
        timeout=30
    )
    
    if update_response.status_code in [200, 201]:
        print("✅ Licença atualizada com sucesso!")
        print(f"   Device ID: {DEVICE_ID}")
        print(f"   created_by: sergio")
        print(f"\n✅ Agora o sergio verá a licença quando fizer login!")
    else:
        print(f"❌ Erro ao atualizar: {update_response.text}")
        print(f"\n💡 Se o erro for sobre created_by não ser aceito,")
        print(f"   aguarde o deploy do código atualizado no Render.")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Erro de conexão: {e}")
    exit(1)

print("\n✅ Processo concluído!")

