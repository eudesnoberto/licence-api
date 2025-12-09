#!/usr/bin/env python3
"""
Script para migrar dados do SQLite local para MySQL no HostGator
"""

import sqlite3
import pymysql
import sys
from pathlib import Path
from datetime import datetime

# Configuração SQLite (local)
SQLITE_DB = Path("api/license.db")

# Configuração MySQL (HostGator)
# ⚠️ IMPORTANTE: Configure via variáveis de ambiente ou edite aqui localmente
# Não commite este arquivo com credenciais reais!
import os
MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

def migrate_table(sqlite_conn, mysql_conn, table_name, columns_map=None):
    """Migra uma tabela do SQLite para MySQL"""
    print(f"\n📋 Migrando tabela: {table_name}")
    
    sqlite_cur = sqlite_conn.cursor()
    mysql_cur = mysql_conn.cursor()
    
    # Buscar dados do SQLite
    sqlite_cur.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cur.fetchall()
    
    if not rows:
        print(f"   ℹ️  Tabela {table_name} está vazia")
        return 0
    
    # Obter nomes das colunas
    sqlite_cur.execute(f"PRAGMA table_info({table_name})")
    sqlite_columns = [row[1] for row in sqlite_cur.fetchall()]
    
    # Mapear colunas se necessário
    if columns_map:
        mysql_columns = [columns_map.get(col, col) for col in sqlite_columns]
    else:
        mysql_columns = sqlite_columns
    
    # Preparar query de inserção
    placeholders = ', '.join(['%s'] * len(mysql_columns))
    columns_str = ', '.join([f"`{col}`" for col in mysql_columns])
    insert_query = f"INSERT IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    inserted = 0
    for row in rows:
        try:
            # Converter valores
            values = []
            for i, val in enumerate(row):
                if val is None:
                    values.append(None)
                elif isinstance(val, str) and val.startswith('datetime('):
                    # Ignorar funções SQLite
                    values.append(None)
                else:
                    values.append(val)
            
            mysql_cur.execute(insert_query, values)
            inserted += 1
        except Exception as e:
            print(f"   ⚠️  Erro ao inserir linha: {e}")
            continue
    
    mysql_conn.commit()
    print(f"   ✅ {inserted}/{len(rows)} registros migrados")
    return inserted

def main():
    print("=" * 60)
    print("🚀 Migração SQLite → MySQL (HostGator)")
    print("=" * 60)
    
    # Verificar SQLite
    if not SQLITE_DB.exists():
        print(f"❌ Banco SQLite não encontrado: {SQLITE_DB}")
        sys.exit(1)
    
    print(f"\n📂 Banco SQLite: {SQLITE_DB}")
    
    # Conectar SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        print("✅ Conectado ao SQLite")
    except Exception as e:
        print(f"❌ Erro ao conectar SQLite: {e}")
        sys.exit(1)
    
    # Conectar MySQL
    try:
        mysql_conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4'
        )
        print("✅ Conectado ao MySQL (HostGator)")
    except Exception as e:
        print(f"❌ Erro ao conectar MySQL: {e}")
        print(f"   Verifique se o banco {MYSQL_DATABASE} existe e as credenciais estão corretas")
        sys.exit(1)
    
    # Lista de tabelas para migrar
    tables = [
        "admin_users",
        "users",
        "devices",
        "blocked_devices",
        "access_logs",
        "license_history"
    ]
    
    total_migrated = 0
    
    try:
        for table in tables:
            # Verificar se tabela existe no SQLite
            sqlite_cur = sqlite_conn.cursor()
            sqlite_cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not sqlite_cur.fetchone():
                print(f"\n⚠️  Tabela {table} não existe no SQLite, pulando...")
                continue
            
            migrated = migrate_table(sqlite_conn, mysql_conn, table)
            total_migrated += migrated
        
        print("\n" + "=" * 60)
        print("✅ Migração concluída!")
        print(f"📊 Total de registros migrados: {total_migrated}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        mysql_conn.rollback()
        sys.exit(1)
    finally:
        sqlite_conn.close()
        mysql_conn.close()
        print("\n🔌 Conexões fechadas")

if __name__ == "__main__":
    main()

