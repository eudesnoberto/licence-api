"""
Serviço de envio de emails para notificações de licenças.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime
from typing import Optional

import config
from db import get_conn


def get_welcome_email_template(owner_name: str, license_type: str, start_date: str, end_date: str, days_duration: int) -> str:
    """
    Gera template HTML moderno para email de boas-vindas/ativação.
    """
    license_type_names = {
        "mensal": "Mensal",
        "trimestral": "Trimestral",
        "semestral": "Semestral",
        "anual": "Anual",
        "trianual": "Trienal",
        "vitalicia": "Vitalícia"
    }
    
    license_name = license_type_names.get(license_type, license_type.capitalize())
    days_text = "dia" if days_duration == 1 else "dias"
    
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bem-vindo ao Easy Play Rockola</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px; text-align: center;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">🎉 Parabéns!</h1>
                            <p style="margin: 10px 0 0; color: #ffffff; font-size: 18px; opacity: 0.9;">Sua licença foi ativada com sucesso</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                Olá <strong>{owner_name}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 30px; color: #374151; font-size: 16px; line-height: 1.6;">
                                É com grande satisfação que informamos que sua licença do <strong style="color: #667eea;">Easy Play Rockola</strong> foi ativada com sucesso!
                            </p>
                            
                            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border: 2px solid #667eea; padding: 30px; border-radius: 12px; margin: 30px 0; text-align: center;">
                                <h2 style="margin: 0 0 15px; color: #667eea; font-size: 24px; font-weight: 700;">Easy Play Rockola</h2>
                                <p style="margin: 0; color: #1f2937; font-size: 18px; font-weight: 600;">
                                    Licença <span style="color: #667eea;">{license_name}</span> Ativada
                                </p>
                            </div>
                            
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0; background-color: #f9fafb; border-radius: 8px; overflow: hidden;">
                                <tr>
                                    <td style="padding: 20px; border-bottom: 1px solid #e5e7eb;">
                                        <strong style="color: #6b7280; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Plano Escolhido</strong>
                                        <p style="margin: 8px 0 0; color: #111827; font-size: 20px; font-weight: 700; color: #667eea;">{license_name}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px; border-bottom: 1px solid #e5e7eb;">
                                        <strong style="color: #6b7280; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Duração da Licença</strong>
                                        <p style="margin: 8px 0 0; color: #111827; font-size: 18px; font-weight: 600;">{days_duration} {days_text}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px; border-bottom: 1px solid #e5e7eb;">
                                        <strong style="color: #6b7280; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Data de Início</strong>
                                        <p style="margin: 8px 0 0; color: #111827; font-size: 16px; font-weight: 600;">{start_date}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px;">
                                        <strong style="color: #6b7280; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Data de Expiração</strong>
                                        <p style="margin: 8px 0 0; color: #111827; font-size: 16px; font-weight: 600;">{end_date}</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <div style="background-color: #ecfdf5; border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin: 30px 0;">
                                <p style="margin: 0; color: #065f46; font-size: 16px; line-height: 1.6;">
                                    ✅ <strong>Sua licença está ativa!</strong> Você já pode começar a usar o <strong>Easy Play Rockola</strong> imediatamente.
                                </p>
                            </div>
                            
                            <p style="margin: 30px 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                Agradecemos sua confiança e esperamos que aproveite ao máximo todas as funcionalidades do sistema.
                            </p>
                            
                            <div style="text-align: center; margin: 40px 0;">
                                <a href="https://api.epr.app.br" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 16px 32px; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);">
                                    Acessar Dashboard
                                </a>
                            </div>
                            
                            <p style="margin: 30px 0 0; color: #6b7280; font-size: 14px; line-height: 1.6; border-top: 1px solid #e5e7eb; padding-top: 20px;">
                                Em caso de dúvidas ou necessidade de suporte, nossa equipe está sempre à disposição.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                Este é um email automático de confirmação de ativação.
                            </p>
                            <p style="margin: 10px 0 0; color: #9ca3af; font-size: 11px;">
                                © {datetime.now().year} Easy Play Rockola. Todos os direitos reservados.
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
    return html


def calculate_license_days(start_date: str, end_date: str) -> int:
    """
    Calcula quantos dias de duração tem a licença.
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        delta = end - start
        return delta.days
    except:
        return 0


def send_welcome_email(owner_name: str, email: str, license_type: str, start_date: str, end_date: str) -> bool:
    """
    Envia email de boas-vindas quando licença é criada/ativada.
    """
    if not email or not config.SMTP_ENABLED:
        return False
    
    days_duration = calculate_license_days(start_date, end_date)
    html_body = get_welcome_email_template(owner_name, license_type, start_date, end_date, days_duration)
    subject = f"🎉 Parabéns! Sua licença do Easy Play Rockola foi ativada"
    
    return send_email(email, subject, html_body)


def get_email_template(days_remaining: int, owner_name: str, license_type: str, end_date: str) -> str:
    """
    Gera template HTML moderno para email de alerta de expiração.
    """
    days_text = "dia" if days_remaining == 1 else "dias"
    urgency_color = "#dc2626" if days_remaining == 1 else "#f59e0b" if days_remaining == 2 else "#3b82f6"
    
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerta de Expiração de Licença</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px; text-align: center;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">⚠️ Alerta de Expiração</h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                Olá <strong>{owner_name}</strong>,
                            </p>
                            
                            <div style="background-color: {urgency_color}15; border-left: 4px solid {urgency_color}; padding: 20px; border-radius: 8px; margin: 30px 0;">
                                <p style="margin: 0; color: #1f2937; font-size: 18px; font-weight: 600;">
                                    Sua licença expira em <span style="color: {urgency_color}; font-size: 24px; font-weight: 700;">{days_remaining} {days_text}</span>
                                </p>
                            </div>
                            
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0; background-color: #f9fafb; border-radius: 8px; overflow: hidden;">
                                <tr>
                                    <td style="padding: 15px; border-bottom: 1px solid #e5e7eb;">
                                        <strong style="color: #6b7280; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Tipo de Licença</strong>
                                        <p style="margin: 5px 0 0; color: #111827; font-size: 16px; font-weight: 600;">{license_type.capitalize()}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px;">
                                        <strong style="color: #6b7280; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Data de Expiração</strong>
                                        <p style="margin: 5px 0 0; color: #111827; font-size: 16px; font-weight: 600;">{end_date}</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 30px 0 20px; color: #374151; font-size: 16px; line-height: 1.6;">
                                Para continuar usando o sistema sem interrupções, é necessário renovar sua licença antes da data de expiração.
                            </p>
                            
                            <div style="text-align: center; margin: 40px 0;">
                                <a href="https://api.epr.app.br" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 16px 32px; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);">
                                    Renovar Licença Agora
                                </a>
                            </div>
                            
                            <p style="margin: 30px 0 0; color: #6b7280; font-size: 14px; line-height: 1.6; border-top: 1px solid #e5e7eb; padding-top: 20px;">
                                Se você já renovou sua licença, pode ignorar este email. Em caso de dúvidas, entre em contato com nosso suporte.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                Este é um email automático. Por favor, não responda.
                            </p>
                            <p style="margin: 10px 0 0; color: #9ca3af; font-size: 11px;">
                                © {datetime.now().year} Sistema de Licenciamento. Todos os direitos reservados.
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
    return html


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Envia email usando SMTP configurado.
    
    Returns:
        True se enviado com sucesso, False caso contrário
    """
    if not config.SMTP_ENABLED:
        return False
    
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        return False
    
    try:
        # Cria mensagem
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{config.SMTP_FROM_NAME} <{config.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Adiciona corpo HTML
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)
        
        # Conecta e envia
        if config.SMTP_USE_TLS:
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
        
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Erro ao enviar email para {to_email}: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        # Log mais detalhado para debug
        if "authentication failed" in error_msg.lower() or "login" in error_msg.lower():
            print("ERRO: Credenciais SMTP inválidas")
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            print("ERRO: Não foi possível conectar ao servidor SMTP")
        elif "tls" in error_msg.lower() or "ssl" in error_msg.lower():
            print("ERRO: Problema com TLS/SSL no SMTP")
        return False


def check_and_send_expiration_emails():
    """
    Verifica licenças próximas do vencimento e envia emails de alerta.
    Executa diariamente via scheduler.
    """
    if not config.SMTP_ENABLED:
        return
    
    today = date.today()
    
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Busca licenças ativas que expiram em 1, 2 ou 3 dias
        cur.execute(
            """
            SELECT device_id, owner_name, email, license_type, end_date
            FROM devices
            WHERE status = 'active'
              AND email IS NOT NULL
              AND email != ''
              AND end_date IS NOT NULL
              AND end_date != ''
              AND license_type != 'vitalicia'
            """,
        )
        
        devices = cur.fetchall()
        
        for row in devices:
            device_id, owner_name, email, license_type, end_date_str = row
            
            if not email or not end_date_str:
                continue
            
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                days_remaining = (end_date - today).days
                
                # Verifica se está nos dias de alerta configurados
                if days_remaining in config.EMAIL_ALERT_DAYS:
                    # Verifica se já foi enviado email para este dia
                    cur.execute(
                        """
                        SELECT 1 FROM access_logs
                        WHERE device_id = ?
                          AND message LIKE ?
                          AND created_at >= date('now', '-1 day')
                        LIMIT 1
                        """,
                        (device_id, f"%Email enviado: {days_remaining} dias%"),
                    )
                    
                    already_sent = cur.fetchone()
                    
                    if not already_sent:
                        # Envia email
                        html_body = get_email_template(
                            days_remaining, owner_name or "Cliente", license_type, end_date_str
                        )
                        subject = f"⚠️ Sua licença expira em {days_remaining} {'dia' if days_remaining == 1 else 'dias'}"
                        
                        success = send_email(email, subject, html_body)
                        
                        if success:
                            # Registra no log
                            insert_access_log(
                                device_id=device_id,
                                allowed=True,
                                message=f"Email enviado: {days_remaining} dias restantes",
                                version="system",
                                hostname="system",
                                telemetry_json="{}",
                                ip="system",
                                user_agent="email-service",
                            )
                            print(f"Email enviado para {email} - {days_remaining} dias restantes")
                        else:
                            print(f"Falha ao enviar email para {email}")
                            
            except Exception as e:
                print(f"Erro ao processar dispositivo {device_id}: {e}")


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
    """Helper para inserir log de acesso."""
    from db import get_conn
    with get_conn() as conn:
        cur = conn.cursor()
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

