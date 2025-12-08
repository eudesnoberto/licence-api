from contextlib import contextmanager
import hashlib
import sqlite3
from pathlib import Path

import config


DB_PATH = Path(config.DB_PATH)


def _hash_admin_password(raw: str) -> str:
    # Hash simples com sal estático para admin (pode ser trocado depois)
    return hashlib.sha256(f"admin-salt::{raw}".encode("utf-8")).hexdigest()


def init_db() -> None:
    """Cria as tabelas básicas em SQLite, se ainda não existirem."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # Tabela devices
        cur.execute(
            """
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
            """
        )

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
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS blocked_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL UNIQUE,
                reason TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )

        # Tabela access_logs
        cur.execute(
            """
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
            """
        )

        # Tabela license_history
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS license_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                admin TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )

        # Tabela de usuários admin do painel
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                must_change_password INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )

        # Tabela de usuários/revendedores
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
            """
        )

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


@contextmanager
def get_conn() -> sqlite3.Connection:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

