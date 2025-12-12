# 🔄 Solução: Manter Servidor Render Ativo (Keep-Alive)

## 🎯 Problema

O Render free "dorme" após 15 minutos de inatividade, causando:
- ⚠️ Delay de 50+ segundos na primeira requisição após "dormir"
- ⚠️ Possível perda de dados do SQLite (sistema de arquivos efêmero)
- ⚠️ Experiência ruim para usuários

---

## ✅ Solução: Keep-Alive Externo (GRATUITO)

### **Opção 1: UptimeRobot (Recomendado - Mais Fácil)**

1. **Criar conta gratuita:**
   - Acesse: https://uptimerobot.com
   - Crie uma conta (gratuita, até 50 monitores)

2. **Adicionar Monitor:**
   - Clique em "Add New Monitor"
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: License API Keep-Alive
   - **URL**: `https://licence-api-zsbg.onrender.com/ping`
   - **Monitoring Interval**: 5 minutes (mínimo no plano free)
   - Clique em "Create Monitor"

3. **Pronto!** O UptimeRobot fará ping a cada 5 minutos, mantendo o servidor ativo.

---

### **Opção 2: cron-job.org (Alternativa)**

1. **Criar conta:**
   - Acesse: https://cron-job.org
   - Crie uma conta gratuita

2. **Criar Job:**
   - Clique em "Create cronjob"
   - **Title**: License API Keep-Alive
   - **Address**: `https://licence-api-zsbg.onrender.com/ping`
   - **Schedule**: A cada 5 minutos (`*/5 * * * *`)
   - Clique em "Create"

3. **Pronto!** O cron-job.org fará requisições a cada 5 minutos.

---

### **Opção 3: Python Script Local (Se tiver PC sempre ligado)**

Crie um script que faz ping periodicamente:

```python
# keep_alive.py
import requests
import time
from datetime import datetime

API_URL = "https://licence-api-zsbg.onrender.com/ping"
INTERVAL = 300  # 5 minutos

while True:
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            print(f"[{datetime.now()}] ✅ Servidor ativo")
        else:
            print(f"[{datetime.now()}] ⚠️  Servidor respondeu com status {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Erro: {e}")
    
    time.sleep(INTERVAL)
```

Execute:
```powershell
python keep_alive.py
```

---

## 🗄️ Solução Adicional: Migrar para PostgreSQL (Persistência Real)

O SQLite no Render free é **efêmero** (perde dados quando reinicia). A melhor solução é migrar para PostgreSQL.

### **Render oferece PostgreSQL GRATUITO:**

1. **Criar Banco PostgreSQL no Render:**
   - Dashboard → New → PostgreSQL
   - Nome: `license-db`
   - Plano: Free
   - Criar

2. **Obter Connection String:**
   - Dashboard → Seu banco → Connection String
   - Copie a string (ex: `postgresql://user:pass@host:5432/dbname`)

3. **Configurar no Render:**
   - Dashboard → Seu serviço → Environment
   - Adicionar: `DATABASE_URL=postgresql://...`

4. **Atualizar código para usar PostgreSQL:**
   - Usar `psycopg2` ao invés de `sqlite3`
   - Adaptar queries SQL

---

## 📋 Endpoint Criado

Foi criado o endpoint `/ping` que pode ser usado para keep-alive:

```bash
curl https://licence-api-zsbg.onrender.com/ping
```

Resposta:
```json
{
  "status": "ok",
  "message": "Server is alive",
  "timestamp": "2025-12-08T...",
  "server": "license-api"
}
```

---

## 🎯 Recomendação

**Para solução rápida:**
1. ✅ Use **UptimeRobot** (gratuito, fácil, confiável)
2. ✅ Configure para fazer ping em `/ping` a cada 5 minutos

**Para solução definitiva:**
1. ✅ Migre para **PostgreSQL** (gratuito no Render)
2. ✅ Dados persistem mesmo se servidor reiniciar
3. ✅ Mais robusto para produção

---

## ⚙️ Configuração Atual

O endpoint `/ping` já está criado e funcionando. Basta configurar o keep-alive externo!

---

## 📊 Monitoramento

Após configurar, você pode verificar:

1. **Logs do Render:**
   - Dashboard → Seu serviço → Logs
   - Deve ver requisições GET em `/ping` a cada 5 minutos

2. **UptimeRobot Dashboard:**
   - Mostra status do servidor
   - Alertas se servidor cair

---

**Solução implementada!** Configure o keep-alive externo e o servidor não vai mais "dormir"! 🚀



