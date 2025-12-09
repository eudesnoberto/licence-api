# 🔄 Guia Completo: Redundância de Servidores

## 🎯 Objetivo

Ter múltiplos servidores hospedando a mesma API, garantindo que se um cair, o sistema continue funcionando automaticamente.

---

## 📋 Estratégia de Redundância

### **Como Funciona:**

1. **Cliente tenta Servidor 1** (Principal)
2. **Se falhar** → Tenta Servidor 2 (Backup 1)
3. **Se falhar** → Tenta Servidor 3 (Backup 2)
4. **Se todos falharem** → Usa modo offline (token salvo)

### **Vantagens:**

- ✅ **Alta Disponibilidade**: Sistema sempre online
- ✅ **Resiliência**: Continua funcionando mesmo com falhas
- ✅ **Distribuição**: Reduz carga em um único servidor
- ✅ **Offline**: Funciona mesmo se todos os servidores estiverem offline

---

## 🚀 Opções de Hospedagem Gratuita

### **1. Railway.app** ⭐ MELHOR OPÇÃO
- **Gratuito**: $5 crédito/mês
- **Fácil**: Deploy automático do GitHub
- **URL**: `https://seu-projeto.railway.app`
- **Limite**: ~500 horas/mês grátis

### **2. Render.com**
- **Gratuito**: Plano free tier
- **URL**: `https://seu-projeto.onrender.com`
- **Limite**: Pode "dormir" após 15min inativo

### **3. Fly.io**
- **Gratuito**: 3 VMs compartilhadas
- **URL**: `https://seu-projeto.fly.dev`
- **Limite**: 3 apps grátis

### **4. PythonAnywhere**
- **Gratuito**: Plano Beginner
- **URL**: `https://seu-usuario.pythonanywhere.com`
- **Limite**: 1 app, 512MB

---

## 📝 Configuração no Cliente AHK

### **Arquivo: `SOLUCAO_COM_REDUNDANCIA.ahk`**

Este arquivo já está configurado com suporte a múltiplos servidores!

### **Como Configurar:**

```autohotkey
; Array de servidores (em ordem de prioridade)
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://api1.railway.app"      ; Servidor Principal
g_LicenseAPI_Servers[2] := "https://api2.onrender.com"     ; Backup 1
g_LicenseAPI_Servers[3] := "https://api3.fly.dev"          ; Backup 2
```

### **Exemplo Real:**

```autohotkey
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://protecao-api.railway.app"
g_LicenseAPI_Servers[2] := "https://protecao-api-backup.onrender.com"
g_LicenseAPI_Servers[3] := "https://protecao-api-backup2.fly.dev"
```

---

## 🔧 Deploy em Múltiplos Servidores

### **Servidor 1: Railway.app**

1. Acesse: https://railway.app
2. New Project > Deploy from GitHub
3. Selecione repositório
4. Configure variáveis de ambiente
5. Deploy automático!
6. URL: `https://seu-projeto.railway.app`

### **Servidor 2: Render.com**

1. Acesse: https://render.com
2. New > Web Service
3. Conecte GitHub
4. Selecione repositório
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd api && python app.py`
6. Deploy!
7. URL: `https://seu-projeto.onrender.com`

### **Servidor 3: Fly.io** (Opcional)

1. Instale CLI: `curl -L https://fly.io/install.sh | sh`
2. `fly launch`
3. Configure `fly.toml`
4. `fly deploy`
5. URL: `https://seu-projeto.fly.dev`

---

## 📊 Sincronização de Banco de Dados

### **Problema:**

Cada servidor terá seu próprio banco SQLite. As licenças precisam estar sincronizadas.

### **Soluções:**

#### **Opção 1: Banco Compartilhado (Recomendado)**

Use um banco na nuvem:
- **Supabase** (PostgreSQL grátis)
- **PlanetScale** (MySQL grátis)
- **Railway PostgreSQL** (grátis com crédito)

#### **Opção 2: Sincronização Manual**

1. Exporte banco do servidor principal
2. Importe nos servidores backup
3. Faça periodicamente (diário/semanal)

#### **Opção 3: API de Sincronização**

Crie endpoint que sincroniza bancos entre servidores.

---

## 🎯 Configuração Recomendada

### **Setup Inicial:**

1. **Servidor Principal**: Railway.app
   - Mais confiável
   - Sempre online
   - URL: `https://api1.railway.app`

2. **Servidor Backup**: Render.com
   - Backup automático
   - URL: `https://api2.onrender.com`

3. **Cliente AHK**: Usa ambos
   - Tenta Railway primeiro
   - Se falhar, tenta Render
   - Se ambos falharem, usa offline

---

## 📝 Arquivos Necessários para Deploy

### **requirements.txt** (já criado)
```
Flask==3.0.0
flask-cors==4.0.0
werkzeug==3.0.1
APScheduler==3.10.4
```

### **Procfile** (já criado)
```
web: cd api && python app.py
```

### **runtime.txt** (já criado)
```
python-3.11.0
```

---

## ⚙️ Variáveis de Ambiente

Configure estas variáveis em cada servidor:

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
```

---

## 🧪 Testar Redundância

### **Teste 1: Servidor Principal Online**
- Deve funcionar normalmente
- Log: `license_server_used.txt` mostra servidor 1

### **Teste 2: Servidor Principal Offline**
- Deve tentar backup automaticamente
- Log: `license_server_failover.txt` mostra tentativa de backup
- Deve funcionar com backup

### **Teste 3: Todos Offline**
- Deve usar modo offline
- Log: `license_offline_success.txt` mostra modo offline ativado

---

## 📊 Logs de Debug

Os seguintes arquivos são criados em `%TEMP%`:

- `license_server_used.txt` - Qual servidor foi usado
- `license_server_failover.txt` - Quando tenta próximo servidor
- `license_offline_success.txt` - Quando modo offline é ativado

---

## ✅ Checklist de Implementação

- [ ] Deploy no Railway (Servidor 1)
- [ ] Deploy no Render (Servidor 2)
- [ ] Testar URLs de ambos servidores
- [ ] Configurar cliente AHK com array de servidores
- [ ] Testar redundância (desligar servidor 1)
- [ ] Verificar logs de failover
- [ ] Configurar sincronização de banco (se necessário)

---

## 🎯 Próximos Passos

1. **Escolha 2-3 serviços** de hospedagem
2. **Faça deploy** em cada um
3. **Configure cliente AHK** com URLs de todos
4. **Teste redundância** desligando servidores
5. **Monitore logs** para verificar funcionamento

---

**Documento criado em**: 2024-12-15

