#!/usr/bin/env python3
"""
Script para criar todas as tabelas no MySQL remoto (HostGator)
"""

import pymysql
import sys
import hashlib

# Configuração MySQL (HostGator)
MYSQL_HOST = "108.179.252.54"
MYSQL_PORT = 3306
MYSQL_DATABASE = "scpmtc84_api"
MYSQL_USER = "scpmtc84_api"
MYSQL_PASSWORD = "nQT-8gW%-qCY"

def _hash_admin_password(raw: str) -> str:
    """Hash simples com sal estático para admin"""
    return hashlib.sha256(f"admin-salt::{raw}".encode("utf-8")).hexdigest()

def main():
    print("=" * 60)
    print("🗄️  Criando Tabelas no MySQL (HostGator)")
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
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ Conectado ao MySQL!")
        print()
        
        cur = conn.cursor()
        
        # Tabela devices
        print("📋 Criando tabela: devices")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(255) NOT NULL UNIQUE,
                owner_name VARCHAR(255),
                license_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'active',
                start_date DATE NOT NULL,
                end_date DATE,
                allow_offline TINYINT NOT NULL DEFAULT 0,
                custom_interval INT,
                features TEXT,
                update_url TEXT,
                update_hash TEXT,
                update_version TEXT,
                notes TEXT,
                last_seen_at DATETIME,
                last_seen_ip VARCHAR(45),
                last_version VARCHAR(50),
                last_hostname VARCHAR(255),
                cpf VARCHAR(20),
                address TEXT,
                email VARCHAR(255),
                created_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_device_id (device_id),
                INDEX idx_status (status),
                INDEX idx_created_by (created_by)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✅ Tabela devices criada")
        
        # Tabela blocked_devices
        print("📋 Criando tabela: blocked_devices")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS blocked_devices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(255) NOT NULL UNIQUE,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_device_id (device_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✅ Tabela blocked_devices criada")
        
        # Tabela access_logs
        print("📋 Criando tabela: access_logs")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(255) NOT NULL,
                ip VARCHAR(45) NOT NULL,
                user_agent TEXT,
                hostname VARCHAR(255),
                client_version VARCHAR(50),
                telemetry_json TEXT,
                allowed TINYINT NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_device_id (device_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✅ Tabela access_logs criada")
        
        # Tabela license_history
        print("📋 Criando tabela: license_history")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS license_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(255) NOT NULL,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                admin VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_device_id (device_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✅ Tabela license_history criada")
        
        # Tabela admin_users
        print("📋 Criando tabela: admin_users")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                must_change_password TINYINT NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✅ Tabela admin_users criada")
        
        # Tabela users
        print("📋 Criando tabela: users")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                role VARCHAR(50) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✅ Tabela users criada")
        
        # Tabela password_resets
        print("📋 Criando tabela: password_resets")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                token VARCHAR(255) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_token (token),
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("   ✅ Tabela password_resets criada")
        
        # Verificar se admin padrão existe
        print()
        print("👤 Verificando usuário admin padrão...")
        cur.execute("SELECT COUNT(1) as count FROM admin_users")
        result = cur.fetchone()
        count = result['count'] if result and isinstance(result, dict) else (result[0] if result else 0)
        
        if count == 0:
            print("   ➕ Criando usuário admin padrão (admin/admin123)...")
            cur.execute(
                "INSERT INTO admin_users (username, password_hash, must_change_password) VALUES (%s, %s, 1)",
                ("admin", _hash_admin_password("admin123")),
            )
            print("   ✅ Usuário admin criado")
        else:
            print(f"   ℹ️  Já existem {count} usuário(s) admin")
        
        conn.commit()
        
        # Listar tabelas criadas
        print()
        print("📊 Tabelas criadas:")
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        for table in tables:
            table_name = table[0] if isinstance(table, (list, tuple)) else list(table.values())[0]
            print(f"   ✅ {table_name}")
        
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ Todas as tabelas foram criadas com sucesso!")
        print("=" * 60)
        
    except pymysql.Error as e:
        print(f"❌ Erro MySQL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

