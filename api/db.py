from contextlib import contextmanager
import hashlib
import sqlite3
from pathlib import Path
import os

import config

# Suporte a MySQL
DB_TYPE = getattr(config, "DB_TYPE", "sqlite").lower()
USE_MYSQL = DB_TYPE == "mysql"

if USE_MYSQL:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()  # Compatibilidade com MySQLdb
        MYSQL_AVAILABLE = True
    except ImportError:
        MYSQL_AVAILABLE = False
        print("⚠️  pymysql não instalado. Instale com: pip install pymysql")
else:
    MYSQL_AVAILABLE = False

DB_PATH = Path(config.DB_PATH) if not USE_MYSQL else None


def _hash_admin_password(raw: str) -> str:
    # Hash simples com sal estático para admin (pode ser trocado depois)
    return hashlib.sha256(f"admin-salt::{raw}".encode("utf-8")).hexdigest()


def _get_mysql_connection():
    """Cria conexão MySQL"""
    if not MYSQL_AVAILABLE:
        raise ImportError("pymysql não está instalado. Execute: pip install pymysql")
    
    return pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )


def _execute_mysql_query(conn, query: str, params=None):
    """Executa query MySQL com tratamento de erros"""
    cur = conn.cursor()
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur
    except Exception as e:
        conn.rollback()
        raise


def init_db() -> None:
    """Cria as tabelas básicas em SQLite ou MySQL, se ainda não existirem."""
    
    if USE_MYSQL:
        if not MYSQL_AVAILABLE:
            raise ImportError("MySQL configurado mas pymysql não está instalado. Execute: pip install pymysql")
        
        conn = _get_mysql_connection()
        cur = conn.cursor()
        
        try:
            # Tabela devices
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
            
            # Verificar e adicionar colunas se não existirem
            cur.execute("SHOW COLUMNS FROM devices LIKE 'cpf'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE devices ADD COLUMN cpf VARCHAR(20)")
            
            cur.execute("SHOW COLUMNS FROM devices LIKE 'address'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE devices ADD COLUMN address TEXT")
            
            cur.execute("SHOW COLUMNS FROM devices LIKE 'email'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE devices ADD COLUMN email VARCHAR(255)")
            
            cur.execute("SHOW COLUMNS FROM devices LIKE 'created_by'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE devices ADD COLUMN created_by VARCHAR(100)")
            
            # Tabela blocked_devices
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blocked_devices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL UNIQUE,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_device_id (device_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela access_logs
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
            
            # Tabela license_history
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
            
            # Tabela de usuários admin do painel
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
            
            # Tabela de usuários/revendedores
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
            
            # Usuário admin padrão (admin / admin123) se não existir nenhum usuário
            cur.execute("SELECT COUNT(1) as count FROM admin_users")
            result = cur.fetchone()
            count = result['count'] if result else 0
            
            if count == 0:
                default_user = getattr(config, "ADMIN_DEFAULT_USER", "admin")
                default_pass = getattr(config, "ADMIN_DEFAULT_PASSWORD", "admin123")
                cur.execute(
                    "INSERT INTO admin_users (username, password_hash, must_change_password) VALUES (%s, %s, 1)",
                    (default_user, _hash_admin_password(default_pass)),
                )
            
            conn.commit()
        finally:
            conn.close()
    else:
        # SQLite (código original)
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            
            # Tabela devices
            cur.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL UNIQUE,
                    owner_name TEXT,
                    license_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    allow_offline INTEGER NOT NULL DEFAULT 0,
                    custom_interval INTEGER,
                    features TEXT,
                    update_url TEXT,
                    update_hash TEXT,
                    update_version TEXT,
                    notes TEXT,
                    last_seen_at TEXT,
                    last_seen_ip TEXT,
                    last_version TEXT,
                    last_hostname TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Garantir colunas adicionais (cpf, address, email, created_by) mesmo em bases antigas
            cur.execute("PRAGMA table_info(devices)")
            existing_cols = {row[1] for row in cur.fetchall()}
            if "cpf" not in existing_cols:
                cur.execute("ALTER TABLE devices ADD COLUMN cpf TEXT")
            if "address" not in existing_cols:
                cur.execute("ALTER TABLE devices ADD COLUMN address TEXT")
            if "email" not in existing_cols:
                cur.execute("ALTER TABLE devices ADD COLUMN email TEXT")
            if "created_by" not in existing_cols:
                cur.execute("ALTER TABLE devices ADD COLUMN created_by TEXT")
            
            # Tabela blocked_devices
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blocked_devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL UNIQUE,
                    reason TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Tabela access_logs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    user_agent TEXT,
                    hostname TEXT,
                    client_version TEXT,
                    telemetry_json TEXT,
                    allowed INTEGER NOT NULL,
                    message TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Tabela license_history
            cur.execute("""
                CREATE TABLE IF NOT EXISTS license_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    admin TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Tabela de usuários admin do painel
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    must_change_password INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Tabela de usuários/revendedores
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Usuário admin padrão (admin / admin123) se não existir nenhum usuário
            cur.execute("SELECT COUNT(1) FROM admin_users")
            (count,) = cur.fetchone()
            if count == 0:
                default_user = getattr(config, "ADMIN_DEFAULT_USER", "admin")
                default_pass = getattr(config, "ADMIN_DEFAULT_PASSWORD", "admin123")
                cur.execute(
                    "INSERT INTO admin_users (username, password_hash, must_change_password) VALUES (?, ?, 1)",
                    (default_user, _hash_admin_password(default_pass)),
                )
            
            conn.commit()


def _normalize_query(query: str) -> str:
    """Normaliza query SQL: converte ? para %s se usar MySQL"""
    if USE_MYSQL:
        # Contar quantos ? existem
        count = query.count('?')
        # Substituir todos os ? por %s
        query = query.replace('?', '%s', count)
    return query


class DatabaseCursor:
    """Wrapper para cursor que normaliza queries automaticamente"""
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.is_mysql = USE_MYSQL
    
    def execute(self, query: str, params=None):
        """Executa query normalizando placeholders"""
        query = _normalize_query(query)
        if self.is_mysql:
            return self.cursor.execute(query, params)
        else:
            return self.cursor.execute(query, params)
    
    def fetchone(self):
        """Busca uma linha"""
        result = self.cursor.fetchone()
        if self.is_mysql and result:
            # Converter dict para Row-like object
            class Row:
                def __init__(self, data):
                    self._data = data
                def __getitem__(self, key):
                    if isinstance(key, int):
                        return list(self._data.values())[key]
                    return self._data.get(key)
                def __len__(self):
                    return len(self._data)
                def __iter__(self):
                    return iter(self._data.values())
            return Row(result)
        return result
    
    def fetchall(self):
        """Busca todas as linhas"""
        results = self.cursor.fetchall()
        if self.is_mysql and results:
            class Row:
                def __init__(self, data):
                    self._data = data
                def __getitem__(self, key):
                    if isinstance(key, int):
                        return list(self._data.values())[key]
                    return self._data.get(key)
                def __len__(self):
                    return len(self._data)
                def __iter__(self):
                    return iter(self._data.values())
            return [Row(r) for r in results]
        return results
    
    def __getattr__(self, name):
        """Delega outros métodos para o cursor"""
        return getattr(self.cursor, name)


@contextmanager
def get_conn():
    """Context manager para conexão com banco (SQLite ou MySQL)"""
    init_db()
    
    if USE_MYSQL:
        if not MYSQL_AVAILABLE:
            raise ImportError("MySQL configurado mas pymysql não está instalado. Execute: pip install pymysql")
        
        conn = _get_mysql_connection()
        try:
            yield conn
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


def get_cursor(conn):
    """Retorna cursor normalizado (compatível com SQLite e MySQL)"""
    if USE_MYSQL:
        return DatabaseCursor(conn, conn.cursor())
    else:
        return conn.cursor()
