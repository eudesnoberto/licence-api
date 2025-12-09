#!/usr/bin/env python3
"""
Script para testar conexão MySQL e criar tabelas
"""

import pymysql
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
env_path = Path("api/.env")
if env_path.exists():
    load_dotenv(env_path)
else:
    # Tentar carregar da raiz
    load_dotenv()

# Configuração MySQL (HostGator)
# ⚠️ IMPORTANTE: Configure via variáveis de ambiente ou edite aqui localmente
# Não commite este arquivo com credenciais reais!
MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

def test_connection():
    """Testa conexão MySQL"""
    print("=" * 60)
    print("🧪 Teste de Conexão MySQL")
    print("=" * 60)
    print()
    
    try:
        print(f"🔌 Conectando a {MYSQL_HOST}:{MYSQL_PORT}...")
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4'
        )
        print("✅ Conexão estabelecida com sucesso!")
        
        # Testar query simples
        cur = conn.cursor()
        cur.execute("SELECT VERSION()")
        version = cur.fetchone()
        print(f"✅ Versão MySQL: {version[0]}")
        
        # Listar tabelas existentes
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        print(f"\n📋 Tabelas existentes: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except pymysql.Error as e:
        print(f"❌ Erro MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

