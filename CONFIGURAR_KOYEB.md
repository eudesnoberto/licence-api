# 🚀 Configurar Servidor no Koyeb

## 📋 Passo a Passo Completo

### **1. Criar Novo App no Koyeb**

1. Acesse: https://app.koyeb.com
2. Faça login na sua conta
3. Clique em **"Create App"** ou **"New App"**

---

### **2. Conectar ao Repositório GitHub**

1. Na tela de criação, selecione **"GitHub"**
2. Autorize o Koyeb a acessar seu GitHub (se necessário)
3. Selecione o repositório: `eudesnoberto/licence-api`
4. Branch: `main`

---

### **3. Configurações Básicas**

#### **App Name:**
- **Name**: `licence-api` (ou o nome que preferir)

#### **Region:**
- Escolha a região mais próxima (ex: `fra` - Frankfurt, `iad` - Washington DC)

#### **Build & Run Settings:**

**Build Command:**
```bash
pip install -r api/requirements.txt
```

**Run Command:**
```bash
cd api && python app.py
```

**OU** (se o Koyeb não encontrar o diretório):
```bash
python api/app.py
```

---

### **4. Variáveis de Ambiente** ⚠️ **OBRIGATÓRIO**

⚠️ **IMPORTANTE**: As variáveis do `koyeb.toml` **NÃO são aplicadas automaticamente**. Você **DEVE** adicioná-las manualmente no dashboard!

1. No dashboard do Koyeb, vá em **"Settings"** → **"Environment"** (ou **"Environment Variables"**)
2. Clique em **"Add Environment Variable"** (ou **"+"**)
3. Adicione **uma por uma** as seguintes variáveis:

   | Key | Value |
   |-----|-------|
   | `DB_TYPE` | `mysql` |
   | `MYSQL_HOST` | `108.179.252.54` |
   | `MYSQL_PORT` | `3306` |
   | `MYSQL_DATABASE` | `scpmtc84_api` |
   | `MYSQL_USER` | `scpmtc84_api` |
   | `MYSQL_PASSWORD` | `nQT-8gW%-qCY` |

4. Clique em **"Save"** após cada variável

**Total: 6 variáveis de ambiente**

📖 **Guia detalhado**: Veja `ADICIONAR_VARIAVEIS_KOYEB.md` para instruções passo a passo com screenshots.

---

### **5. Configurações Avanções (Opcional)**

#### **Instance Type:**
- **Free Tier**: `Starter` (512MB RAM)
- Se precisar de mais recursos, pode escolher planos pagos

#### **Auto-Deploy:**
- ✅ **Auto-Deploy**: Habilitado (deploy automático a cada push)

#### **Health Check:**
- **Health Check Path**: `/health` (opcional, mas recomendado)

---

### **6. Deploy**

1. Clique em **"Deploy"** ou **"Create App"**
2. O Koyeb começará a fazer build automaticamente
3. Aguarde o deploy completar (pode levar 2-5 minutos)
4. Verifique os logs para confirmar que está funcionando

---

## 🔍 Verificar Estrutura do Projeto

O projeto tem a seguinte estrutura:

```
licence-api/
├── api/
│   ├── app.py          ← Arquivo principal
│   ├── requirements.txt ← Dependências
│   ├── config.py
│   ├── db.py
│   └── ...
├── frontend/
├── koyeb.toml         ← Configuração Koyeb (se usar)
└── README.md
```

**Importante**: O arquivo `app.py` está dentro da pasta `api/`, por isso o comando precisa ser `cd api && python app.py`

---

## ⚠️ Se o Erro "No such file or directory" Persistir

### **Solução 1: Usar caminho relativo**

Mude o **Run Command** para:

```bash
python api/app.py
```

### **Solução 2: Verificar Root Directory**

1. Vá em **Settings** → **General**
2. Verifique o campo **Root Directory**
3. Deve estar **vazio** (raiz do repositório)
4. Se estiver preenchido, limpe e salve

### **Solução 3: Usar koyeb.toml**

Crie um arquivo `koyeb.toml` na raiz do projeto:

```toml
[build]
builder = "nixpacks"

[run]
command = "cd api && python app.py"
```

---

## ✅ Checklist de Configuração

- [ ] Repositório: `eudesnoberto/licence-api`
- [ ] Branch: `main`
- [ ] Build Command: `pip install -r api/requirements.txt`
- [ ] Run Command: `cd api && python app.py` (ou `python api/app.py`)
- [ ] Variáveis de ambiente MySQL configuradas (6 variáveis)
- [ ] Auto-Deploy habilitado

---

## 🧪 Testar Após Deploy

Após o deploy completar, teste os endpoints:

```bash
# Health check
curl https://seu-app.koyeb.app/health

# Ping
curl https://seu-app.koyeb.app/ping

# Login (teste)
curl -X POST https://seu-app.koyeb.app/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 📝 Notas Importantes

1. **Primeiro deploy pode demorar** - O Koyeb precisa instalar todas as dependências
2. **URL será gerada automaticamente** - Formato: `seu-app.koyeb.app`
3. **Logs são importantes** - Sempre verifique os logs se houver problemas
4. **Koyeb não "dorme"** - Diferente do Render, o Koyeb free tier não desliga após inatividade

---

## 🔄 Atualizar URL Após Deploy

Após o deploy, você receberá uma URL como:
```
https://seu-app.koyeb.app
```

**Atualize nos seguintes lugares:**

1. **Frontend** (`frontend/src/main.ts`):
   - Adicione a URL ao array de servidores

2. **AHK Script** (`SOLUCAO_COM_REDUNDANCIA.ahk`):
   - Adicione a URL ao array `g_LicenseAPI_Servers`

3. **Script de Verificação** (`VERIFICAR_SERVIDORES.ps1`):
   - Adicione a URL ao array de servidores

---

## 🎯 Vantagens do Koyeb

- ✅ **Não "dorme"** - Servidor sempre ativo (diferente do Render)
- ✅ **Deploy rápido** - Geralmente mais rápido que Render
- ✅ **Logs em tempo real** - Fácil de debugar
- ✅ **Free tier generoso** - 512MB RAM, suficiente para a API

---

**Pronto!** Após configurar tudo, o Koyeb fará o deploy automaticamente. 🚀

