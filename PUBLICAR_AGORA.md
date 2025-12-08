# 🚀 Publicar Agora - Passo a Passo Rápido

## ✅ Frontend Compilado!

O frontend já foi compilado e está na pasta `frontend/dist/`.

---

## 📤 Passo 1: Publicar Frontend no Cloudflare Pages

### Opção A: Upload Direto (Mais Rápido)

1. **Acesse:** https://dash.cloudflare.com
2. **Vá em:** Pages (no menu lateral)
3. **Clique em:** "Create a project"
4. **Escolha:** "Upload assets"
5. **Arraste a pasta:** `C:\protecao\frontend\dist` (ou selecione os arquivos dentro dela)
6. **Project name:** `fartgreen-dashboard`
7. **Clique em:** "Deploy site"

### Opção B: Via Git (Recomendado para atualizações)

1. **Faça commit e push** do código para GitHub/GitLab
2. **No Cloudflare Pages:**
   - Clique em "Create a project"
   - Conecte seu repositório
   - Configure:
     - **Build command:** `npm run build`
     - **Build output directory:** `dist`
     - **Root directory:** `frontend`

### Configurar Variáveis de Ambiente

Após criar o projeto:

1. **Vá em:** Settings > Environment variables
2. **Adicione:**
   - **Variable name:** `VITE_API_BASE_URL`
   - **Value:** `https://api.fartgreen.fun`
   - **Environment:** Production, Preview, Branch previews
3. **Salve**

### Configurar Domínio

1. **Vá em:** Custom domains
2. **Adicione:** `fartgreen.fun`
3. **Adicione:** `www.fartgreen.fun`
4. O Cloudflare configurará o DNS automaticamente

**Aguarde 2-5 minutos** para o deploy completar.

---

## 🔧 Passo 2: Configurar Backend (Cloudflare Tunnel)

### 2.1 Instalar Cloudflare Tunnel

```powershell
# Opção 1: Via Chocolatey (recomendado)
choco install cloudflared

# Opção 2: Download manual
# Baixe de: https://github.com/cloudflare/cloudflared/releases
```

### 2.2 Fazer Login

```powershell
cloudflared tunnel login
```

Isso abrirá o navegador. Selecione seu domínio `fartgreen.fun`.

### 2.3 Criar Tunnel

```powershell
cloudflared tunnel create api-backend
```

**Anote o Tunnel ID** que será exibido (algo como: `abc123-def456-...`)

### 2.4 Configurar Tunnel

Crie/edite o arquivo: `%USERPROFILE%\.cloudflared\config.yml`

```yaml
tunnel: <SEU_TUNNEL_ID_AQUI>
credentials-file: C:\Users\<SEU_USUARIO>\.cloudflared\<TUNNEL_ID>.json

ingress:
  - hostname: api.fartgreen.fun
    service: http://localhost:5000
  - service: http_status:404
```

**Substitua:**
- `<SEU_TUNNEL_ID_AQUI>` pelo ID do passo 2.3
- `<SEU_USUARIO>` pelo seu usuário do Windows

### 2.5 Configurar DNS

```powershell
cloudflared tunnel route dns api-backend api.fartgreen.fun
```

Ou manualmente no Cloudflare Dashboard:
- **DNS** > **Records** > **Add record**
- **Type:** CNAME
- **Name:** `api`
- **Target:** `<TUNNEL_ID>.cfargotunnel.com`
- **Proxy status:** Proxied (laranja)

---

## 🚀 Passo 3: Iniciar Serviços

### Terminal 1 - Backend

```powershell
cd C:\protecao\api
.\.venv\Scripts\Activate.ps1
python app.py
```

Deixe rodando.

### Terminal 2 - Cloudflare Tunnel

```powershell
cloudflared tunnel run api-backend
```

Deixe rodando.

---

## ✅ Passo 4: Verificar

### Testar Frontend

Acesse: https://fartgreen.fun

Deve mostrar a **landing page**.

### Testar Dashboard

Acesse: https://fartgreen.fun/#/dashboard

Deve redirecionar para **login**.

### Testar API

```powershell
Invoke-WebRequest -Uri "https://api.fartgreen.fun/health"
```

Deve retornar: `{"status": "ok"}`

---

## 🎉 Pronto!

Seu sistema está publicado!

- **Frontend:** https://fartgreen.fun
- **API:** https://api.fartgreen.fun

---

## 🔄 Para Atualizar Frontend

```powershell
cd C:\protecao\frontend
npm run build
```

Depois, no Cloudflare Pages:
- Vá em seu projeto
- Clique em "Retry deployment" ou faça novo upload

---

## 🐛 Problemas?

### Frontend não carrega
- Verifique se o deploy foi concluído (aguarde alguns minutos)
- Verifique se a variável `VITE_API_BASE_URL` está configurada
- Verifique o console do navegador (F12)

### API não responde
- Verifique se o backend está rodando (`python app.py`)
- Verifique se o tunnel está rodando (`cloudflared tunnel run`)
- Verifique o DNS: `nslookup api.fartgreen.fun`

### Erro de CORS
- Verifique se `api/app.py` tem o domínio correto no CORS
- Deve incluir: `https://fartgreen.fun` e `https://www.fartgreen.fun`

---

**Precisa de ajuda? Consulte:** `GUIA_PUBLICACAO_CLOUDFLARE.md`

