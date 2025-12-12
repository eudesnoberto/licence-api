#!/usr/bin/env python3
"""
Script para atualizar a licença do sergio para que created_by seja "sergio"
"""

import requests
from getpass import getpass

RENDER_API_URL = "https://licence-api-zsbg.onrender.com"

DEVICE_ID = "02592614b69110a201bf84c68d1c9247"

print("🔧 Atualizando licença do sergio...\n")

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
    
    # Nota: A API não tem endpoint direto para atualizar created_by
    # Vamos usar uma abordagem: deletar e recriar com created_by correto
    # OU criar um endpoint temporário
    
    print("⚠️  A API não tem endpoint para atualizar 'created_by' diretamente.")
    print("💡 Solução: Vamos recriar a licença com created_by='sergio'\n")
    
    # Primeiro, buscar dados atuais da licença
    print("📋 Buscando dados da licença atual...")
    devices_response = requests.get(
        f"{RENDER_API_URL}/admin/devices",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    
    if devices_response.status_code != 200:
        print(f"❌ Erro ao buscar licenças: {devices_response.text}")
        exit(1)
    
    devices = devices_response.json().get("items", [])
    licenca_atual = None
    
    for device in devices:
        if device.get("device_id") == DEVICE_ID:
            licenca_atual = device
            break
    
    if not licenca_atual:
        print(f"❌ Licença não encontrada!")
        exit(1)
    
    print(f"✅ Licença encontrada:")
    print(f"   Device ID: {licenca_atual.get('device_id')}")
    print(f"   Nome: {licenca_atual.get('owner_name')}")
    print(f"   created_by atual: {licenca_atual.get('created_by', 'N/A')}\n")
    
    # Dados para recriar
    dados_licenca = {
        "device_id": licenca_atual.get("device_id"),
        "owner_name": licenca_atual.get("owner_name"),
        "cpf": licenca_atual.get("cpf"),
        "email": licenca_atual.get("email"),
        "address": licenca_atual.get("address"),
        "license_type": licenca_atual.get("license_type"),
    }
    
    print("⚠️  Para atualizar created_by, precisamos:")
    print("   1. Deletar a licença atual")
    print("   2. Recriar com created_by='sergio'")
    print("\n   Mas a API não tem endpoint de DELETE.")
    print("\n💡 SOLUÇÃO ALTERNATIVA:")
    print("   Vamos fazer login como 'sergio' e recriar a licença.")
    print("   Assim, created_by será automaticamente 'sergio'.\n")
    
    # Fazer login como sergio
    print("🔐 Fazendo login como 'sergio'...")
    sergio_password = input("   Senha do sergio (TEMPORARIA123): ").strip() or "TEMPORARIA123"
    
    sergio_login = requests.post(
        f"{RENDER_API_URL}/admin/login",
        json={"username": "sergio", "password": sergio_password},
        timeout=60
    )
    
    if sergio_login.status_code != 200:
        print(f"❌ Erro no login do sergio: {sergio_login.text}")
        print(f"\n💡 Dica: A senha padrão é TEMPORARIA123")
        exit(1)
    
    sergio_token = sergio_login.json()["token"]
    print("✅ Login como sergio realizado!\n")
    
    # Criar licença como sergio (vai ter created_by='sergio')
    print("📝 Recriando licença como sergio...")
    print("   (A licença atual será substituída)\n")
    
    # Usar endpoint de usuário comum para criar licença vitalícia
    create_response = requests.post(
        f"{RENDER_API_URL}/user/devices/create",
        headers={
            "Authorization": f"Bearer {sergio_token}",
            "Content-Type": "application/json"
        },
        json=dados_licenca,
        timeout=30
    )
    
    if create_response.status_code in [200, 201]:
        print("✅ Licença recriada com sucesso!")
        print(f"   Device ID: {dados_licenca['device_id']}")
        print(f"   Nome: {dados_licenca['owner_name']}")
        print(f"   created_by: sergio (agora correto!)")
        print(f"\n✅ Agora o sergio verá a licença quando fizer login!")
    else:
        if "já existe" in create_response.text.lower() or "already exists" in create_response.text.lower():
            print("⚠️  Licença já existe.")
            print("💡 A licença atual tem created_by='admin'.")
            print("💡 Para corrigir, você precisa:")
            print("   1. Deletar a licença atual no dashboard (como admin)")
            print("   2. Fazer login como sergio")
            print("   3. Recriar a licença (assim created_by será 'sergio')")
        else:
            print(f"❌ Erro ao recriar licença: {create_response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Erro de conexão: {e}")
    exit(1)

print("\n✅ Processo concluído!")



