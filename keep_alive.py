#!/usr/bin/env python3
"""
Script de Keep-Alive para manter servidor Render ativo
Executa este script em um PC que fica sempre ligado para fazer ping periódico
"""

import requests
import time
from datetime import datetime
import sys

# Configuração
API_URLS = [
    "https://licence-api-zsbg.onrender.com/ping",
    "https://api.fartgreen.fun/ping",  # Se tiver outro servidor
]

INTERVAL = 300  # 5 minutos (300 segundos)
TIMEOUT = 30   # Timeout de 30 segundos

def ping_server(url: str) -> bool:
    """Faz ping no servidor e retorna True se sucesso"""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {url} - {data.get('message', 'OK')}")
            return True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  {url} - Status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏱️  {url} - Timeout (servidor pode estar 'dormindo')")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ {url} - Erro: {e}")
        return False

def main():
    """Loop principal de keep-alive"""
    print("=" * 60)
    print("🔄 Keep-Alive para Servidores Render")
    print("=" * 60)
    print(f"📡 Servidores: {', '.join(API_URLS)}")
    print(f"⏰ Intervalo: {INTERVAL} segundos ({INTERVAL // 60} minutos)")
    print(f"🛑 Pressione Ctrl+C para parar")
    print("=" * 60)
    print()
    
    try:
        while True:
            for url in API_URLS:
                ping_server(url)
                time.sleep(2)  # Pequeno delay entre servidores
            
            print(f"⏳ Aguardando {INTERVAL} segundos até próximo ping...\n")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Keep-alive interrompido pelo usuário")
        sys.exit(0)

if __name__ == "__main__":
    main()

