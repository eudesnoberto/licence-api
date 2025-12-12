#!/usr/bin/env python3
"""
Script para testar configuração SMTP e envio de emails.
Execute: python testar_smtp.py
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('api/.env')

# Configurações SMTP
SMTP_ENABLED = os.getenv("SMTP_ENABLED", "false").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Sistema de Licenciamento")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_smtp_config():
    """Testa a configuração SMTP e tenta enviar um email de teste."""
    
    print_section("🔍 Verificando Configuração SMTP")
    
    # Verificar se está habilitado
    print(f"\n✓ SMTP Habilitado: {SMTP_ENABLED}")
    if not SMTP_ENABLED:
        print("❌ ERRO: SMTP não está habilitado!")
        print("   Configure SMTP_ENABLED=true no arquivo .env")
        return False
    
    # Verificar credenciais
    print(f"✓ SMTP Host: {SMTP_HOST}")
    print(f"✓ SMTP Port: {SMTP_PORT}")
    print(f"✓ SMTP User: {SMTP_USER if SMTP_USER else '❌ NÃO CONFIGURADO'}")
    print(f"✓ SMTP Password: {'✓ Configurado' if SMTP_PASSWORD else '❌ NÃO CONFIGURADO'}")
    print(f"✓ SMTP From Email: {SMTP_FROM_EMAIL}")
    print(f"✓ SMTP Use TLS: {SMTP_USE_TLS}")
    
    if not SMTP_USER or not SMTP_PASSWORD:
        print("\n❌ ERRO: SMTP_USER ou SMTP_PASSWORD não configurados!")
        return False
    
    # Testar conexão
    print_section("🔌 Testando Conexão SMTP")
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        print(f"\n🔄 Conectando a {SMTP_HOST}:{SMTP_PORT}...")
        
        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            print("✓ Conexão estabelecida")
            print("🔄 Iniciando TLS...")
            server.starttls()
            print("✓ TLS iniciado")
        else:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
            print("✓ Conexão SSL estabelecida")
        
        print(f"🔄 Autenticando como {SMTP_USER}...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("✓ Autenticação bem-sucedida!")
        
        server.quit()
        print("✓ Conexão fechada")
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ ERRO DE AUTENTICAÇÃO: {e}")
        print("\n💡 Dicas:")
        print("   - Gmail: Use uma 'Senha de App', não a senha normal")
        print("   - Acesse: https://myaccount.google.com/apppasswords")
        print("   - Gere uma senha de app e use ela no SMTP_PASSWORD")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ ERRO DE CONEXÃO: {e}")
        print("\n💡 Dicas:")
        print(f"   - Verifique se {SMTP_HOST} está acessível")
        print(f"   - Verifique se a porta {SMTP_PORT} está aberta")
        print("   - Verifique firewall/antivírus")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        print(f"\n📋 Detalhes:\n{traceback.format_exc()}")
        return False
    
    # Testar envio de email
    print_section("📧 Testando Envio de Email")
    
    email_teste = input("\n📧 Digite um email para teste (ou Enter para pular): ").strip()
    
    if not email_teste:
        print("⚠️  Teste de envio pulado")
        return True
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        print(f"\n🔄 Enviando email de teste para {email_teste}...")
        
        # Criar mensagem
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg["To"] = email_teste
        msg["Subject"] = "Teste de Email - Sistema de Licenciamento"
        
        html_body = """
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
        
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)
        
        # Conectar e enviar
        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("✅ Email enviado com sucesso!")
        print(f"\n📬 Verifique a caixa de entrada de {email_teste}")
        print("   (Também verifique a pasta de Spam/Lixo Eletrônico)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO ao enviar email: {e}")
        import traceback
        print(f"\n📋 Detalhes:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🧪 TESTE DE CONFIGURAÇÃO SMTP")
    print("=" * 60)
    
    success = test_smtp_config()
    
    print_section("📊 Resultado Final")
    
    if success:
        print("\n✅ Configuração SMTP está OK!")
        print("\n💡 Próximos passos:")
        print("   1. Verifique se o email de teste chegou")
        print("   2. Se não chegou, verifique a pasta de Spam")
        print("   3. Teste a recuperação de senha no sistema")
    else:
        print("\n❌ Configuração SMTP com problemas!")
        print("\n💡 Verifique:")
        print("   1. Se SMTP_ENABLED=true no .env")
        print("   2. Se as credenciais estão corretas")
        print("   3. Se o servidor SMTP está acessível")
        print("   4. Os logs acima para mais detalhes")
    
    print("\n" + "=" * 60 + "\n")

