# 🚀 Passo a Passo: GitHub → Render.com

## ✅ Resposta Rápida

**SIM**, você precisa subir os arquivos para o GitHub antes de fazer deploy no Render.

O Render conecta com seu repositório GitHub e faz deploy automático.

---

## 📤 PARTE 1: Subir Arquivos para GitHub

### **Seu Repositório:**
https://github.com/eudesnoberto/licence-api.git

### **Opção 1: Via Git Command Line (Recomendado)**

Abra PowerShell ou CMD na pasta `C:\protecao` e execute:

```bash
# 1. Inicialize Git (se ainda não foi feito)
git init

# 2. Adicione o repositório remoto
git remote add origin https://github.com/eudesnoberto/licence-api.git

# 3. Adicione todos os arquivos
git add .

# 4. Faça commit
git commit -m "Initial commit - API de licenciamento"

# 5. Crie branch main (se necessário)
git branch -M main

# 6. Envie para GitHub
git push -u origin main
```

**Se pedir usuário/senha:**
- Use um **Personal Access Token** do GitHub (não a senha)
- Como criar: GitHub → Settings → Developer settings → Personal access tokens → Generate new token

### **Opção 2: Via GitHub Desktop**

1. Baixe: https://desktop.github.com
2. Instale e abra
3. File → Add Local Repository
4. Selecione: `C:\protecao`
5. Commit: "Initial commit"
6. Publish repository
7. Escolha: `eudesnoberto/licence-api`

### **Opção 3: Via Interface Web do GitHub**

1. Acesse: https://github.com/eudesnoberto/licence-api
2. Clique em **"uploading an existing file"**
3. Arraste os arquivos necessários (veja lista abaixo)
4. Commit

---

## 📁 Arquivos que DEVEM estar no GitHub

### **✅ OBRIGATÓRIOS:**

```
licence-api/
├── api/
│   ├── app.py              ← OBRIGATÓRIO
│   ├── config.py           ← OBRIGATÓRIO
│   ├── db.py               ← OBRIGATÓRIO
│   ├── license_service.py  ← OBRIGATÓRIO
│   ├── email_service.py    ← OBRIGATÓRIO
│   └── requirements.txt    ← OBRIGATÓRIO
│
├── requirements.txt        ← OBRIGATÓRIO (raiz)
├── Procfile                ← OBRIGATÓRIO
├── runtime.txt             ← OPCIONAL
└── .gitignore              ← RECOMENDADO
```

### **❌ NÃO SUBIR:**

- `*.db` - Banco de dados (será criado no servidor)
- `__pycache__/` - Cache Python
- `.env` - Variáveis de ambiente
- `frontend/` - Frontend não precisa (se usar Cloudflare)
- `node_modules/` - Dependências Node.js
- `ahk-client/` - Clientes AHK (opcional)

---

## 🚀 PARTE 2: Deploy no Render.com

### **Passo 1: Criar Conta no Render**

1. Acesse: https://render.com
2. Clique em **"Get Started for Free"**
3. Escolha **"Sign up with GitHub"**
4. Autorize acesso aos repositórios

### **Passo 2: Criar Web Service**

1. No dashboard, clique em **"New +"**
2. Selecione **"Web Service"**
3. Selecione repositório: **`eudesnoberto/licence-api`**
4. Clique em **"Connect"**

### **Passo 3: Configurar**

Preencha:

- **Name**: `licence-api` (ou qualquer nome)
- **Region**: `Oregon (US West)` (ou mais próximo de você)
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

No Render, vá em **"Environment"** e adicione:

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

**⚠️ IMPORTANTE**: 
- Render usa porta **10000** por padrão (não 5000)
- O `app.py` já está configurado para ler `PORT` do ambiente

### **Passo 5: Deploy**

1. Clique em **"Create Web Service"**
2. Render começará build e deploy
3. Aguarde 3-5 minutos
4. URL será: `https://licence-api.onrender.com` (ou nome que você escolheu)

---

## ✅ Verificar se Funcionou

### **1. Verificar GitHub:**

Acesse: https://github.com/eudesnoberto/licence-api

Deve ver:
- ✅ Pasta `api/` com arquivos Python
- ✅ `requirements.txt` na raiz
- ✅ `Procfile` na raiz

### **2. Verificar Render:**

1. Acesse dashboard do Render
2. Clique no seu serviço
3. Vá em **"Logs"**
4. Deve ver: "Running on http://0.0.0.0:10000"

### **3. Testar API:**

Acesse no navegador:
```
https://licence-api.onrender.com/health
```

Deve retornar:
```json
{"status": "ok"}
```

---

## 🔄 Atualizações Futuras

Quando fizer mudanças no código:

```bash
cd C:\protecao
git add .
git commit -m "Descrição da mudança"
git push origin main
```

O Render detecta automaticamente e faz redeploy! 🎉

---

## ⚠️ Limitações do Render Free

- **"Dorme" após 15 minutos** de inatividade
- **Primeira requisição** após dormir demora ~30 segundos
- **Limite**: 750 horas/mês grátis
- **Solução**: Use como **backup**, não como principal

---

## 🎯 Estrutura Final no GitHub

```
licence-api/
├── .gitignore
├── README.md
├── requirements.txt
├── Procfile
├── runtime.txt
└── api/
    ├── app.py
    ├── config.py
    ├── db.py
    ├── license_service.py
    ├── email_service.py
    └── requirements.txt
```

---

## 📋 Checklist Completo

### **GitHub:**
- [ ] Repositório criado: https://github.com/eudesnoberto/licence-api
- [ ] Git inicializado na pasta `C:\protecao`
- [ ] Arquivos adicionados e commitados
- [ ] Push realizado para GitHub
- [ ] Arquivos visíveis no GitHub

### **Render:**
- [ ] Conta criada no Render
- [ ] GitHub conectado
- [ ] Web Service criado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado
- [ ] API testada (endpoint /health)
- [ ] URL obtida

### **Cliente AHK:**
- [ ] URL do Render adicionada ao array de servidores
- [ ] Testado com servidor principal offline

---

## 🐛 Problemas Comuns

### **"Repository not found"**
- Verifique se o repositório existe
- Verifique se você tem permissão
- Verifique se o nome está correto

### **"Build failed"**
- Verifique se `requirements.txt` está correto
- Verifique logs no Render
- Verifique se Python 3 está selecionado

### **"Port already in use"**
- Render usa variável `PORT` automaticamente
- Não precisa especificar no código
- Verifique se `app.py` lê `os.environ.get("PORT")`

### **"Module not found"**
- Verifique se todas as dependências estão em `requirements.txt`
- Verifique se build command está correto

---

## 🎯 Próximos Passos

1. ✅ Subir arquivos para GitHub
2. ✅ Fazer deploy no Render
3. ✅ Obter URL do Render
4. ✅ Configurar cliente AHK com redundância
5. ✅ Testar sistema completo

---

**Tudo pronto!** Agora você pode hospedar gratuitamente e ter redundância! 🚀

