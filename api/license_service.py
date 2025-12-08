from calendar import monthrange
from datetime import date, datetime, timezone, timedelta
from typing import Any, Dict, Optional, List, Tuple

import config
from db import get_conn, get_cursor, USE_MYSQL


def _row_to_dict(row) -> Dict[str, Any]:
    if row is None:
        return {}
    
    # MySQL com DictCursor já retorna dict diretamente
    if USE_MYSQL:
        if isinstance(row, dict):
            return row.copy()
        # Se for Row wrapper, acessar _data
        if hasattr(row, '_data'):
            return row._data.copy()
    
    # SQLite: Row precisa ser convertido
    if hasattr(row, 'keys'):
        return {key: row[key] for key in row.keys()}
    
    # Fallback: tentar dict() normal
    try:
        return dict(row)
    except:
        return {}


def fetch_device(device_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        cur = get_cursor(conn)
        cur.execute(
            "SELECT * FROM devices WHERE device_id = ? LIMIT 1",
            (device_id,),
        )
        row = cur.fetchone()
        return _row_to_dict(row) or None


def is_device_blocklisted(device_id: str) -> bool:
    with get_conn() as conn:
        cur = get_cursor(conn)
        cur.execute(
            "SELECT 1 FROM blocked_devices WHERE device_id = ? LIMIT 1",
            (device_id,),
        )
        return cur.fetchone() is not None


def auto_create_device(device_id: str) -> Dict[str, Any]:
    """Cria registro automático, similar ao PHP (status pending, tipo mensal)."""
    start = datetime.now(timezone.utc).date().isoformat()
    license_type = "mensal"
    end = calculate_end_date(license_type, start)

    with get_conn() as conn:
        cur = get_cursor(conn)
        cur.execute(
            """
            INSERT INTO devices (device_id, license_type, status, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (device_id, license_type, "pending", start, end),
        )
        conn.commit()

    fetched = fetch_device(device_id)
    assert fetched is not None
    return fetched


def evaluate_license(device: Dict[str, Any]) -> Dict[str, Any]:
    status = device.get("status")
    license_type = device.get("license_type")
    start_date = device.get("start_date")
    end_date = device.get("end_date")

    # MySQL pode devolver datetime.date ou string; normalizar
    if isinstance(start_date, datetime):
        start_date = start_date.date().isoformat()
    elif isinstance(start_date, date):
        start_date = start_date.isoformat()

    if isinstance(end_date, datetime):
        end_date = end_date.date().isoformat()
    elif isinstance(end_date, date):
        end_date = end_date.isoformat()

    # Bloqueado
    if status == "blocked":
        return {"allow": False, "msg": "Licença bloqueada.", "end_date": end_date}

    # Gerar data de fim se vazia (exceto vitalícia)
    if license_type != "vitalicia" and not end_date and start_date:
        end_date = calculate_end_date(str(license_type), str(start_date))

    # Expiração
    if license_type != "vitalicia" and end_date:
        today = date.today()
        expires = datetime.strptime(str(end_date), "%Y-%m-%d").date()
        if today > expires:
            return {
                "allow": False,
                "msg": f"Licença expirada em {expires.strftime('%d/%m/%Y')}",
                "end_date": end_date,
            }

    # Pending
    if status == "pending":
        return {
            "allow": False,
            "msg": "Licença aguardando aprovação.",
            "end_date": end_date,
        }

    return {"allow": True, "msg": "Licença ativa.", "end_date": end_date}


def calculate_end_date(license_type: str, start_date: str) -> Optional[str]:
    if license_type == "vitalicia":
        return None

    period = config.LICENSE_PERIODS.get(license_type)
    if not period:
        return None

    # Utiliza DateInterval-like simplificado: PnM / PnY
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    years = 0
    months = 0

    if period.endswith("M"):
        months = int(period[1:-1])
    elif period.endswith("Y"):
        years = int(period[1:-1])

    # somar anos/meses manualmente
    year = start.year + years
    month = start.month + months
    while month > 12:
        month -= 12
        year += 1

    day = start.day
    # ajuste simples para meses menores
    last_day = monthrange(year, month)[1]
    if day > last_day:
        day = last_day

    end = date(year, month, day)
    return end.isoformat()


def detect_clone_usage(device_id: str, current_ip: str, current_hostname: str) -> Tuple[bool, Optional[str]]:
    """
    Detecta se o mesmo Device ID está sendo usado de múltiplos IPs simultaneamente.
    
    Returns:
        (is_clone, message): (True, mensagem) se clone detectado, (False, None) caso contrário
    """
    if not config.ENABLE_CLONE_DETECTION:
        return (False, None)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        
        # Busca acessos recentes do mesmo Device ID (dentro da janela de tempo)
        window_start = (datetime.now(timezone.utc) - timedelta(seconds=config.CLONE_DETECTION_WINDOW)).isoformat()
        
        cur.execute(
            """
            SELECT DISTINCT ip, hostname, created_at
            FROM access_logs
            WHERE device_id = ?
              AND created_at >= ?
              AND allowed = 1
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (device_id, window_start),
        )
        
        recent_accesses = cur.fetchall()
        
        if len(recent_accesses) < 2:
            return (False, None)  # Não há acessos suficientes para detectar clone
        
        # Agrupa por IP
        unique_ips = set()
        unique_hostnames = set()
        
        for row in recent_accesses:
            ip = row[0] if row[0] else ""
            hostname = row[1] if row[1] else ""
            if ip:
                unique_ips.add(ip)
            if hostname:
                unique_hostnames.add(hostname)
        
        # Se há mais IPs únicos do que o permitido, é clone
        if len(unique_ips) > config.MAX_SIMULTANEOUS_IPS:
            ips_list = ", ".join(sorted(unique_ips))
            return (
                True,
                f"Uso simultâneo detectado de {len(unique_ips)} IPs diferentes: {ips_list}. Licença bloqueada por possível clonagem."
            )
        
        # Se o IP atual é diferente do último conhecido E há acessos recentes, pode ser clone
        cur.execute("SELECT last_seen_ip, last_hostname FROM devices WHERE device_id = ?", (device_id,))
        last_seen = cur.fetchone()
        
        if last_seen and last_seen[0]:
            last_ip = last_seen[0]
            last_hostname = last_seen[1] if last_seen[1] else ""
            
            # Se IP mudou E hostname mudou E há acessos recentes, suspeito
            if (current_ip != last_ip and 
                current_hostname != last_hostname and 
                last_hostname and 
                current_hostname and
                len(recent_accesses) > 1):
                return (
                    True,
                    f"Mudança suspeita detectada: IP {last_ip} → {current_ip}, Hostname {last_hostname} → {current_hostname}. Possível clonagem."
                )
        
        return (False, None)


def update_device_seen(primary_id: int, ip: str, version: str, hostname: str) -> None:
    with get_conn() as conn:
        cur = get_cursor(conn)
        cur.execute(
            """
            UPDATE devices
               SET last_seen_at = datetime('now'),
                   last_seen_ip = ?,
                   last_version = ?,
                   last_hostname = ?,
                   updated_at = datetime('now')
             WHERE id = ?
            """,
            (ip, version, hostname, primary_id),
        )
        conn.commit()


def insert_access_log(
    device_id: str,
    allowed: bool,
    message: str,
    version: str,
    hostname: str,
    telemetry_json: str,
    ip: str,
    user_agent: str,
) -> None:
    with get_conn() as conn:
        cur = get_cursor(conn)
        cur.execute(
            """
            INSERT INTO access_logs
                (device_id, ip, user_agent, hostname, client_version,
                 telemetry_json, allowed, message)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                device_id,
                ip,
                user_agent,
                hostname,
                version,
                telemetry_json,
                1 if allowed else 0,
                message,
            ),
        )
        conn.commit()


def build_config_payload(device: Dict[str, Any], effective_end: Optional[str]) -> Dict[str, Any]:
    cfg = dict(config.DEFAULT_CONFIG)

    custom_interval = device.get("custom_interval")
    if custom_interval:
        try:
            val = int(custom_interval)
            if val > 0:
                cfg["interval"] = max(15, val)
        except (TypeError, ValueError):
            pass

    features = device.get("features")
    if features:
        # CSV simples: "core,premium"
        feat_list = [f.strip() for f in str(features).split(",") if f.strip()]
        if feat_list:
            cfg["features"] = feat_list

    update_url = device.get("update_url")
    if update_url:
        cfg["update"] = {
            "url": update_url,
            "sha256": device.get("update_hash"),
            "version": device.get("update_version"),
        }

    cfg["license_expires_at"] = effective_end if effective_end else None
    return cfg


