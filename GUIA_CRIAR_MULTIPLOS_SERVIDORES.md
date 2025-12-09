# 🚀 Guia: Como Criar Múltiplos Servidores (Principal + Backups)

## 🎯 Objetivo

Criar 3 servidores hospedando a mesma API para ter redundância:
- **Servidor Principal**: Railway.app
- **Backup 1**: Render.com
- **Backup 2**: Fly.io (opcional)

---

## 📋 Pré-requisitos

- ✅ Código no GitHub: https://github.com/eudesnoberto/licence-api
- ✅ Contas gratuitas nos serviços:
  - Railway.app
  - Render.com
  - Fly.io (opcional)

---

## 🚂 SERVIDOR 1: Railway.app (Principal)

### **Passo 1: Criar Conta**
1. Acesse: https://railway.app
2. Clique em "Login" → "Sign up with GitHub"
3. Autorize acesso

### **Passo 2: Criar Projeto**
1. Clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha: `eudesnoberto/licence-api`
4. Railway detectará Python automaticamente

### **Passo 3: Configurar Variáveis**
Vá em **"Variables"** e adicione:

```
FLASK_ENV=production
PORT=5000
DB_PATH=/data/protecao.db
# ⚠️ IMPORTANTE: Substitua pelos valores reais
API_KEY=SUA_API_KEY_AQUI
SHARED_SECRET=SEU_SHARED_SECRET_AQUI
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
SMTP_ENABLED=false
ALLOW_AUTO_PROVISION=false
```

### **Passo 4: Configurar Porta**
1. Vá em **"Settings"** → **"Networking"**
2. Port: `5000`
3. Public: `true`

### **Passo 5: Obter URL**
Após deploy, Railway fornecerá URL como:
```
https://licence-api-production.up.railway.app
```

**OU configure domínio customizado:**
1. Vá em **"Settings"** → **"Domains"**
2. Adicione domínio: `api1.fartgreen.fun` (se você tiver)
3. Configure DNS apontando para Railway

### **Passo 6: Renomear (Opcional)**
Para ter URL mais curta:
1. Vá em **"Settings"**
2. Altere **"Service Name"** para algo como `api1`
3. URL ficará: `https://api1.railway.app`

---

## 🎨 SERVIDOR 2: Render.com (Backup 1)

### **Passo 1: Criar Conta**
1. Acesse: https://render.com
2. Clique em **"Get Started for Free"**
3. Conecte com GitHub

### **Passo 2: Criar Web Service**
1. Clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte repositório: `eudesnoberto/licence-api`
4. Clique em **"Connect"**

### **Passo 3: Configurar**
Preencha:

- **Name**: `licence-api-backup1` (ou qualquer nome)
- **Region**: `Oregon (US West)`
- **Branch**: `main`
- **Root Directory**: Deixe **VAZIO**
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  cd api && python app.py
  ```

### **Passo 4: Variáveis de Ambiente**
Vá em **"Environment"** e adicione:

```
FLASK_ENV=production
PORT=10000
DB_PATH=/opt/render/project/src/api/license.db
# ⚠️ IMPORTANTE: Substitua pelos valores reais
API_KEY=SUA_API_KEY_AQUI
SHARED_SECRET=SEU_SHARED_SECRET_AQUI
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
SMTP_ENABLED=false
ALLOW_AUTO_PROVISION=false
```

**⚠️ IMPORTANTE**: Render usa porta **10000**, não 5000!

### **Passo 5: Deploy**
1. Clique em **"Create Web Service"**
2. Aguarde deploy (3-5 minutos)
3. URL será: `https://licence-api-backup1.onrender.com`

### **Passo 6: Domínio Customizado (Opcional)**
1. Vá em **"Settings"** → **"Custom Domain"**
2. Adicione: `api-backup1.fartgreen.fun`
3. Configure DNS apontando para Render

---

## 🪂 SERVIDOR 3: Fly.io (Backup 2 - Opcional)

### **Passo 1: Instalar CLI**
```powershell
# No PowerShell (como Administrador)
iwr https://fly.io/install.ps1 -useb | iex
```

### **Passo 2: Login**
```powershell
fly auth login
```

### **Passo 3: Criar App**
```powershell
cd C:\protecao
fly launch
```

Siga as instruções:
- App name: `licence-api-backup2`
- Region: escolha mais próximo
- PostgreSQL: No (usamos SQLite)
- Redis: No

### **Passo 4: Configurar fly.toml**
Crie/edite `fly.toml`:

```toml
app = "licence-api-backup2"
primary_region = "gru"  # ou região mais próxima

[build]

[env]
  FLASK_ENV = "production"
  PORT = "8080"
  DB_PATH = "/data/protecao.db"
  # ⚠️ IMPORTANTE: Configure via variáveis de ambiente
  # API_KEY = "SUA_API_KEY_AQUI"
  # SHARED_SECRET = "SEU_SHARED_SECRET_AQUI"
  # REQUIRE_API_KEY = "true"
  REQUIRE_SIGNATURE = "true"
  SMTP_ENABLED = "false"
  ALLOW_AUTO_PROVISION = "false"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

### **Passo 5: Deploy**
```powershell
fly deploy
```

### **Passo 6: Obter URL**
Após deploy, URL será:
```
https://licence-api-backup2.fly.dev
```

---

## 🔧 Configurar Cliente AHK

### **Atualize `SOLUCAO_COM_REDUNDANCIA.ahk`:**

```autohotkey
; Array de servidores (em ordem de prioridade)
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://api1.railway.app"              ; Principal
g_LicenseAPI_Servers[2] := "https://licence-api-backup1.onrender.com" ; Backup 1
g_LicenseAPI_Servers[3] := "https://licence-api-backup2.fly.dev"   ; Backup 2
```

### **OU com domínios customizados:**

```autohotkey
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://api.fartgreen.fun"           ; Principal
g_LicenseAPI_Servers[2] := "https://api-backup1.fartgreen.fun"   ; Backup 1
g_LicenseAPI_Servers[3] := "https://api-backup2.fartgreen.fun"   ; Backup 2
```

---

## 🌐 Configurar Domínios Customizados (Opcional)

Se você tem domínio `fartgreen.fun`, pode configurar subdomínios:

### **No seu provedor DNS:**

```
api.fartgreen.fun          → CNAME → railway.app
api-backup1.fartgreen.fun  → CNAME → onrender.com
api-backup2.fartgreen.fun  → CNAME → fly.dev
```

### **Depois configure nos serviços:**

1. **Railway**: Settings → Domains → Add `api.fartgreen.fun`
2. **Render**: Settings → Custom Domain → Add `api-backup1.fartgreen.fun`
3. **Fly.io**: `fly domains add api-backup2.fartgreen.fun`

---

## ✅ Checklist de Criação

### **Servidor 1 (Railway):**
- [ ] Conta criada
- [ ] Projeto criado
- [ ] Repositório conectado
- [ ] Variáveis configuradas
- [ ] Deploy realizado
- [ ] URL obtida/testada

### **Servidor 2 (Render):**
- [ ] Conta criada
- [ ] Web Service criado
- [ ] Repositório conectado
- [ ] Variáveis configuradas (PORT=10000)
- [ ] Deploy realizado
- [ ] URL obtida/testada

### **Servidor 3 (Fly.io - Opcional):**
- [ ] CLI instalado
- [ ] Login realizado
- [ ] App criado
- [ ] fly.toml configurado
- [ ] Deploy realizado
- [ ] URL obtida/testada

### **Cliente AHK:**
- [ ] URLs configuradas no array
- [ ] Testado com servidor principal
- [ ] Testado com servidor offline (backup ativa)
- [ ] Testado com todos offline (modo offline)

---

## 🧪 Testar Redundância

### **Teste 1: Todos Online**
- Deve usar Servidor 1 (Railway)
- Log: `license_server_used.txt` mostra índice 1

### **Teste 2: Servidor 1 Offline**
- Desligue Railway ou bloqueie URL
- Deve tentar Servidor 2 (Render)
- Log: `license_server_failover.txt` mostra tentativa

### **Teste 3: Servidores 1 e 2 Offline**
- Desligue Railway e Render
- Deve tentar Servidor 3 (Fly.io)
- Log mostra tentativa de servidor 3

### **Teste 4: Todos Offline**
- Desligue todos os servidores
- Deve usar modo offline (token salvo)
- Log: `license_offline_success.txt`

---

## 📊 Comparação de Serviços

| Serviço | Gratuito | Porta | "Dorme"? | Melhor Para |
|---------|----------|-------|----------|-------------|
| Railway | ✅ $5/mês | 5000 | ❌ Não | Principal |
| Render | ✅ | 10000 | ⚠️ Sim (15min) | Backup |
| Fly.io | ✅ 3 VMs | 8080 | ❌ Não | Backup 2 |

---

## 🎯 Recomendação Final

### **Configuração Ideal:**

1. **Principal**: Railway.app
   - Mais confiável
   - Sempre online
   - URL: `https://api1.railway.app`

2. **Backup 1**: Render.com
   - Backup confiável
   - Pode "dormir" mas funciona
   - URL: `https://licence-api-backup1.onrender.com`

3. **Backup 2**: Fly.io (opcional)
   - Backup adicional
   - Sempre online
   - URL: `https://licence-api-backup2.fly.dev`

### **No Cliente AHK:**

```autohotkey
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://api1.railway.app"
g_LicenseAPI_Servers[2] := "https://licence-api-backup1.onrender.com"
g_LicenseAPI_Servers[3] := "https://licence-api-backup2.fly.dev"
```

---

## 🐛 Problemas Comuns

### **Railway: "Build failed"**
- Verifique `requirements.txt`
- Verifique se Python 3 está selecionado
- Verifique logs

### **Render: "App sleeping"**
- Render free "dorme" após 15min
- Primeira requisição demora ~30s
- Normal para plano gratuito

### **Fly.io: "Deploy failed"**
- Verifique `fly.toml`
- Verifique se porta está correta (8080)
- Verifique logs: `fly logs`

---

## 📝 Próximos Passos

1. ✅ Criar conta Railway
2. ✅ Deploy no Railway (Servidor 1)
3. ✅ Criar conta Render
4. ✅ Deploy no Render (Servidor 2)
5. ✅ (Opcional) Deploy no Fly.io (Servidor 3)
6. ✅ Obter URLs de todos
7. ✅ Configurar cliente AHK
8. ✅ Testar redundância

---

**Documento criado em**: 2024-12-15

