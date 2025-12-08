#!/usr/bin/env python3
"""
Script para importar dados do backup local para o servidor Render
Importa via API REST do servidor
"""

import json
import sys
import requests
from pathlib import Path
from getpass import getpass

# Configuração do servidor Render
RENDER_API_URL = "https://licence-api-zsbg.onrender.com"

def import_to_render():
    """Importa dados do backup para o Render via API"""
    
    # Carregar backup
    backup_file = Path(__file__).parent / "backup_banco_local.json"
    
    if not backup_file.exists():
        print(f"❌ Arquivo de backup não encontrado: {backup_file}")
        print("   Execute primeiro: python exportar_banco_local.py")
        sys.exit(1)
    
    print(f"📂 Carregando backup: {backup_file}")
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    # Verificar se servidor está online
    print(f"\n🔍 Verificando servidor Render...")
    print(f"   URL: {RENDER_API_URL}")
    
    try:
        health_response = requests.get(f"{RENDER_API_URL}/health", timeout=15)
        if health_response.status_code == 200:
            print("✅ Servidor está online!")
        else:
            print(f"⚠️  Servidor respondeu com status {health_response.status_code}")
    except requests.exceptions.Timeout:
        print("⚠️  Servidor pode estar 'dormindo' (plano gratuito do Render)")
        print("   Aguardando 30 segundos para servidor acordar...")
        import time
        time.sleep(30)
        print("   Tentando novamente...")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Erro ao verificar servidor: {e}")
        print("   Continuando mesmo assim...")
    
    # Login no Render
    print(f"\n🔐 Fazendo login no Render...")
    print(f"   💡 Usuário padrão: admin")
    
    username = input("\n   Usuário admin (Enter para 'admin'): ").strip() or "admin"
    
    # Tentar usar getpass, mas se falhar, usar input normal
    try:
        password = getpass("   Senha admin (Enter para usar senha padrão): ").strip()
    except Exception:
        # Fallback se getpass não funcionar
        password = input("   Senha admin (Enter para usar senha padrão): ").strip()
    
    if not password:
        # Usar senha padrão do Render
        password = "Stage.7997"
        print("   ✓ Usando senha padrão do Render")
    else:
        print(f"   ✓ Senha digitada (oculta)")
    
    try:
        # Fazer login com timeout maior (Render pode estar "dormindo")
        print("   ⏳ Conectando... (pode demorar se servidor estiver 'dormindo')")
        login_response = requests.post(
            f"{RENDER_API_URL}/admin/login",
            json={"username": username, "password": password},
            timeout=60  # Timeout maior para Render "dormindo"
        )
        
        if login_response.status_code != 200:
            error_text = login_response.text
            print(f"\n❌ Erro no login: {error_text}")
            print(f"\n💡 Dicas:")
            print(f"   - Verifique se o usuário e senha estão corretos")
            print(f"   - No Render, o padrão é: admin / admin123")
            print(f"   - Se você alterou a senha, use a senha atual")
            print(f"   - O servidor pode estar 'dormindo' (plano gratuito)")
            print(f"   - Tente acessar o dashboard primeiro: https://fartgreen.fun/#dashboard")
            sys.exit(1)
        
        token = login_response.json()["token"]
        print("✅ Login realizado com sucesso!")
        
        # Importar admin_users (exceto o padrão admin/admin123)
        print(f"\n📥 Importando Admin Users...")
        admin_users = backup_data.get("admin_users", [])
        imported_admins = 0
        
        for admin in admin_users:
            # Pular o admin padrão (já existe no Render)
            if admin["username"] == "admin":
                print(f"   ⏭️  Pulando admin padrão (já existe)")
                continue
            
            # Nota: A API não tem endpoint para criar admin_users diretamente
            # Você precisará criar manualmente ou usar SQL direto
            print(f"   ⚠️  Admin '{admin['username']}' precisa ser criado manualmente")
        
        # Importar users (usuários comuns)
        print(f"\n📥 Importando Usuários Comuns...")
        users = backup_data.get("users", [])
        imported_users = 0
        
        if not users:
            print("   ℹ️  Nenhum usuário para importar")
            use_temp_all = True  # Valor padrão
        else:
            print(f"   📊 Total de usuários: {len(users)}")
            # Perguntar uma vez para todos
            use_temp_all = input(f"\n   💡 Usar senha temporária 'TEMPORARIA123' para TODOS os usuários? (S/n): ").strip().lower()
            use_temp_all = use_temp_all != 'n'  # Padrão: sim
        
        for user in users:
            try:
                if use_temp_all:
                    password = "TEMPORARIA123"
                else:
                    password = input(f"   📝 Digite a senha para '{user['username']}' (ou Enter para pular): ").strip()
                    if not password:
                        print(f"      ⏭️  Pulando usuário")
                        continue
                
                response = requests.post(
                    f"{RENDER_API_URL}/admin/users/create",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "username": user["username"],
                        "password": password,
                        "email": user.get("email"),
                        "role": user.get("role", "user")
                    },
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ Usuário '{user['username']}' criado")
                    imported_users += 1
                elif response.status_code == 409:
                    print(f"   ⏭️  Usuário '{user['username']}' já existe")
                else:
                    print(f"   ❌ Erro ao criar '{user['username']}': {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Erro ao criar '{user['username']}': {e}")
        
        # Importar devices (licenças)
        print(f"\n📥 Importando Licenças...")
        devices = backup_data.get("devices", [])
        imported_devices = 0
        updated_created_by = 0
        
        for device in devices:
            try:
                # Obter created_by do backup
                created_by = device.get("created_by")
                
                # Se created_by for None ou vazio, definir como 'admin' (para admin ver todas)
                if not created_by:
                    created_by = "admin"
                    print(f"   ℹ️  Licença sem created_by - será atribuída ao admin")
                
                # Preparar dados da licença
                device_data = {
                    "device_id": device["device_id"],
                    "license_type": device["license_type"],
                    "owner_name": device.get("owner_name"),
                    "cpf": device.get("cpf"),
                    "email": device.get("email"),
                    "address": device.get("address"),
                    "created_by": created_by  # IMPORTANTE: Preservar created_by
                }
                
                # Usar endpoint de admin para criar licença
                response = requests.post(
                    f"{RENDER_API_URL}/admin/devices/create",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json=device_data,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    created_by_info = f" (criada por: {created_by})" if created_by else ""
                    print(f"   ✅ Licença para '{device['device_id'][:20]}...' criada{created_by_info}")
                    imported_devices += 1
                elif response.status_code == 400:
                    # Verificar se é erro de "já registrado"
                    error_text = response.text.lower()
                    if "já registrado" in error_text or "already registered" in error_text or "já existe" in error_text:
                        # Licença já existe - tentar atualizar created_by
                        print(f"   ⏭️  Licença '{device['device_id'][:20]}...' já existe - atualizando 'created_by'...")
                        
                        # Tentar atualizar created_by usando endpoint específico
                        try:
                            update_response = requests.post(
                                f"{RENDER_API_URL}/admin/devices/update-created-by",
                                headers={
                                    "Authorization": f"Bearer {token}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "device_id": device["device_id"],
                                    "created_by": created_by
                                },
                                timeout=30
                            )
                            
                            if update_response.status_code == 200:
                                print(f"      ✅ Campo 'created_by' atualizado para '{created_by}'")
                                updated_created_by += 1
                                imported_devices += 1  # Contar como importada
                            else:
                                print(f"      ⚠️  Não foi possível atualizar 'created_by': {update_response.text}")
                                # Tentar atualizar via endpoint de criação (que atualiza se existir)
                                print(f"      🔄 Tentando atualizar via endpoint de criação...")
                                device_data["created_by"] = created_by
                                retry_response = requests.post(
                                    f"{RENDER_API_URL}/admin/devices/create",
                                    headers={
                                        "Authorization": f"Bearer {token}",
                                        "Content-Type": "application/json"
                                    },
                                    json=device_data,
                                    timeout=30
                                )
                                if retry_response.status_code in [200, 201]:
                                    print(f"      ✅ Licença atualizada com sucesso!")
                                    updated_created_by += 1
                                    imported_devices += 1
                                else:
                                    print(f"      ❌ Erro ao atualizar: {retry_response.text}")
                        except Exception as e:
                            print(f"      ⚠️  Erro ao atualizar 'created_by': {e}")
                    else:
                        print(f"   ❌ Erro ao criar licença '{device['device_id'][:20]}...': {response.text}")
                elif response.status_code == 409:
                    # Licença já existe - tentar atualizar created_by
                    print(f"   ⏭️  Licença '{device['device_id'][:20]}...' já existe - atualizando 'created_by'...")
                    
                    # Tentar atualizar created_by usando endpoint específico
                    try:
                        update_response = requests.post(
                            f"{RENDER_API_URL}/admin/devices/update-created-by",
                            headers={
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "device_id": device["device_id"],
                                "created_by": created_by
                            },
                            timeout=30
                        )
                        
                        if update_response.status_code == 200:
                            print(f"      ✅ Campo 'created_by' atualizado para '{created_by}'")
                            updated_created_by += 1
                            imported_devices += 1  # Contar como importada
                        else:
                            print(f"      ⚠️  Não foi possível atualizar 'created_by': {update_response.text}")
                    except Exception as e:
                        print(f"      ⚠️  Erro ao atualizar 'created_by': {e}")
                else:
                    print(f"   ❌ Erro ao criar licença '{device['device_id'][:20]}...': {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Erro ao criar licença: {e}")
        
        # Importar blocked_devices
        print(f"\n📥 Importando Dispositivos Bloqueados...")
        blocked = backup_data.get("blocked_devices", [])
        imported_blocked = 0
        
        for blocked_device in blocked:
            try:
                # Nota: A API pode não ter endpoint para bloquear diretamente
                # Você pode precisar fazer isso manualmente no dashboard
                print(f"   ⚠️  Dispositivo bloqueado '{blocked_device['device_id']}' precisa ser bloqueado manualmente")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        # Resumo
        print(f"\n{'='*60}")
        print(f"✅ Importação concluída!")
        print(f"\n📊 Resumo:")
        print(f"   - Usuários Comuns: {imported_users}/{len(users)}")
        print(f"   - Licenças: {imported_devices}/{len(devices)}")
        print(f"   - Licenças com 'created_by' atualizado: {updated_created_by}")
        print(f"\n📋 Permissões:")
        print(f"   - Admin verá TODAS as licenças (created_by = 'admin' ou null)")
        print(f"   - Usuários comuns verão apenas licenças com created_by = seu username")
        print(f"\n⚠️  Notas:")
        print(f"   - Admin users precisam ser criados manualmente")
        print(f"   - Dispositivos bloqueados precisam ser bloqueados manualmente")
        print(f"   - Usuários criados têm senha temporária: TEMPORARIA123")
        print(f"   - Peça para os usuários alterarem a senha no primeiro acesso")
        print(f"   - Licenças sem 'created_by' foram atribuídas ao 'admin'")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        print(f"   Verifique se o servidor Render está online: {RENDER_API_URL}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Importação cancelada pelo usuário")
        sys.exit(1)

if __name__ == "__main__":
    import_to_render()

