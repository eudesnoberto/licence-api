from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import json
import base64
import logging
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS

import config
from db import get_conn, get_cursor, USE_MYSQL
from license_service import (
    fetch_device,
    is_device_blocklisted,
    auto_create_device,
    evaluate_license,
    update_device_seen,
    insert_access_log,
    build_config_payload,
    detect_clone_usage,
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configura Flask para confiar em proxies (necessário para Cloudflare Tunnel)
# Isso permite que request.remote_addr funcione corretamente com X-Forwarded-For
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# CORS: libera apenas os domínios do dashboard (produção e dev)
CORS(
    app,
    resources={r"/*": {
        "origins": ["https://api.epr.app.br", "https://www.api.epr.app.br", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
    }},
)


def json_response(payload, status=200):
    return jsonify(payload), status


def _admin_hash_password(raw: str) -> str:
    return hashlib.sha256(f"admin-salt::{raw}".encode("utf-8")).hexdigest()


def _make_admin_token(username: str, role: str = "admin") -> str:
    issued_at = datetime.utcnow().isoformat()
    payload = f"{username}|{role}|{issued_at}"
    sig = hmac.new(config.SHARED_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    token_bytes = f"{payload}|{sig}".encode("utf-8")
    return base64.urlsafe_b64encode(token_bytes).decode("utf-8")


def _parse_admin_token(token: str) -> tuple[str, str] | None:
    """Retorna (username, role) ou None se inválido."""
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        parts = raw.split("|")
        if len(parts) == 3:
            # Token antigo (sem role)
            username, issued_at, sig = parts
            expected = hmac.new(
                config.SHARED_SECRET.encode("utf-8"),
                f"{username}|{issued_at}".encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(expected, sig):
                return None
            return (username, "admin")
        elif len(parts) == 4:
            # Token novo (com role)
            username, role, issued_at, sig = parts
            expected = hmac.new(
                config.SHARED_SECRET.encode("utf-8"),
                f"{username}|{role}|{issued_at}".encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(expected, sig):
                return None
            return (username, role)
        return None
    except Exception:
        return None


def get_client_ip() -> str:
    """
    Obtém o IP real do cliente, considerando proxies e Cloudflare.
    Ordem de prioridade:
    1. CF-Connecting-IP (Cloudflare real)
    2. X-Forwarded-For (primeiro IP da lista - após ProxyFix)
    3. X-Real-IP
    4. request.remote_addr (já processado pelo ProxyFix)
    """
    # Cloudflare real envia o IP neste header
    cf_ip = request.headers.get("CF-Connecting-IP", "").strip()
    if cf_ip and cf_ip != "127.0.0.1":
        logger.debug(f"IP obtido via CF-Connecting-IP: {cf_ip}")
        return cf_ip
    
    # X-Forwarded-For (após ProxyFix, request.remote_addr já deve ter o IP correto)
    # Mas vamos verificar manualmente também para garantir
    forwarded_for = request.headers.get("X-Forwarded-For", "").strip()
    if forwarded_for:
        # Pega o primeiro IP da lista (IP do cliente original)
        client_ip = forwarded_for.split(",")[0].strip()
        if client_ip and client_ip != "127.0.0.1":
            logger.debug(f"IP obtido via X-Forwarded-For: {client_ip}")
            return client_ip
    
    # X-Real-IP (alguns proxies usam)
    real_ip = request.headers.get("X-Real-IP", "").strip()
    if real_ip and real_ip != "127.0.0.1":
        logger.debug(f"IP obtido via X-Real-IP: {real_ip}")
        return real_ip
    
    # ProxyFix já processou X-Forwarded-For, então remote_addr deve ter o IP real
    remote_addr = request.remote_addr or ""
    if remote_addr and remote_addr != "127.0.0.1":
        logger.debug(f"IP obtido via request.remote_addr: {remote_addr}")
        return remote_addr
    
    # Se ainda for localhost, tenta obter do ambiente (útil para desenvolvimento)
    if remote_addr == "127.0.0.1":
        # Em desenvolvimento local, pode ser que o cliente esteja na mesma máquina
        # Mas em produção via Cloudflare Tunnel, isso não deveria acontecer
        logger.warning(f"IP é localhost (127.0.0.1) - pode indicar problema de configuração do proxy")
        # Tenta obter do header X-Forwarded-For novamente (pode ter múltiplos IPs)
        if forwarded_for:
            ips = [ip.strip() for ip in forwarded_for.split(",")]
            for ip in ips:
                if ip and ip != "127.0.0.1" and not ip.startswith("10.") and not ip.startswith("192.168."):
                    logger.debug(f"IP obtido do X-Forwarded-For (filtrando local): {ip}")
                    return ip
    
    # Log detalhado para debug (apenas em desenvolvimento)
    if remote_addr == "127.0.0.1":
        logger.warning(f"IP é localhost - Headers disponíveis: X-Forwarded-For={forwarded_for}, X-Real-IP={real_ip}, CF-Connecting-IP={cf_ip}")
    
    return remote_addr or "unknown"


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return json_response({"error": "Unauthorized"}, 401)
        token = auth.split(" ", 1)[1].strip()
        result = _parse_admin_token(token)
        if not result:
            return json_response({"error": "Unauthorized"}, 401)
        username, role = result
        request.admin_username = username  # type: ignore[attr-defined]
        request.user_role = role  # type: ignore[attr-defined]
        return fn(*args, **kwargs)

    return wrapper


@app.route("/health", methods=["GET"])
def health():
    """Endpoint simples para o dashboard testar se a API está online."""
    return json_response({"status": "ok"}, 200)


@app.route("/ping", methods=["GET"])
def ping():
    """
    Endpoint de keep-alive para manter o servidor ativo.
    Pode ser chamado por serviços externos (UptimeRobot, cron-job.org, etc.)
    para evitar que o servidor 'durma' no plano gratuito do Render.
    """
    import datetime
    return json_response({
        "status": "ok",
        "message": "Server is alive",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "server": "license-api"
    }, 200)


@app.route("/verify", methods=["GET"])
def verify():
    id_ = (request.args.get("id") or "").strip()
    version = (request.args.get("version") or "").strip()
    ts = (request.args.get("ts") or "").strip()
    sig = (request.args.get("sig") or "").strip()
    api_key_qs = (request.args.get("api_key") or "").strip()
    api_key_hdr = (request.headers.get("X-API-Key") or "").strip()

    hostname = request.args.get("hostname", "")
    username = request.args.get("username", "")
    osbuild = request.args.get("osbuild", "")
    ram_total = request.args.get("ram_total", "")
    ram_free = request.args.get("ram_free", "")
    cpu_load = request.args.get("cpu_load", "")
    client_time = request.args.get("client_time", "")

    logger.info(f"VERIFY: id={id_[:20]}..., version={version}, ts={ts}, sig_len={len(sig)}")

    if not id_ or not version:
        logger.warning(f"VERIFY: Parâmetros ausentes - id={bool(id_)}, version={bool(version)}")
        return json_response({"allow": False, "msg": "Parâmetros ausentes."}, 400)

    # API key
    if config.REQUIRE_API_KEY and config.API_KEY:
        if api_key_qs != config.API_KEY and api_key_hdr != config.API_KEY:
            logger.warning(f"VERIFY: API key inválida - qs={bool(api_key_qs)}, hdr={bool(api_key_hdr)}")
            return json_response({"allow": False, "msg": "API key inválida."}, 403)

    # Timestamp
    try:
        if not ts or len(ts) != 14:
            logger.warning(f"VERIFY: Timestamp inválido - ts={ts}, len={len(ts) if ts else 0}")
            raise ValueError
        client_dt = datetime.strptime(ts, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError as e:
        logger.warning(f"VERIFY: Erro ao parsear timestamp - ts={ts}, error={e}")
        return json_response({"allow": False, "msg": f"Timestamp inválido: {ts}"}, 400)

    now_utc = datetime.now(timezone.utc)
    time_diff = abs((now_utc - client_dt).total_seconds())
    hours_diff = time_diff / 3600
    
    logger.info(f"VERIFY: Timestamp OK - client={client_dt}, server={now_utc}, diff={time_diff}s ({hours_diff:.1f}h), max_skew={config.MAX_TIME_SKEW}s")
    
    if time_diff > config.MAX_TIME_SKEW:
        logger.warning(f"VERIFY: Requisição expirada - diff={time_diff}s ({hours_diff:.1f}h), max={config.MAX_TIME_SKEW}s")
        hours_max = config.MAX_TIME_SKEW / 3600
        return json_response({
            "allow": False, 
            "msg": f"Relógio desincronizado. Diferença: {int(hours_diff)}h {int((time_diff % 3600) / 60)}min (máximo permitido: {int(hours_max)}h). Sincronize o relógio do sistema."
        }, 400)

    # Assinatura
    if config.REQUIRE_SIGNATURE and config.SHARED_SECRET:
        if not sig:
            logger.warning(f"VERIFY: Assinatura ausente")
            return json_response({"allow": False, "msg": "Assinatura ausente."}, 403)
        expected = hashlib.sha256(
            f"{id_}|{version}|{ts}|{config.SHARED_SECRET}".encode("utf-8")
        ).hexdigest()
        # Usa hmac.compare_digest() em vez de hashlib.compare_digest() para compatibilidade com Python antigo
        if not hmac.compare_digest(expected, sig):
            logger.warning(f"VERIFY: Assinatura inválida - expected={expected[:20]}..., received={sig[:20]}...")
            return json_response({"allow": False, "msg": "Assinatura inválida."}, 403)

    # Blocklist hardcoded
    if id_ in config.HARDCODED_BLOCKLIST:
        return json_response({"allow": False, "msg": "Dispositivo bloqueado."}, 403)

    # Busca/auto provision
    device = fetch_device(id_)
    if not device:
        if not config.ALLOW_AUTO_PROVISION:
            logger.warning(f"VERIFY: ID não registrado - id={id_}")
            return json_response({"allow": False, "msg": "ID não registrado."}, 403)
        logger.info(f"VERIFY: Auto-provisionando dispositivo - id={id_}")
        device = auto_create_device(id_)

    # Blocklist na tabela
    if is_device_blocklisted(id_):
        return json_response(
            {"allow": False, "msg": "Este dispositivo está bloqueado."}, 403
        )

    validation = evaluate_license(device)
    allow = bool(validation["allow"])
    msg = validation["msg"]
    effective_end = validation.get("end_date")
    
    logger.info(f"VERIFY: Device encontrado - id={id_}, license_type={device.get('license_type')}, status={device.get('status')}, allow={allow}, msg={msg}")

    # Detecção de clones (ANTES de atualizar métricas)
    # Obtém IP real do cliente (considerando proxies/Cloudflare)
    ip = get_client_ip()
    is_clone, clone_message = detect_clone_usage(id_, ip, hostname)
    
    if is_clone:
        logger.warning(f"VERIFY: Clone detectado - Device ID: {id_}, IP: {ip}, Hostname: {hostname}, Mensagem: {clone_message}")
        
        # Bloqueia automaticamente
        with get_conn() as conn:
            cur = get_cursor(conn)
            cur.execute(
                "UPDATE devices SET status = 'blocked', updated_at = datetime('now') WHERE device_id = ?",
                (id_,),
            )
            conn.commit()
        
        # Re-avalia a licença (agora bloqueada)
        device["status"] = "blocked"
        validation = evaluate_license(device)
        allow = False
        msg = clone_message or "Licença bloqueada - uso simultâneo detectado."

    # Atualiza métricas de último acesso
    update_device_seen(device["id"], ip, version, hostname)

    # Loga acesso
    telemetry = {
        "hostname": hostname,
        "username": username,
        "osbuild": osbuild,
        "ram_total": ram_total,
        "ram_free": ram_free,
        "cpu_load": cpu_load,
        "client_time": client_time,
    }
    insert_access_log(
        device_id=id_,
        allowed=allow,
        message=msg,
        version=version,
        hostname=hostname,
        telemetry_json=json.dumps(telemetry, ensure_ascii=False),
        ip=ip,
        user_agent=request.headers.get("User-Agent", ""),
    )

    config_payload = build_config_payload(device, effective_end)

    # ------------------------------------------------------------------
    # Token de licença assinado (para cache/offline no cliente)
    # Assinatura HMAC-SHA256 sobre o JSON serializado do payload.
    # ------------------------------------------------------------------
    license_payload = {
        "device_id": id_,
        "license_type": device.get("license_type"),
        "status": device.get("status"),
        "issued_at": now_utc.isoformat(),
        "expires_at": effective_end,
        "features": config_payload.get("features", []),
    }
    payload_raw = json.dumps(license_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    signature = hmac.new(
        config.SHARED_SECRET.encode("utf-8"),
        payload_raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    license_token = {
        "payload": license_payload,
        "payload_raw": payload_raw,
        "signature": signature,
    }

    response_payload = {
        "allow": allow,
        "msg": msg,
        "config": config_payload,
        "license_token": license_token,
    }
    
    logger.info(f"VERIFY: Resposta final - allow={allow}, msg={msg[:50] if msg else 'N/A'}")
    
    return json_response(response_payload)


@app.route("/admin/devices", methods=["GET"])
@require_admin
def admin_devices():
    """Lista dispositivos/licenças para o dashboard. Usuários comuns veem apenas as suas."""
    username = getattr(request, "admin_username", None)
    user_role = getattr(request, "user_role", "admin")
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        if user_role == "admin":
            # Admin vê todas as licenças
            cur.execute(
                """
                SELECT
                    id,
                    device_id,
                    owner_name,
                    cpf,
                    email,
                    address,
                    license_type,
                    status,
                    start_date,
                    end_date,
                    custom_interval,
                    features,
                    last_seen_at,
                    last_seen_ip,
                    last_hostname,
                    last_version,
                    created_by
                FROM devices
                ORDER BY created_at DESC
                """
            )
        else:
            # Usuário comum vê apenas suas licenças
            cur.execute(
                """
                SELECT
                    id,
                    device_id,
                    owner_name,
                    cpf,
                    email,
                    address,
                    license_type,
                    status,
                    start_date,
                    end_date,
                    custom_interval,
                    features,
                    last_seen_at,
                    last_seen_ip,
                    last_hostname,
                    last_version,
                    created_by
                FROM devices
                WHERE created_by = ?
                ORDER BY created_at DESC
                """,
                (username,),
            )
        rows_data = cur.fetchall()
        # Converter rows para dict (compatível com SQLite e MySQL)
        rows = []
        for row in rows_data:
            # MySQL com DictCursor já retorna dict diretamente
            if USE_MYSQL:
                # pymysql DictCursor já retorna dict, apenas copiar
                row_dict = row.copy() if isinstance(row, dict) else dict(row)
            else:
                # SQLite: Row precisa ser convertido para dict
                if hasattr(row, 'keys'):
                    row_dict = {key: row[key] for key in row.keys()}
                else:
                    try:
                        row_dict = dict(row)
                    except:
                        row_dict = {}
            
            # Garantir que created_by existe mesmo em registros antigos
            if "created_by" not in row_dict:
                row_dict["created_by"] = None
            
            rows.append(row_dict)
    
    return json_response({"items": rows})


@app.route("/admin/devices/create", methods=["POST"])
@require_admin
def create_device_license():
    """Cria licença apenas com Device ID (cadastro rápido)."""
    data = request.get_json(silent=True) or {}

    device_id = (data.get("device_id") or "").strip()
    license_type = (data.get("license_type") or "anual").strip()
    owner_name = (data.get("owner_name") or "").strip()
    cpf = (data.get("cpf") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()

    if not device_id:
        return json_response({"error": "Device ID é obrigatório."}, 400)

    if license_type not in ["mensal", "trimestral", "semestral", "anual", "trianual", "vitalicia"]:
        return json_response({"error": "Tipo de licença inválido."}, 400)

    today = datetime.utcnow().date().isoformat()
    from license_service import calculate_end_date

    end = calculate_end_date(license_type, today)

    with get_conn() as conn:
        cur = get_cursor(conn)
        # Verifica se já existe
        username = getattr(request, "admin_username", None)
        cur.execute("SELECT id, created_by FROM devices WHERE device_id = ?", (device_id,))
        exists = cur.fetchone()
        
        # Verificar se usuário comum está tentando atualizar licença de outro usuário
        user_role = getattr(request, "user_role", "admin")
        if exists and user_role != "admin":
            existing_created_by = exists[1] if len(exists) > 1 else None
            if existing_created_by and existing_created_by != username:
                return json_response({"error": "Você não tem permissão para atualizar esta licença."}, 403)

        if exists:
            # Atualiza existente
            # Se created_by for fornecido e usuário for admin, atualiza também
            created_by_update = data.get("created_by")
            # Se não fornecido e for admin, manter o existente ou usar 'admin'
            if not created_by_update and user_role == "admin":
                # Se não fornecido, usar 'admin' para que admin veja todas
                created_by_update = "admin"
            # Se não fornecido e for usuário comum, usar o username atual
            elif not created_by_update and user_role != "admin":
                created_by_update = username
            
            # Sempre atualizar created_by se for admin (pode definir para qualquer usuário)
            if user_role == "admin":
                cur.execute(
                    """
                    UPDATE devices SET
                        owner_name=?,
                        cpf=?,
                        email=?,
                        address=?,
                        license_type=?,
                        status='active',
                        start_date=?,
                        end_date=?,
                        created_by=?,
                        updated_at=datetime('now')
                    WHERE device_id=?
                    """,
                    (owner_name if owner_name else None, cpf if cpf else None, email if email else None, address if address else None, license_type, today, end, created_by_update, device_id),
                )
            else:
                cur.execute(
                    """
                    UPDATE devices SET
                        owner_name=?,
                        cpf=?,
                        email=?,
                        address=?,
                        license_type=?,
                        status='active',
                        start_date=?,
                        end_date=?,
                        updated_at=datetime('now')
                    WHERE device_id=?
                    """,
                    (owner_name if owner_name else None, cpf if cpf else None, email if email else None, address if address else None, license_type, today, end, device_id),
                )
            # Envia email de boas-vindas se email foi fornecido (licença renovada/atualizada)
            if email and config.SMTP_ENABLED:
                try:
                    from email_service import send_welcome_email
                    send_welcome_email(owner_name or "Cliente", email, license_type, today, end)
                    logger.info(f"Email de boas-vindas enviado para {email} - Licença {license_type} atualizada")
                except Exception as e:
                    logger.warning(f"Erro ao enviar email de boas-vindas para {email}: {e}")
        else:
            # Cria novo
            username = getattr(request, "admin_username", None)
            user_role = getattr(request, "user_role", "admin")
            
            # Determinar created_by
            created_by_value = None
            if user_role == "admin":
                # Admin pode especificar created_by, ou usar 'admin' por padrão
                created_by_value = data.get("created_by")
                if not created_by_value:
                    created_by_value = "admin"  # Admin vê todas as licenças sem created_by
            else:
                # Usuário comum sempre cria com seu próprio username
                created_by_value = username
            
            cur.execute(
                """
                INSERT INTO devices (
                    device_id, owner_name, cpf, email, address,
                    license_type, status, start_date, end_date,
                    custom_interval, features, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    device_id,
                    owner_name if owner_name else None,
                    cpf if cpf else None,
                    email if email else None,
                    address if address else None,
                    license_type,
                    "active",
                    today,
                    end,
                    60,
                    "core",
                    created_by_value,  # Usa o valor determinado acima
                ),
            )
        conn.commit()
        
        # Envia email de boas-vindas se email foi fornecido
        if email and config.SMTP_ENABLED:
            try:
                from email_service import send_welcome_email
                send_welcome_email(owner_name or "Cliente", email, license_type, today, end)
                logger.info(f"Email de boas-vindas enviado para {email} - Licença {license_type} criada")
            except Exception as e:
                logger.warning(f"Erro ao enviar email de boas-vindas para {email}: {e}")

    return json_response({"success": True, "device_id": device_id, "license_type": license_type}, 201)


@app.route("/payments/pix/create", methods=["POST"])
@require_admin
def create_pix_payment():
    """Stub seguro: cria/atualiza licença em modo pending e devolve dados fictícios de Pix."""
    data = request.get_json(silent=True) or {}

    owner_name = (data.get("owner_name") or "").strip()
    cpf = (data.get("cpf") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()
    license_type = (data.get("license_type") or "anual").strip()
    device_id = (data.get("device_id") or "").strip()

    if not owner_name or not cpf:
        return json_response({"error": "Nome e CPF são obrigatórios."}, 400)

    # Se não vier device_id, gera um novo (caso uso só administrativo)
    if not device_id:
        device_id = hashlib.sha256(f"{owner_name}|{cpf}|{datetime.utcnow().isoformat()}".encode("utf-8")).hexdigest()[:32]

    today = datetime.utcnow().date().isoformat()
    from license_service import calculate_end_date

    end = calculate_end_date(license_type, today)

    with get_conn() as conn:
        cur = get_cursor(conn)
        cur.execute(
            """
            INSERT INTO devices (
                device_id, owner_name, cpf, email, address,
                license_type, status, start_date, end_date,
                custom_interval, features
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?
            )
            ON CONFLICT(device_id) DO UPDATE SET
                owner_name=excluded.owner_name,
                cpf=excluded.cpf,
                email=excluded.email,
                address=excluded.address,
                license_type=excluded.license_type,
                status='pending',
                start_date=excluded.start_date,
                end_date=excluded.end_date
            """,
            (
                device_id,
                owner_name,
                cpf,
                email,
                address,
                license_type,
                "pending",
                today,
                end,
                data.get("custom_interval") or 60,
                data.get("features") or "core",
            ),
        )
        conn.commit()
        
        # Envia email de boas-vindas se email foi fornecido (apenas se status for 'active')
        # Para 'pending', o email será enviado quando o pagamento for confirmado e status mudar para 'active'
        if email and config.SMTP_ENABLED:
            try:
                from email_service import send_welcome_email
                # Verifica o status final após inserção
                cur.execute("SELECT status FROM devices WHERE device_id = ?", (device_id,))
                final_status = cur.fetchone()
                if final_status and final_status[0] == 'active':
                    send_welcome_email(owner_name, email, license_type, today, end)
                    logger.info(f"Email de boas-vindas enviado para {email} - Licença {license_type} criada via pagamento")
                else:
                    logger.info(f"Email de boas-vindas não enviado - Licença em status '{final_status[0] if final_status else 'unknown'}' (aguardando confirmação de pagamento)")
            except Exception as e:
                logger.warning(f"Erro ao enviar email de boas-vindas para {email}: {e}")

    # Pix stub (sem integração real com PagSeguro ainda)
    payment_id = hashlib.sha256(f"{device_id}|{today}".encode("utf-8")).hexdigest()[:32]
    pix_payload = f"PIX_FAKE_{payment_id}"

    return json_response(
        {
            "device_id": device_id,
            "payment_id": payment_id,
            "pix_qr_text": pix_payload,
            "status": "pending",
        },
        201,
    )


@app.route("/admin/login", methods=["POST"])
def admin_login():
    """Login do painel admin. Retorna token, flag de troca obrigatória de senha e role."""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return json_response({"error": "Credenciais obrigatórias."}, 400)

    with get_conn() as conn:
        cur = get_cursor(conn)
        # Primeiro tenta admin_users
        if USE_MYSQL:
            cur.execute(
                "SELECT password_hash, must_change_password FROM admin_users WHERE username = %s LIMIT 1",
                (username,),
            )
        else:
            cur.execute(
                "SELECT password_hash, must_change_password FROM admin_users WHERE username = ? LIMIT 1",
                (username,),
            )
        row = cur.fetchone()
        if row:
            # Compatível com MySQL DictCursor e SQLite Row
            if USE_MYSQL and hasattr(row, 'keys'):
                pwd_hash, must_change = row['password_hash'], int(row['must_change_password'])
            else:
                pwd_hash = row[0] if isinstance(row, tuple) else row['password_hash']
                must_change = int(row[1] if isinstance(row, tuple) else row['must_change_password'])
            
            if _admin_hash_password(password) == pwd_hash:
                token = _make_admin_token(username, "admin")
                return json_response({
                    "token": token,
                    "must_change_password": bool(must_change),
                    "role": "admin"
                })
        
        # Se não encontrou em admin_users, tenta users
        if USE_MYSQL:
            cur.execute(
                "SELECT password_hash, role FROM users WHERE username = %s LIMIT 1",
                (username,),
            )
        else:
            cur.execute(
                "SELECT password_hash, role FROM users WHERE username = ? LIMIT 1",
                (username,),
            )
        row = cur.fetchone()
        if row:
            # Compatível com MySQL DictCursor e SQLite Row
            if USE_MYSQL and hasattr(row, 'keys'):
                pwd_hash, role = row['password_hash'], row['role']
            else:
                pwd_hash = row[0] if isinstance(row, tuple) else row['password_hash']
                role = row[1] if isinstance(row, tuple) else row['role']
            
            if _user_hash_password(password) == pwd_hash:
                token = _make_admin_token(username, role or "user")
                return json_response({
                    "token": token,
                    "must_change_password": False,
                    "role": role or "user"
                })

    return json_response({"error": "Usuário ou senha inválidos."}, 401)


@app.route("/admin/change-password", methods=["POST"])
@require_admin
def admin_change_password():
    """Permite ao admin trocar a senha (obrigatório no primeiro acesso)."""
    data = request.get_json(silent=True) or {}
    old = (data.get("old_password") or "").strip()
    new = (data.get("new_password") or "").strip()

    if not old or not new:
        return json_response({"error": "Preencha as duas senhas."}, 400)

    username = getattr(request, "admin_username", None)
    if not username:
        return json_response({"error": "Unauthorized"}, 401)

    with get_conn() as conn:
        cur = get_cursor(conn)
        # Verificar em admin_users primeiro
        cur.execute(
            "SELECT password_hash FROM admin_users WHERE username = ? LIMIT 1",
            (username,),
        )
        row = cur.fetchone()
        if row:
            current_hash = row[0]
            if _admin_hash_password(old) != current_hash:
                return json_response({"error": "Senha atual incorreta."}, 400)
            cur.execute(
                "UPDATE admin_users SET password_hash = ?, must_change_password = 0 WHERE username = ?",
                (_admin_hash_password(new), username),
            )
        else:
            # Verificar em users
            cur.execute(
                "SELECT password_hash FROM users WHERE username = ? LIMIT 1",
                (username,),
            )
            row = cur.fetchone()
            if not row:
                return json_response({"error": "Usuário não encontrado."}, 404)
            current_hash = row[0]
            if _user_hash_password(old) != current_hash:
                return json_response({"error": "Senha atual incorreta."}, 400)
            cur.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (_user_hash_password(new), username),
            )
        conn.commit()

    return json_response({"ok": True})


def _user_hash_password(raw: str) -> str:
    """Hash de senha para usuários/revendedores."""
    return hashlib.sha256(f"user-salt::{raw}".encode("utf-8")).hexdigest()


@app.route("/admin/users", methods=["GET"])
@require_admin
def admin_users():
    """Lista todos os usuários/revendedores."""
    with get_conn() as conn:
        cur = get_cursor(conn)
        cur.execute(
            """
            SELECT id, username, email, role, created_at
            FROM users
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
        items = [
            {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "role": row["role"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    return json_response({"items": items})


@app.route("/admin/users/create", methods=["POST"])
@require_admin
def admin_users_create():
    """Cria um novo usuário/revendedor."""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    email = (data.get("email") or "").strip() or None
    role = (data.get("role") or "user").strip()

    if not username or not password:
        return json_response({"error": "Usuário e senha são obrigatórios."}, 400)

    if len(password) < 6:
        return json_response({"error": "Senha deve ter no mínimo 6 caracteres."}, 400)

    if role not in ["admin", "user"]:
        return json_response({"error": "Role deve ser 'admin' ou 'user'."}, 400)

    with get_conn() as conn:
        cur = get_cursor(conn)
        # Verificar se usuário já existe em users
        cur.execute("SELECT id FROM users WHERE username = ? LIMIT 1", (username,))
        if cur.fetchone():
            return json_response({"error": "Usuário já existe."}, 400)
        
        # Verificar se usuário já existe em admin_users
        cur.execute("SELECT id FROM admin_users WHERE username = ? LIMIT 1", (username,))
        if cur.fetchone():
            return json_response({"error": "Usuário já existe."}, 400)

        # Criar usuário
        cur.execute(
            """
            INSERT INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
            """,
            (username, _user_hash_password(password), email, role),
        )
        conn.commit()
        user_id = cur.lastrowid

    logger.info(f"Usuário criado: {username} (ID: {user_id}, Role: {role})")
    return json_response({"ok": True, "user_id": user_id, "username": username, "role": role}, 201)


@app.route("/user/devices/create", methods=["POST"])
@require_admin
def user_devices_create():
    """Permite usuários comuns criarem licenças gratuitas ilimitadas."""
    data = request.get_json(silent=True) or {}
    username = getattr(request, "admin_username", None)
    
    if not username:
        return json_response({"error": "Não autenticado."}, 401)
    
    # Verificar se é usuário comum
    with get_conn() as conn:
        cur = get_cursor(conn)
        # Verificar em users
        cur.execute("SELECT role FROM users WHERE username = ? LIMIT 1", (username,))
        row = cur.fetchone()
        if row:
            user_role = row[0]
        else:
            # Se não está em users, é admin (não pode usar este endpoint)
            return json_response({"error": "Apenas usuários comuns podem usar este endpoint."}, 403)
        
        if user_role != "user":
            return json_response({"error": "Apenas usuários comuns podem criar licenças gratuitas."}, 403)
    
    device_id = (data.get("device_id") or "").strip()
    owner_name = (data.get("owner_name") or "").strip()
    cpf = (data.get("cpf") or "").strip()
    email = (data.get("email") or "").strip()
    address = (data.get("address") or "").strip()

    if not device_id:
        return json_response({"error": "Device ID é obrigatório."}, 400)

    today = datetime.utcnow().date().isoformat()
    # Licença gratuita ilimitada (vitalicia)
    license_type = "vitalicia"

    with get_conn() as conn:
        cur = get_cursor(conn)
        cur.execute("SELECT id FROM devices WHERE device_id = ? LIMIT 1", (device_id,))
        if cur.fetchone():
            return json_response({"error": "Device ID já registrado."}, 400)

        cur.execute(
            """
            INSERT INTO devices (
                device_id, owner_name, cpf, email, address,
                license_type, status, start_date, end_date, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                device_id,
                owner_name if owner_name else None,
                cpf if cpf else None,
                email if email else None,
                address if address else None,
                license_type,
                "active",
                today,
                None,  # Vitalicia não tem end_date
                username,  # Salva quem criou
            ),
        )
        conn.commit()

    logger.info(f"Licença gratuita criada por usuário comum {username} para Device ID: {device_id}")
    return json_response({"success": True, "device_id": device_id, "license_type": license_type}, 201)


@app.route("/admin/devices/update-created-by", methods=["POST"])
@require_admin
def update_device_created_by():
    """Endpoint temporário para atualizar o campo created_by de uma licença."""
    data = request.get_json(silent=True) or {}
    device_id = (data.get("device_id") or "").strip()
    new_created_by = (data.get("created_by") or "").strip()
    
    if not device_id or not new_created_by:
        return json_response({"error": "device_id e created_by são obrigatórios."}, 400)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        # Verificar se licença existe
        cur.execute("SELECT id FROM devices WHERE device_id = ?", (device_id,))
        if not cur.fetchone():
            return json_response({"error": "Licença não encontrada."}, 404)
        
        # Atualizar created_by
        cur.execute(
            "UPDATE devices SET created_by = ?, updated_at = datetime('now') WHERE device_id = ?",
            (new_created_by, device_id)
        )
        conn.commit()
    
    logger.info(f"created_by atualizado para Device ID {device_id}: {new_created_by}")
    return json_response({"success": True, "device_id": device_id, "created_by": new_created_by}, 200)


@app.route("/admin/devices/<device_id>/deactivate", methods=["POST"])
@require_admin
def deactivate_device(device_id: str):
    """Desativa ou reativa uma licença (alterna entre 'blocked' e 'active')."""
    username = getattr(request, "admin_username", None)
    user_role = getattr(request, "user_role", "admin")
    data = request.get_json(silent=True) or {}
    action = data.get("action", "toggle")  # "block", "activate", ou "toggle"
    
    if not username:
        return json_response({"error": "Não autenticado."}, 401)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        
        # Verificar se licença existe e obter status atual
        cur.execute("SELECT id, status, created_by FROM devices WHERE device_id = ?", (device_id,))
        row = cur.fetchone()
        if not row:
            return json_response({"error": "Licença não encontrada."}, 404)
        
        current_status = row[1] if len(row) > 1 else None
        created_by = row[2] if len(row) > 2 else None
        
        # Verificar permissões (usuários comuns só podem desativar suas próprias licenças)
        if user_role != "admin":
            if created_by != username:
                return json_response({"error": "Você não tem permissão para modificar esta licença."}, 403)
        
        # Determinar novo status
        if action == "activate":
            new_status = "active"
        elif action == "block":
            new_status = "blocked"
        else:  # toggle
            new_status = "active" if current_status == "blocked" else "blocked"
        
        # Atualizar status
        cur.execute(
            "UPDATE devices SET status = ?, updated_at = datetime('now') WHERE device_id = ?",
            (new_status, device_id)
        )
        conn.commit()
    
    action_text = "reativada" if new_status == "active" else "desativada"
    logger.info(f"Licença {action_text}: {device_id} por {username} (status: {new_status})")
    return json_response({"success": True, "device_id": device_id, "status": new_status}, 200)


@app.route("/admin/devices/<device_id>/delete", methods=["DELETE"])
@require_admin
def delete_device(device_id: str):
    """Exclui uma licença permanentemente."""
    username = getattr(request, "admin_username", None)
    user_role = getattr(request, "user_role", "admin")
    
    if not username:
        return json_response({"error": "Não autenticado."}, 401)
    
    # Apenas admins podem excluir licenças
    if user_role != "admin":
        return json_response({"error": "Apenas administradores podem excluir licenças."}, 403)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        
        # Verificar se licença existe
        cur.execute("SELECT id FROM devices WHERE device_id = ?", (device_id,))
        if not cur.fetchone():
            return json_response({"error": "Licença não encontrada."}, 404)
        
        # Excluir licença
        cur.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))
        conn.commit()
    
    logger.info(f"Licença excluída: {device_id} por {username}")
    return json_response({"success": True, "device_id": device_id, "message": "Licença excluída permanentemente."}, 200)


@app.route("/user/profile", methods=["GET", "PUT"])
@require_admin
def user_profile():
    """Obtém ou atualiza dados do usuário logado."""
    username = getattr(request, "admin_username", None)
    user_role = getattr(request, "user_role", "admin")
    
    if not username:
        return json_response({"error": "Não autenticado."}, 401)
    
    if request.method == "GET":
        # GET: Retornar perfil do usuário
        with get_conn() as conn:
            cur = get_cursor(conn)
            # Verificar em users
            if USE_MYSQL:
                cur.execute(
                    "SELECT id, username, email, role, created_at FROM users WHERE username = %s LIMIT 1",
                    (username,),
                )
            else:
                cur.execute(
                    "SELECT id, username, email, role, created_at FROM users WHERE username = ? LIMIT 1",
                    (username,),
                )
            row = cur.fetchone()
            if row:
                # Compatível com MySQL DictCursor e SQLite Row
                if USE_MYSQL and hasattr(row, 'keys'):
                    return json_response({
                        "id": row["id"],
                        "username": row["username"],
                        "email": row["email"],
                        "role": row["role"],
                        "created_at": str(row["created_at"]),
                    })
                else:
                    row_dict = dict(row) if hasattr(row, 'keys') else {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "role": row[3],
                        "created_at": row[4],
                    }
                    return json_response(row_dict)
            else:
                # Se não está em users, é admin
                if USE_MYSQL:
                    cur.execute(
                        "SELECT id, username, created_at FROM admin_users WHERE username = %s LIMIT 1",
                        (username,),
                    )
                else:
                    cur.execute(
                        "SELECT id, username, created_at FROM admin_users WHERE username = ? LIMIT 1",
                        (username,),
                    )
                row = cur.fetchone()
                if row:
                    if USE_MYSQL and hasattr(row, 'keys'):
                        return json_response({
                            "id": row["id"],
                            "username": row["username"],
                            "email": None,
                            "role": "admin",
                            "created_at": str(row["created_at"]),
                        })
                    else:
                        return json_response({
                            "id": row[0] if isinstance(row, tuple) else row["id"],
                            "username": row[1] if isinstance(row, tuple) else row["username"],
                            "email": None,
                            "role": "admin",
                            "created_at": str(row[2] if isinstance(row, tuple) else row["created_at"]),
                        })
        
        return json_response({"error": "Usuário não encontrado."}, 404)
    
    else:
        # PUT: Atualizar perfil
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip() or None
        
        with get_conn() as conn:
            cur = get_cursor(conn)
            
            # Verificar primeiro em users
            if USE_MYSQL:
                cur.execute("SELECT id, role FROM users WHERE username = %s LIMIT 1", (username,))
            else:
                cur.execute("SELECT id, role FROM users WHERE username = ? LIMIT 1", (username,))
            row = cur.fetchone()
            
            if row:
                # Usuário existe em users, atualizar email
                if USE_MYSQL:
                    if hasattr(row, 'keys'):
                        user_id, user_role = row['id'], row.get('role', 'user')
                    else:
                        user_id, user_role = row[0], row[1] if len(row) > 1 else 'user'
                    cur.execute(
                        "UPDATE users SET email = %s, updated_at = NOW() WHERE username = %s",
                        (email, username),
                    )
                else:
                    user_id = row[0] if isinstance(row, tuple) else row['id']
                    user_role = row[1] if isinstance(row, tuple) and len(row) > 1 else row.get('role', 'user') if hasattr(row, 'get') else 'user'
                    cur.execute(
                        "UPDATE users SET email = ?, updated_at = datetime('now') WHERE username = ?",
                        (email, username),
                    )
                conn.commit()
                logger.info(f"Perfil atualizado por {username} (email: {email})")
                return json_response({"ok": True, "message": "Perfil atualizado com sucesso."})
            else:
                # Admin não está em users, verificar se está em admin_users
                if USE_MYSQL:
                    cur.execute("SELECT id FROM admin_users WHERE username = %s LIMIT 1", (username,))
                else:
                    cur.execute("SELECT id FROM admin_users WHERE username = ? LIMIT 1", (username,))
                admin_row = cur.fetchone()
                
                if admin_row:
                    # Admin existe em admin_users, criar/atualizar registro em users para permitir email
                    # Verificar se já existe um registro em users com este username (pode ter sido criado antes)
                    if USE_MYSQL:
                        cur.execute("SELECT id FROM users WHERE username = %s LIMIT 1", (username,))
                    else:
                        cur.execute("SELECT id FROM users WHERE username = ? LIMIT 1", (username,))
                    existing_user = cur.fetchone()
                    
                    if existing_user:
                        # Já existe, apenas atualizar email
                        if USE_MYSQL:
                            cur.execute(
                                "UPDATE users SET email = %s, updated_at = NOW() WHERE username = %s",
                                (email, username),
                            )
                        else:
                            cur.execute(
                                "UPDATE users SET email = ?, updated_at = datetime('now') WHERE username = ?",
                                (email, username),
                            )
                    else:
                        # Não existe em users, criar com email e role admin
                        # Usar hash temporário (admin pode alterar senha depois se necessário)
                        import hashlib
                        temp_password_hash = hashlib.sha256(f"user-salt::admin_temp_{username}".encode("utf-8")).hexdigest()
                        
                        if USE_MYSQL:
                            cur.execute(
                                "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                                (username, temp_password_hash, email, 'admin'),
                            )
                        else:
                            cur.execute(
                                "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                                (username, temp_password_hash, email, 'admin'),
                            )
                    
                    conn.commit()
                    logger.info(f"Email adicionado ao admin {username}: {email}")
                    return json_response({"ok": True, "message": "Email adicionado/atualizado com sucesso."})
                else:
                    return json_response({"error": "Usuário não encontrado."}, 404)


@app.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    """Envia email com token para recuperação de senha."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    
    if not email:
        return json_response({"error": "E-mail é obrigatório."}, 400)
    
    if not config.SMTP_ENABLED:
        return json_response({"error": "Recuperação de senha por email não está habilitada."}, 503)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        
        # Verificar primeiro em users (tabela de usuários/revendedores)
        if USE_MYSQL:
            cur.execute("SELECT username FROM users WHERE email = %s LIMIT 1", (email,))
        else:
            cur.execute("SELECT username FROM users WHERE email = ? LIMIT 1", (email,))
        row = cur.fetchone()
        
        # Se não encontrou em users, verificar se é admin (admin_users não tem email, mas podemos verificar por username se necessário)
        # Por enquanto, apenas verificar em users
        if not row:
            logger.warning(f"Tentativa de recuperação de senha com email não cadastrado: {email}")
            # Não revelar se email existe ou não por segurança
            return json_response({"ok": True, "message": "Se o email existir, você receberá instruções."})
        
        # Obter username (compatível com MySQL DictCursor e SQLite Row)
        if USE_MYSQL and hasattr(row, 'keys'):
            username = row['username']
        else:
            username = row[0] if isinstance(row, tuple) else row['username']
        
        # Gerar token de recuperação (válido por 30 minutos)
        import secrets
        reset_token = secrets.token_urlsafe(32)
        reset_expires = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        
        # Salvar token no banco (criar tabela se necessário)
        if USE_MYSQL:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    token VARCHAR(255) NOT NULL UNIQUE,
                    expires_at DATETIME NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_token (token),
                    INDEX idx_expires_at (expires_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            cur.execute(
                "INSERT INTO password_resets (username, token, expires_at) VALUES (%s, %s, %s)",
                (username, reset_token, reset_expires),
            )
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    expires_at TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            cur.execute(
                "INSERT INTO password_resets (username, token, expires_at) VALUES (?, ?, ?)",
                (username, reset_token, reset_expires),
            )
        conn.commit()
        
        # Enviar email
        try:
            from email_service import send_email
            reset_url = f"https://www.api.epr.app.br/#/reset-password?token={reset_token}"
            html_body = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Recuperação de Senha</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f3f4f6;">
                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 40px 20px; text-align: center;">
                            <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                                <tr>
                                    <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                                        <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">🔐 Recuperação de Senha</h1>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 40px 30px;">
                                        <p style="margin: 0 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                            Olá <strong>{username}</strong>,
                                        </p>
                                        <p style="margin: 0 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                            Você solicitou a recuperação de senha. Clique no botão abaixo para redefinir sua senha:
                                        </p>
                                        <p style="margin: 30px 0; text-align: center;">
                                            <a href="{reset_url}" style="display: inline-block; padding: 12px 25px; background-color: #667eea; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600;">
                                                Redefinir Senha
                                            </a>
                                        </p>
                                        <p style="margin: 20px 0 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                            Ou copie e cole este link no navegador:<br>
                                            <code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-size: 12px; word-break: break-all;">{reset_url}</code>
                                        </p>
                                        <p style="margin: 30px 0 0; color: #9ca3af; font-size: 12px; line-height: 1.6;">
                                            Este link expira em 30 minutos. Se você não solicitou esta recuperação, ignore este email.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            success = send_email(
                to_email=email,
                subject="Recuperação de Senha - Easy Play Rockola",
                html_body=html_body,
            )
            if not success:
                logger.error(f"Falha ao enviar email de recuperação para {email} - send_email retornou False")
                logger.error(f"Configuração SMTP: HOST={config.SMTP_HOST}, PORT={config.SMTP_PORT}, USER={config.SMTP_USER}, TLS={config.SMTP_USE_TLS}")
                return json_response({"error": "Erro ao enviar email. Verifique a configuração SMTP no servidor."}, 500)
            logger.info(f"✅ Email de recuperação de senha enviado com sucesso para {email}")
            logger.info(f"   Token gerado: {reset_token[:20]}...")
        except Exception as e:
            import traceback
            logger.error(f"❌ Erro ao enviar email de recuperação: {e}")
            logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
            return json_response({"error": f"Erro ao enviar email: {str(e)}"}, 500)
    
    return json_response({"ok": True, "message": "Se o email existir, você receberá instruções."})


@app.route("/auth/test-email", methods=["POST"])
@require_admin
def test_email():
    """Endpoint para testar envio de email (apenas admin)."""
    data = request.get_json(silent=True) or {}
    test_email_addr = (data.get("email") or "").strip()
    
    if not test_email_addr:
        return json_response({"error": "E-mail é obrigatório."}, 400)
    
    if not config.SMTP_ENABLED:
        return json_response({"error": "SMTP não está habilitado."}, 503)
    
    try:
        from email_service import send_email
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">✅ Teste de Email</h2>
            <p>Este é um email de teste do sistema de licenciamento.</p>
            <p>Se você recebeu este email, a configuração SMTP está funcionando corretamente!</p>
            <hr>
            <p style="color: #6b7280; font-size: 12px;">
                Enviado automaticamente pelo sistema de teste SMTP
            </p>
        </body>
        </html>
        """
        
        success = send_email(
            to_email=test_email_addr,
            subject="Teste de Email - Sistema de Licenciamento",
            html_body=html_body,
        )
        
        if not success:
            logger.error(f"Falha no teste de email para {test_email_addr}")
            return json_response({"error": "Falha ao enviar email de teste. Verifique os logs do servidor."}, 500)
        
        logger.info(f"✅ Email de teste enviado com sucesso para {test_email_addr}")
        return json_response({"ok": True, "message": f"Email de teste enviado para {test_email_addr}. Verifique a caixa de entrada e a pasta de spam."})
        
    except Exception as e:
        import traceback
        logger.error(f"Erro no teste de email: {e}\n{traceback.format_exc()}")
        return json_response({"error": f"Erro ao enviar email de teste: {str(e)}"}, 500)


@app.route("/auth/reset-password", methods=["GET"])
def get_reset_token_info():
    """Retorna informações sobre o token de recuperação (tempo de expiração)."""
    token = request.args.get("token", "").strip()
    
    if not token:
        return json_response({"error": "Token é obrigatório."}, 400)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        # Buscar token e tempo de expiração
        if USE_MYSQL:
            cur.execute(
                "SELECT expires_at FROM password_resets WHERE token = %s LIMIT 1",
                (token,),
            )
        else:
            cur.execute(
                "SELECT expires_at FROM password_resets WHERE token = ? LIMIT 1",
                (token,),
            )
        row = cur.fetchone()
        
        if not row:
            return json_response({"error": "Token inválido."}, 400)
        
        # Obter expires_at (compatível com MySQL DictCursor e SQLite Row)
        from datetime import datetime
        if USE_MYSQL and hasattr(row, 'keys'):
            expires_at = row['expires_at']
        else:
            expires_at = row[0] if isinstance(row, tuple) else row['expires_at']
        
        # Converter para datetime se necessário
        if isinstance(expires_at, str):
            try:
                # Tentar diferentes formatos de data
                if 'T' in expires_at:
                    expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                else:
                    # Formato MySQL: 'YYYY-MM-DD HH:MM:SS'
                    expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
            except Exception as e:
                logger.error(f"Erro ao converter data: {e}, formato: {expires_at}")
                return json_response({"error": "Formato de data inválido."}, 500)
        
        # Verificar se já expirou
        now = datetime.utcnow()
        if expires_at <= now:
            return json_response({"error": "Token expirado."}, 400)
        
        # Calcular tempo restante em segundos
        remaining_seconds = int((expires_at - now).total_seconds())
        
        return json_response({
            "ok": True,
            "expires_at": expires_at.isoformat() if isinstance(expires_at, datetime) else str(expires_at),
            "remaining_seconds": remaining_seconds,
        })


@app.route("/auth/reset-password", methods=["POST"])
def reset_password():
    """Redefine a senha usando token de recuperação."""
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = (data.get("new_password") or "").strip()
    
    if not token or not new_password:
        return json_response({"error": "Token e nova senha são obrigatórios."}, 400)
    
    # Validar requisitos da senha
    if len(new_password) < 6:
        return json_response({"error": "Senha deve ter no mínimo 6 caracteres."}, 400)
    
    import re
    if not re.search(r'\d', new_password):
        return json_response({"error": "Senha deve conter pelo menos um número."}, 400)
    
    if not re.search(r'[a-z]', new_password):
        return json_response({"error": "Senha deve conter pelo menos uma letra minúscula."}, 400)
    
    if not re.search(r'[A-Z]', new_password):
        return json_response({"error": "Senha deve conter pelo menos uma letra maiúscula."}, 400)
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', new_password):
        return json_response({"error": "Senha deve conter pelo menos um caractere especial (!@#$%^&*)."}, 400)
    
    with get_conn() as conn:
        cur = get_cursor(conn)
        # Verificar token
        if USE_MYSQL:
            cur.execute(
                "SELECT username, expires_at FROM password_resets WHERE token = %s AND expires_at > NOW() LIMIT 1",
                (token,),
            )
        else:
            cur.execute(
                "SELECT username, expires_at FROM password_resets WHERE token = ? AND expires_at > datetime('now') LIMIT 1",
                (token,),
            )
        row = cur.fetchone()
        if not row:
            return json_response({"error": "Token inválido ou expirado."}, 400)
        
        # Obter username e expires_at (compatível com MySQL DictCursor e SQLite Row)
        if USE_MYSQL and hasattr(row, 'keys'):
            username, expires_at = row['username'], row['expires_at']
        else:
            username = row[0] if isinstance(row, tuple) else row['username']
            expires_at = row[1] if isinstance(row, tuple) else row['expires_at']
        
        # IMPORTANTE: Deletar o token ANTES de atualizar a senha para evitar uso múltiplo
        # Isso garante que mesmo se houver erro depois, o token já foi invalidado
        if USE_MYSQL:
            cur.execute("DELETE FROM password_resets WHERE token = %s", (token,))
        else:
            cur.execute("DELETE FROM password_resets WHERE token = ?", (token,))
        
        # Verificar se usuário existe em admin_users ou users
        user_found = False
        is_admin = False
        
        if USE_MYSQL:
            cur.execute("SELECT id FROM admin_users WHERE username = %s LIMIT 1", (username,))
        else:
            cur.execute("SELECT id FROM admin_users WHERE username = ? LIMIT 1", (username,))
        admin_row = cur.fetchone()
        
        if admin_row:
            # Usuário está em admin_users - atualizar lá
            is_admin = True
            user_found = True
            if USE_MYSQL:
                cur.execute(
                    "UPDATE admin_users SET password_hash = %s, must_change_password = 0 WHERE username = %s",
                    (_admin_hash_password(new_password), username),
                )
            else:
                cur.execute(
                    "UPDATE admin_users SET password_hash = ?, must_change_password = 0 WHERE username = ?",
                    (_admin_hash_password(new_password), username),
                )
        else:
            # Verificar em users
            if USE_MYSQL:
                cur.execute("SELECT id FROM users WHERE username = %s LIMIT 1", (username,))
            else:
                cur.execute("SELECT id FROM users WHERE username = ? LIMIT 1", (username,))
            user_row = cur.fetchone()
            
            if user_row:
                user_found = True
                if USE_MYSQL:
                    cur.execute(
                        "UPDATE users SET password_hash = %s WHERE username = %s",
                        (_user_hash_password(new_password), username),
                    )
                else:
                    cur.execute(
                        "UPDATE users SET password_hash = ? WHERE username = ?",
                        (_user_hash_password(new_password), username),
                    )
        
        if not user_found:
            conn.rollback()  # Reverter a deleção do token se usuário não foi encontrado
            return json_response({"error": "Usuário não encontrado."}, 404)
        
        conn.commit()
        
        logger.info(f"Senha redefinida para usuário {username} via token (tipo: {'admin' if is_admin else 'user'})")
        return json_response({"ok": True, "message": "Senha redefinida com sucesso."})


# ============================================================================
# Scheduler para envio de emails de expiração
# ============================================================================
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from email_service import check_and_send_expiration_emails
    
    scheduler = BackgroundScheduler()
    # Executa diariamente às 09:00
    scheduler.add_job(
        check_and_send_expiration_emails,
        trigger=CronTrigger(hour=9, minute=0),
        id="check_expiration_emails",
        name="Verificar e enviar emails de expiração",
        replace_existing=True,
    )
    SCHEDULER_AVAILABLE = True
except ImportError:
    logger.warning("APScheduler não disponível - emails automáticos desabilitados")
    SCHEDULER_AVAILABLE = False
    scheduler = None

if __name__ == "__main__":
    # Keep-alive interno (apenas se variável de ambiente estiver definida)
    # Isso ajuda a manter servidor ativo, mas keep-alive externo é mais confiável
    import os
    import threading
    import time
    
    ENABLE_INTERNAL_KEEP_ALIVE = os.getenv("ENABLE_INTERNAL_KEEP_ALIVE", "false").lower() == "true"
    KEEP_ALIVE_URL = os.getenv("KEEP_ALIVE_URL", "")
    
    if ENABLE_INTERNAL_KEEP_ALIVE and KEEP_ALIVE_URL:
        def keep_alive_loop():
            """Faz ping periódico no próprio servidor para mantê-lo ativo"""
            import requests
            interval = 300  # 5 minutos
            while True:
                try:
                    time.sleep(interval)
                    requests.get(f"{KEEP_ALIVE_URL}/ping", timeout=10)
                    logger.debug("Keep-alive interno executado")
                except Exception as e:
                    logger.warning(f"Erro no keep-alive interno: {e}")
        
        keep_alive_thread = threading.Thread(target=keep_alive_loop, daemon=True)
        keep_alive_thread.start()
        logger.info("Keep-alive interno iniciado (recomendado usar serviço externo como UptimeRobot)")
    
    # Inicia scheduler
    if SCHEDULER_AVAILABLE and config.SMTP_ENABLED:
        scheduler.start()
        logger.info("Scheduler de emails iniciado - verificará expirações diariamente às 09:00")
    elif config.SMTP_ENABLED and not SCHEDULER_AVAILABLE:
        logger.warning("SMTP habilitado mas scheduler não disponível - instale apscheduler")
    
    # Suporta variável de ambiente PORT (para Railway, Render, Fly.io, etc.)
    import os
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV", "development") != "production"
    
    # Em produção, use gunicorn/uwsgi + nginx e debug=False
    app.run(host="0.0.0.0", port=port, debug=debug_mode)





