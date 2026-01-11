import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Banco de dados
# Suporta SQLite (local) ou MySQL (remoto)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "license.db"))

# Configuração MySQL (HostGator)
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()  # "sqlite" ou "mysql"

# MySQL Configuration
# ⚠️ IMPORTANTE: Configure via variáveis de ambiente
# Não use valores padrão com credenciais reais
MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

# Connection string MySQL (para uso com pymysql)
if DB_TYPE == "mysql":
    MYSQL_CONNECTION_STRING = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
else:
    MYSQL_CONNECTION_STRING = None

# ---------------------------------------------------------------------------
# Segurança / políticas
# ---------------------------------------------------------------------------
API_KEY = os.getenv("API_KEY", "")
SHARED_SECRET = os.getenv("SHARED_SECRET", "")
# MAX_TIME_SKEW: tolerância máxima de diferença de tempo entre cliente e servidor (em segundos)
# Padrão: 4 horas (14400s) para permitir diferenças de fuso horário e relógios desincronizados
# Em produção, pode ser reduzido para 300s (5 minutos) se necessário
MAX_TIME_SKEW = int(os.getenv("MAX_TIME_SKEW", "14400"))
REQUIRE_SIGNATURE = os.getenv("REQUIRE_SIGNATURE", "true").lower() == "true"
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "true").lower() == "true"
ALLOW_AUTO_PROVISION = os.getenv("ALLOW_AUTO_PROVISION", "false").lower() == "true"

# Admin do painel (apenas para primeiro acesso; depois pode ser alterado via API)
ADMIN_DEFAULT_USER = os.getenv("ADMIN_DEFAULT_USER", "admin")
ADMIN_DEFAULT_PASSWORD = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123")

# Durações padrão por tipo de licença
LICENSE_PERIODS = {
    "mensal": "P1M",
    "trimestral": "P3M",
    "semestral": "P6M",
    "anual": "P1Y",
    "trianual": "P3Y",
    "vitalicia": None,
}

# Config padrão devolvida quando não há personalização no BD
DEFAULT_CONFIG = {
    "interval": 30,
    "features": ["core"],
    "message": "",
}

# Lista rápida de IDs bloqueados (hardcoded)
HARDCODED_BLOCKLIST = [
    # "12345ABC",
]

# ---------------------------------------------------------------------------
# Detecção de clones (anti-pirataria)
# ---------------------------------------------------------------------------
# Detecta quando o mesmo Device ID é usado de IPs diferentes simultaneamente
ENABLE_CLONE_DETECTION = os.getenv("ENABLE_CLONE_DETECTION", "true").lower() == "true"
# Máximo de IPs diferentes que podem acessar o mesmo Device ID simultaneamente
MAX_SIMULTANEOUS_IPS = int(os.getenv("MAX_SIMULTANEOUS_IPS", "1"))
# Janela de tempo (em segundos) para considerar acessos como "simultâneos"
CLONE_DETECTION_WINDOW = int(os.getenv("CLONE_DETECTION_WINDOW", "300"))  # 5 minutos

# ---------------------------------------------------------------------------
# Configuração de Email (SMTP)
# ---------------------------------------------------------------------------
SMTP_ENABLED = os.getenv("SMTP_ENABLED", "false").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Sistema de Licenciamento")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# Dias antes do vencimento para enviar alertas
EMAIL_ALERT_DAYS = [3, 2, 1]  # Envia emails quando faltam 3, 2 e 1 dia

# ---------------------------------------------------------------------------
# Modo Offline / Período de Graça
# ---------------------------------------------------------------------------
# Período de graça (em dias) para permitir uso offline quando servidor está indisponível
# Durante este período, o cliente pode usar o sistema mesmo sem conexão com o servidor
OFFLINE_GRACE_PERIOD_DAYS = int(os.getenv("OFFLINE_GRACE_PERIOD_DAYS", "7"))  # 7 dias padrão

# ---------------------------------------------------------------------------
# Lista de Servidores para Redundância
# ---------------------------------------------------------------------------
# Lista de servidores em ordem de prioridade para os clientes AHK
# O cliente tentará cada servidor até encontrar um que funcione
# IMPORTANTE: A ordem importa - primeiro é o servidor principal
LICENSE_SERVERS = [
    "https://api.epr.app.br",
    "https://licence-api-6evg.onrender.com",
    "https://api-epr.rj.r.appspot.com",
]

# Permite sobrescrever via variável de ambiente (formato: URL1,URL2,URL3)
servers_env = os.getenv("LICENSE_SERVERS", "")
if servers_env:
    LICENSE_SERVERS = [s.strip() for s in servers_env.split(",") if s.strip()]






