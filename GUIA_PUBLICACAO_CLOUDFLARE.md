# 🚀 Guia Completo de Publicação no Cloudflare

Este guia mostra como publicar o sistema completo (frontend + backend) no Cloudflare.

## 📋 Pré-requisitos

1. **Conta no Cloudflare** (gratuita)
2. **Domínio configurado no Cloudflare** (`fartgreen.fun`)
3. **Cloudflare Tunnel instalado** (para o backend)
4. **Node.js instalado** (para compilar o frontend)

---

## 🎨 Parte 1: Publicar Frontend (Cloudflare Pages)

### Passo 1: Compilar o Frontend

```powershell
# Entre na pasta do frontend
cd C:\protecao\frontend

# Instale as dependências (se ainda não instalou)
npm install

# Compile para produção
npm run build
```

Isso criará a pasta `dist/` com os arquivos compilados.

### Passo 2: Configurar Variáveis de Ambiente

Crie um arquivo `.env.production` na pasta `frontend/`:

```env
VITE_API_BASE_URL=https://api.fartgreen.fun
```

**Importante:** Recompile após criar o `.env.production`:

```powershell
npm run build
```

### Passo 3: Publicar no Cloudflare Pages

#### Opção A: Via Interface Web (Recomendado)

1. **Acesse o Cloudflare Dashboard:**
   - Vá para: https://dash.cloudflare.com
   - Selecione seu domínio (`fartgreen.fun`)

2. **Acesse Cloudflare Pages:**
   - No menu lateral, clique em **"Pages"**
   - Clique em **"Create a project"**

3. **Conecte seu repositório (ou faça upload direto):**
   - Se usar Git: Conecte seu repositório GitHub/GitLab
   - Se não usar Git: Clique em **"Upload assets"** e faça upload da pasta `frontend/dist/`

4. **Configure o Build:**
   - **Project name:** `fartgreen-dashboard` (ou o nome que preferir)
   - **Production branch:** `main` (ou sua branch principal)
   - **Build command:** `npm run build` (se usar Git)
   - **Build output directory:** `dist`
   - **Root directory:** `frontend` (se o projeto estiver na raiz)

5. **Variáveis de Ambiente:**
   - Clique em **"Environment variables"**
   - Adicione:
     ```
     VITE_API_BASE_URL = https://api.fartgreen.fun
     ```

6. **Domínio Customizado:**
   - Vá em **"Custom domains"**
   - Adicione: `fartgreen.fun` e `www.fartgreen.fun`
   - O Cloudflare configurará automaticamente o DNS

#### Opção B: Via CLI (Cloudflare Wrangler)

```powershell
# Instale o Wrangler
npm install -g wrangler

# Faça login
wrangler login

# Publique
cd C:\protecao\frontend\dist
wrangler pages deploy . --project-name=fartgreen-dashboard
```

### Passo 4: Verificar Publicação

Após alguns minutos, acesse:
- https://fartgreen.fun
- https://www.fartgreen.fun

Você deve ver a **landing page** pública.

---

## 🔧 Parte 2: Publicar Backend (Cloudflare Tunnel)

### Passo 1: Instalar Cloudflare Tunnel

#### Windows (PowerShell):

```powershell
# Baixe o cloudflared
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"

# Mova para uma pasta no PATH (opcional)
Move-Item cloudflared.exe C:\Windows\System32\cloudflared.exe
```

#### Ou use Chocolatey:

```powershell
choco install cloudflared
```

### Passo 2: Fazer Login no Cloudflare

```powershell
cloudflared tunnel login
```

Isso abrirá o navegador para autenticar. Selecione seu domínio (`fartgreen.fun`).

### Passo 3: Criar um Tunnel

```powershell
# Crie um tunnel chamado "api-backend"
cloudflared tunnel create api-backend
```

Anote o **Tunnel ID** que será exibido.

### Passo 4: Configurar o Tunnel

Crie um arquivo de configuração em `%USERPROFILE%\.cloudflared\config.yml`:

```yaml
tunnel: <SEU_TUNNEL_ID>
credentials-file: C:\Users\<SEU_USUARIO>\.cloudflared\<TUNNEL_ID>.json

ingress:
  # Rota para a API
  - hostname: api.fartgreen.fun
    service: http://localhost:5000
  
  # Catch-all (deve ser o último)
  - service: http_status:404
```

**Substitua:**
- `<SEU_TUNNEL_ID>` pelo ID retornado no passo anterior
- `<SEU_USUARIO>` pelo seu usuário do Windows

### Passo 5: Configurar DNS

```powershell
# Crie o registro DNS para api.fartgreen.fun
cloudflared tunnel route dns api-backend api.fartgreen.fun
```

Ou configure manualmente no Cloudflare Dashboard:
1. Vá em **DNS** > **Records**
2. Adicione um registro **CNAME**:
   - **Name:** `api`
   - **Target:** `<TUNNEL_ID>.cfargotunnel.com`
   - **Proxy status:** Proxied (laranja)

### Passo 6: Configurar Backend para Produção

Crie/atualize o arquivo `api/.env`:

```env
# Segurança
API_KEY=seu_api_key_secreto_aqui
SHARED_SECRET=seu_shared_secret_aqui
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
MAX_TIME_SKEW=14400

# Banco de dados
DB_PATH=./license.db

# Admin padrão
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123

# Email (opcional)
SMTP_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
SMTP_FROM_EMAIL=seu_email@gmail.com
SMTP_FROM_NAME=Sistema de Licenciamento

# Clone detection
ENABLE_CLONE_DETECTION=true
MAX_SIMULTANEOUS_IPS=1
CLONE_DETECTION_WINDOW=300

# Offline mode
OFFLINE_GRACE_PERIOD_DAYS=7
```

### Passo 7: Iniciar o Backend

```powershell
# Entre na pasta da API
cd C:\protecao\api

# Ative o ambiente virtual
.\.venv\Scripts\Activate.ps1

# Inicie o servidor
python app.py
```

O backend estará rodando em `http://localhost:5000`.

### Passo 8: Iniciar o Cloudflare Tunnel

Em **outro terminal**:

```powershell
# Inicie o tunnel
cloudflared tunnel run api-backend
```

Ou para rodar em background (Windows):

```powershell
# Crie um serviço do Windows
cloudflared service install
cloudflared service start
```

### Passo 9: Verificar Backend

Teste se a API está acessível:

```powershell
# Teste o endpoint de health
Invoke-WebRequest -Uri "https://api.fartgreen.fun/health"
```

Deve retornar:
```json
{"status": "ok"}
```

---

## 🔐 Parte 3: Configurar SSL e Segurança

### SSL Automático

O Cloudflare fornece SSL automático para:
- ✅ `fartgreen.fun` (via Pages)
- ✅ `api.fartgreen.fun` (via Tunnel)

### Configurações de Segurança no Cloudflare

1. **Acesse o Dashboard do Cloudflare**
2. **Vá em SSL/TLS:**
   - Modo: **"Full (strict)"**
3. **Vá em Security:**
   - **WAF:** Ativado (recomendado)
   - **Bot Fight Mode:** Ativado (opcional)
4. **Vá em Speed:**
   - **Auto Minify:** Ativado (JavaScript, CSS, HTML)
   - **Brotli:** Ativado

---

## 🧪 Parte 4: Testar Tudo

### 1. Testar Landing Page

Acesse: https://fartgreen.fun

Deve mostrar a página inicial pública.

### 2. Testar Dashboard

Acesse: https://fartgreen.fun/#/dashboard

Deve redirecionar para login.

### 3. Testar API

```powershell
# Teste o health endpoint
Invoke-WebRequest -Uri "https://api.fartgreen.fun/health"

# Deve retornar: {"status": "ok"}
```

### 4. Testar Login

1. Acesse: https://fartgreen.fun/#/dashboard
2. Faça login com:
   - **Usuário:** `admin`
   - **Senha:** `admin123`
3. Deve entrar no dashboard

---

## 🔄 Parte 5: Manter Atualizado

### Atualizar Frontend

```powershell
cd C:\protecao\frontend
npm run build

# Se usar Git + Cloudflare Pages, faça commit e push:
git add .
git commit -m "Atualização do dashboard"
git push

# Cloudflare Pages fará deploy automaticamente
```

### Atualizar Backend

```powershell
# Pare o servidor (Ctrl+C)
# Faça suas alterações
# Reinicie:
cd C:\protecao\api
.\.venv\Scripts\Activate.ps1
python app.py
```

O Cloudflare Tunnel continuará funcionando automaticamente.

---

## 🐛 Troubleshooting

### Frontend não carrega

1. **Verifique o build:**
   ```powershell
   cd C:\protecao\frontend
   npm run build
   ```

2. **Verifique variáveis de ambiente:**
   - No Cloudflare Pages, vá em **Settings** > **Environment variables**
   - Confirme que `VITE_API_BASE_URL` está configurado

3. **Verifique o console do navegador:**
   - Pressione F12
   - Veja se há erros de CORS ou conexão

### Backend não responde

1. **Verifique se o backend está rodando:**
   ```powershell
   # Teste localmente
   Invoke-WebRequest -Uri "http://localhost:5000/health"
   ```

2. **Verifique se o Tunnel está rodando:**
   ```powershell
   cloudflared tunnel list
   ```

3. **Verifique os logs do Tunnel:**
   ```powershell
   cloudflared tunnel run api-backend --loglevel debug
   ```

4. **Verifique o DNS:**
   ```powershell
   nslookup api.fartgreen.fun
   ```

### Erro de CORS

Se aparecer erro de CORS no navegador:

1. **Verifique o arquivo `api/app.py`:**
   ```python
   CORS(
       app,
       resources={r"/*": {"origins": [
           "https://fartgreen.fun",
           "https://www.fartgreen.fun",
           "http://localhost:5173"
       ]}},
   )
   ```

2. **Adicione seu domínio se necessário**

### Erro 404 no Dashboard

Se ao acessar `https://fartgreen.fun/#/dashboard` aparecer 404:

1. **Verifique se o roteamento está funcionando:**
   - O frontend usa hash routing (`#/dashboard`)
   - Certifique-se de que o `index.html` está configurado corretamente

2. **No Cloudflare Pages, configure:**
   - **Build output directory:** `dist`
   - **Root directory:** (deixe vazio se `dist` está na raiz)

---

## 📝 Checklist Final

- [ ] Frontend compilado (`npm run build`)
- [ ] Frontend publicado no Cloudflare Pages
- [ ] Domínio `fartgreen.fun` configurado
- [ ] Variável `VITE_API_BASE_URL` configurada
- [ ] Backend rodando localmente (`python app.py`)
- [ ] Cloudflare Tunnel instalado e configurado
- [ ] Tunnel rodando (`cloudflared tunnel run`)
- [ ] DNS `api.fartgreen.fun` configurado
- [ ] SSL funcionando (verificar cadeado no navegador)
- [ ] Landing page acessível
- [ ] Dashboard acessível (com login)
- [ ] API respondendo (`/health`)

---

## 🎉 Pronto!

Seu sistema está publicado no Cloudflare! 🚀

- **Frontend:** https://fartgreen.fun
- **API:** https://api.fartgreen.fun

---

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs do Cloudflare Pages
2. Verifique os logs do Cloudflare Tunnel
3. Verifique os logs do backend Python
4. Consulte a documentação do Cloudflare

---

**Desenvolvido com ❤️ para gerenciamento de licenças**

