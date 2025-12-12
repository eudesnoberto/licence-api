#!/usr/bin/env python3
"""
Script simples para testar login no Render
"""

import requests

RENDER_API_URL = "https://licence-api-zsbg.onrender.com"

print("🔍 Testando conexão com Render...")
print(f"URL: {RENDER_API_URL}\n")

# Teste 1: Health check
print("1️⃣  Testando /health...")
try:
    r = requests.get(f"{RENDER_API_URL}/health", timeout=15)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 2: Login com credenciais padrão
print("\n2️⃣  Testando login (admin/admin123)...")
try:
    r = requests.post(
        f"{RENDER_API_URL}/admin/login",
        json={"username": "admin", "password": "admin123"},
        timeout=30
    )
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:200]}...")
    
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ Login OK! Token recebido: {data.get('token', '')[:50]}...")
    else:
        print(f"   ❌ Login falhou")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n✅ Teste concluído!")



