# Sistema de Licenciamento - API

Sistema completo de licenciamento com dashboard web moderno, API Flask e clientes em C# e AutoHotkey.

## 🚀 Novidades - Sistema de Servidores Dinâmicos

**✨ Atualize servidores para 30k+ clientes sem recompilar o executável!**

- ✅ **Atualização automática**: Clientes baixam lista de servidores dinamicamente
- ✅ **Cache inteligente**: Reduz carga no servidor e melhora performance
- ✅ **Redundância automática**: Múltiplos servidores com failover
- ✅ **Zero downtime**: Atualize servidores sem interrupção

📖 **Documentação completa**: Veja `docs/SISTEMA_SERVIDORES_DINAMICOS.md`

## 📋 Índice

1. [Requisitos](#-requisitos)
2. [Instalação Rápida](#-instalação-rápida)
3. [Sistema de Servidores Dinâmicos](#-sistema-de-servidores-dinâmicos)
4. [Configuração Detalhada](#️-configuração-detalhada)
5. [Como Rodar o Dashboard](#-como-rodar-o-dashboard)
6. [Estrutura do Projeto](#-estrutura-do-projeto)
7. [Troubleshooting](#-troubleshooting)

---

## 🛠 Requisitos

### Para o Backend (API Flask)

* **Python 3.11+** ([Download](https://www.python.org/downloads/))
* **pip** (geralmente vem com Python)

### Para o Frontend (Dashboard)

* **Node.js 18+** e **npm** ([Download](https://nodejs.org/)) - Opcional
* Ou use a versão já compilada (não precisa de Node.js)

### Para Deploy em Produção

* **Cloudflare Tunnel** (para expor a API)
* **Firebase Hosting** (para o dashboard) - opcional

---

## 🚀 Instalação Rápida

### 1. Clone/Baixe o Projeto

```bash
# Se usar Git
git clone https://github.com/eudesnoberto/licence-api.git protecao
cd protecao

# Ou extraia o ZIP do projeto na pasta desejada
```

### 2. Configurar Backend (API Flask)

```bash
# Entre na pasta da API
cd api

# Crie um ambiente virtual (recomendado)
python -m venv .venv

# Ative o ambiente virtual
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Crie um arquivo .env (opcional)
# Windows PowerShell:
@"
API_KEY=seu_api_key_aqui
SHARED_SECRET=seu_secret_aqui
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
ALLOW_AUTO_PROVISION=false
"@ | Out-File -Encoding utf8 .env

# Inicie o servidor
python app.py
```

O servidor estará rodando em `http://localhost:5000`

### 3. Configurar Frontend (Dashboard)

#### Opção A: Desenvolvimento (com Node.js)

```bash
# Entre na pasta do frontend
cd frontend

# Instale as dependências
npm install

# Crie o arquivo .env para desenvolvimento
# Windows PowerShell:
@"
VITE_API_BASE_URL=http://127.0.0.1:5000
"@ | Out-File -Encoding utf8 .env

# Inicie o servidor de desenvolvimento
npm run dev
```

O dashboard estará em `http://localhost:5173`

#### Opção B: Produção (já compilado)

Se você já tem a pasta `frontend/dist` compilada:

```bash
# Com Python (servidor simples)
cd frontend/dist
python -m http.server 8000

# Ou use o Vite preview
cd frontend
npm run preview
```

---

## 🔄 Sistema de Servidores Dinâmicos

### Como Funciona

O sistema permite atualizar a lista de servidores para **30k+ clientes** sem necessidade de recompilar o executável.

1. **Cliente baixa lista** do endpoint `/servers`
2. **Cache local** (válido por 1 hora)
3. **Atualização automática** a cada 24 horas
4. **Fallback** para servidores hardcoded se falhar

### Como Alterar Servidores

**Arquivo: `api/config.py` (linhas 108-112)**

```python
LICENSE_SERVERS = [
    "https://api.epr.app.br",                    # Servidor Principal
    "https://licence-api-6evg.onrender.com",     # Backup 1
    "https://api-epr.rj.r.appspot.com",          # Backup 2
]
```

**Passos:**
1. Edite `api/config.py`
2. Reinicie a API
3. ✅ Clientes atualizarão automaticamente nas próximas 24 horas

📖 **Guia completo**: Veja `docs/COMO_ALTERAR_SERVIDORES.md`

### Endpoint `/servers`

```bash
curl https://api.epr.app.br/servers
```

Resposta:
```json
{
  "version": 1,
  "timestamp": 20260110220000,
  "servers": [
    "https://api.epr.app.br",
    "https://licence-api-6evg.onrender.com",
    "https://api-epr.rj.r.appspot.com"
  ]
}
```

---

## ⚙️ Configuração Detalhada

### Variáveis de Ambiente do Backend

Crie um arquivo `.env` na pasta `api/`:

```env
# Segurança
API_KEY=seu_api_key_secreto_aqui
SHARED_SECRET=seu_shared_secret_aqui
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
MAX_TIME_SKEW=300

# Auto-provisionamento
ALLOW_AUTO_PROVISION=false

# Admin padrão (mude no primeiro acesso)
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123

# Lista de servidores (opcional, sobrescreve config.py)
LICENSE_SERVERS=https://api.epr.app.br,https://backup1.com,https://backup2.com
```

### Variáveis de Ambiente do Frontend

#### Desenvolvimento (`frontend/.env`):

```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

#### Produção (`frontend/.env.production`):

```env
VITE_API_BASE_URL=https://api.epr.app.br
```

---

## 🖥 Como Rodar o Dashboard

### Modo Desenvolvimento (Local)

1. **Inicie o backend:**
   ```bash
   cd api
   python app.py
   ```
   Deixe rodando em um terminal.

2. **Inicie o frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Acesse:** `http://localhost:5173`

4. **Login padrão:**
   - Usuário: `admin`
   - Senha: `admin123`
   - **Importante:** No primeiro acesso, você será obrigado a trocar a senha.

### Modo Produção (Deploy)

#### Opção 1: Firebase Hosting (Recomendado)

```bash
# 1. Compile o frontend
cd frontend
npm run build

# 2. Faça deploy
cd ..
firebase deploy --only hosting
```

#### Opção 2: Servidor Web Local

```bash
# Compile o frontend
cd frontend
npm run build

# Sirva a pasta dist
cd dist
python -m http.server 8000
```

Acesse: `http://localhost:8000`

---

## 📁 Estrutura do Projeto

```
protecao/
├── api/                           # Backend Flask
│   ├── app.py                     # Aplicação principal
│   ├── config.py                  # Configurações (inclui LICENSE_SERVERS)
│   ├── db.py                      # Banco de dados SQLite
│   ├── license_service.py         # Lógica de licenças
│   ├── requirements.txt           # Dependências Python
│   ├── license.db                 # Banco SQLite (criado automaticamente)
│   └── .env                       # Variáveis de ambiente
│
├── frontend/                       # Dashboard React
│   ├── src/
│   │   ├── main.ts                # Código principal
│   │   └── style.css              # Estilos
│   ├── dist/                      # Build de produção
│   ├── package.json               # Dependências Node
│   └── .env                       # Config dev
│
├── ahk-client/                     # Cliente AutoHotkey
│   └── SOLUCAO_COM_REDUNDANCIA.ahk # Cliente com servidores dinâmicos
│
├── cs-client/                     # Cliente C# (exemplo)
│   └── Program.cs
│
├── docs/                          # Documentação
│   ├── install.md
│   ├── api.md
│   ├── SISTEMA_SERVIDORES_DINAMICOS.md
│   └── COMO_ALTERAR_SERVIDORES.md
│
├── firebase.json                   # Config Firebase
├── .firebaserc                    # Projeto Firebase
└── README.md                      # Este arquivo
```

---

## 🔧 Troubleshooting

### Erro: "Python não foi encontrado"

* Instale Python 3.11+ e marque "Add Python to PATH" durante a instalação
* Reinicie o terminal após instalar

### Erro: "ModuleNotFoundError: No module named 'flask'"

* Ative o ambiente virtual: `.venv\Scripts\Activate.ps1`
* Instale as dependências: `pip install -r requirements.txt`

### Erro: "VITE_API_BASE_URL não configurada"

* Crie o arquivo `frontend/.env` com: `VITE_API_BASE_URL=http://127.0.0.1:5000`
* Reinicie o servidor Vite

### Erro: "CORS policy" no navegador

* Verifique se a URL da API no `.env` do frontend está correta
* Verifique se o backend está rodando
* No `api/app.py`, verifique se o domínio está na lista de CORS permitidos

### Clientes não atualizam servidores

* Verifique se o endpoint `/servers` está acessível: `curl https://api.epr.app.br/servers`
* Limpe o cache: delete `%AppData%\LicenseSystem\servers_cache.json`
* Verifique logs: `%Temp%\license_config_log.txt`

### Dashboard não carrega licenças

* Verifique se está logado (token no localStorage)
* Verifique se o backend está rodando
* Abra o Console do navegador (F12) para ver erros

---

## 📚 Documentação Adicional

* `docs/install.md` - Guia detalhado de instalação
* `docs/api.md` - Documentação da API
* `docs/SISTEMA_SERVIDORES_DINAMICOS.md` - Sistema de servidores dinâmicos
* `docs/COMO_ALTERAR_SERVIDORES.md` - Como alterar servidores

---

## 🎯 Principais Funcionalidades

✅ **Sistema de Licenciamento Completo**
- Dashboard web moderno
- API RESTful com Flask
- Suporte a múltiplos tipos de licença
- Detecção de clones (anti-pirataria)

✅ **Sistema de Servidores Dinâmicos**
- Atualização automática de servidores
- Redundância com failover automático
- Cache inteligente
- Suporte a 30k+ clientes

✅ **Clientes Multiplataforma**
- AutoHotkey (Windows)
- C# (.NET)
- Fácil integração

✅ **Segurança**
- Assinatura criptográfica (SHA-256)
- API Key authentication
- Detecção de uso simultâneo
- Modo offline com período de graça

---

## 📞 Suporte

Para mais informações, consulte a documentação em `docs/` ou abra uma issue no GitHub.

---

**Desenvolvido com ❤️ para gerenciamento de licenças**

**Repositório**: [https://github.com/eudesnoberto/licence-api](https://github.com/eudesnoberto/licence-api)
