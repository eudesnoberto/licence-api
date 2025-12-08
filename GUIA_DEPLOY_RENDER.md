# 🚀 Guia: Deploy no Render.com (Gratuito)

## 📋 Pré-requisitos

- ✅ Conta no GitHub
- ✅ Repositório criado: https://github.com/eudesnoberto/licence-api.git
- ✅ Conta no Render.com (gratuita)
- ✅ Git instalado no seu computador

---

## 🔧 Passo 1: Preparar Arquivos para GitHub

### **Estrutura de Arquivos Necessária:**

```
licence-api/
│
├── api/
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   ├── license_service.py
│   ├── email_service.py
│   └── requirements.txt
│
├── requirements.txt (raiz)
├── Procfile
├── runtime.txt
└── README.md
```

---

## 📤 Passo 2: Subir Arquivos para GitHub

### **Opção A: Via Git Command Line**

```bash
# 1. Navegue até a pasta do projeto
cd C:\protecao

# 2. Inicialize Git (se ainda não foi feito)
git init

# 3. Adicione o repositório remoto
git remote add origin https://github.com/eudesnoberto/licence-api.git

# 4. Adicione todos os arquivos
git add .

# 5. Commit
git commit -m "Initial commit - API de licenciamento"

# 6. Push para GitHub
git push -u origin main
```

### **Opção B: Via GitHub Desktop**

1. Abra GitHub Desktop
2. File > Add Local Repository
3. Selecione pasta `C:\protecao`
4. Commit: "Initial commit"
5. Publish repository
6. Escolha: `eudesnoberto/licence-api`

### **Opção C: Via Interface Web do GitHub**

1. Acesse: https://github.com/eudesnoberto/licence-api
2. Clique em "uploading an existing file"
3. Arraste os arquivos necessários
4. Commit

---

## 🎯 Passo 3: Arquivos que DEVEM estar no GitHub

### **✅ OBRIGATÓRIOS:**

1. **`api/app.py`** - Aplicação Flask principal
2. **`api/config.py`** - Configurações
3. **`api/db.py`** - Banco de dados
4. **`api/license_service.py`** - Serviço de licenças
5. **`api/email_service.py`** - Serviço de emails
6. **`requirements.txt`** (raiz) - Dependências Python
7. **`Procfile`** - Comando de inicialização

### **✅ OPCIONAIS:**

- `runtime.txt` - Versão Python
- `README.md` - Documentação
- `.gitignore` - Arquivos a ignorar

### **❌ NÃO SUBIR:**

- `*.db` - Banco de dados (será criado no servidor)
- `__pycache__/` - Cache Python
- `.env` - Variáveis de ambiente (configure no Render)
- `frontend/` - Frontend não precisa (se usar Cloudflare Pages)

---

## 🚀 Passo 4: Deploy no Render.com

### **4.1. Criar Conta no Render**

1. Acesse: https://render.com
2. Clique em "Get Started for Free"
3. Conecte com GitHub
4. Autorize acesso aos repositórios

### **4.2. Criar Novo Web Service**

1. No dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte com GitHub (se ainda não conectou)
4. Selecione repositório: **`eudesnoberto/licence-api`**
5. Clique em **"Connect"**

### **4.3. Configurar Serviço**

Preencha os campos:

- **Name**: `licence-api` (ou qualquer nome)
- **Region**: `Oregon (US West)` (ou mais próximo)
- **Branch**: `main` (ou `master`)
- **Root Directory**: Deixe vazio (ou `api` se necessário)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  cd api && python app.py
  ```
  OU (se root directory for `api`):
  ```
  python app.py
  ```

### **4.4. Configurar Variáveis de Ambiente**

No Render, vá em **"Environment"** e adicione:

```
FLASK_ENV=production
PORT=10000
DB_PATH=/opt/render/project/src/api/license.db
API_KEY=CFEC44D0118C85FBA54A4B96C89140C6
SHARED_SECRET=BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
SMTP_ENABLED=false
ALLOW_AUTO_PROVISION=false
```

**⚠️ IMPORTANTE**: 
- `PORT=10000` (Render usa porta 10000 por padrão)
- `DB_PATH` pode variar - verifique após primeiro deploy

### **4.5. Deploy**

1. Clique em **"Create Web Service"**
2. Render começará o deploy automaticamente
3. Aguarde alguns minutos
4. URL será: `https://licence-api.onrender.com` (ou nome que você escolheu)

---

## 🔧 Passo 5: Ajustar app.py para Render

O Render usa porta dinâmica. Verifique se `app.py` está assim:

```python
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV", "development") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
```

---

## 📝 Passo 6: Verificar Deploy

### **Teste a API:**

1. Acesse: `https://seu-projeto.onrender.com/health`
2. Deve retornar: `{"status": "ok"}`

### **Se der erro:**

1. Verifique logs no Render (aba "Logs")
2. Verifique variáveis de ambiente
3. Verifique se `requirements.txt` está correto
4. Verifique se `Procfile` está correto

---

## 🔄 Passo 7: Configurar Cliente AHK

### **Com Redundância:**

```autohotkey
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://api1.railway.app"        ; Principal
g_LicenseAPI_Servers[2] := "https://licence-api.onrender.com" ; Backup Render
g_LicenseAPI_Servers[3] := "https://api3.fly.dev"           ; Backup 2
```

---

## ⚠️ Limitações do Render Free

- **"Dorme" após 15 minutos** de inatividade
- **Primeira requisição** após dormir pode demorar ~30 segundos
- **Limite**: 750 horas/mês grátis
- **Solução**: Use como backup, não como principal

---

## 🎯 Estrutura Final do Repositório GitHub

```
licence-api/
├── .gitignore
├── README.md
├── requirements.txt
├── Procfile
├── runtime.txt
└── api/
    ├── __init__.py (opcional)
    ├── app.py
    ├── config.py
    ├── db.py
    ├── license_service.py
    └── email_service.py
```

---

## 📋 Checklist

- [ ] Repositório GitHub criado
- [ ] Arquivos enviados para GitHub
- [ ] Conta Render criada
- [ ] Web Service criado no Render
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado
- [ ] API testada (endpoint /health)
- [ ] URL obtida
- [ ] Cliente AHK configurado com URL do Render

---

## 🐛 Troubleshooting

### **Erro: "Module not found"**
- Verifique se `requirements.txt` tem todas as dependências
- Verifique se build command está correto

### **Erro: "Port already in use"**
- Render usa variável `PORT` automaticamente
- Não precisa especificar porta no código

### **Erro: "Database locked"**
- SQLite pode ter problemas em ambiente compartilhado
- Considere usar PostgreSQL (Render oferece grátis)

### **App "dorme" muito**
- Render free tier "dorme" após 15min inativo
- Use como backup, não como principal
- Ou considere upgrade para plano pago

---

**Documento criado em**: 2024-12-15

