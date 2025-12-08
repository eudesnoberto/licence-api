# Sistema de Licenciamento - Guia Completo

Sistema completo de licenciamento com dashboard web moderno, API Flask e clientes em C# e AutoHotkey.

## 📋 Índice

1. [Requisitos](#requisitos)
2. [Instalação Rápida](#instalação-rápida)
3. [Configuração Detalhada](#configuração-detalhada)
4. [Como Rodar o Dashboard](#como-rodar-o-dashboard)
5. [Como Usar em Outro PC](#como-usar-em-outro-pc)
6. [Estrutura do Projeto](#estrutura-do-projeto)
7. [Troubleshooting](#troubleshooting)

---

## 🛠 Requisitos

### Para o Backend (API Flask)
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **pip** (geralmente vem com Python)

### Para o Frontend (Dashboard)
- **Node.js 18+** e **npm** ([Download](https://nodejs.org/))
- Ou use a versão já compilada (não precisa de Node.js)

### Para Deploy em Produção
- **Cloudflare Tunnel** (para expor a API)
- **Firebase Hosting** (para o dashboard) - opcional, pode usar servidor local

---

## 🚀 Instalação Rápida

### 1. Clone/Baixe o Projeto

```bash
# Se usar Git
git clone <seu-repositorio> protecao
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

# Crie um arquivo .env (opcional, para personalizar)
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

Se você já tem a pasta `frontend/dist` compilada, pode servir com qualquer servidor web:

```bash
# Com Python (servidor simples)
cd frontend/dist
python -m http.server 8000

# Ou use o Vite preview
cd frontend
npm run preview
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

# Auto-provisionamento (criar licenças automaticamente)
ALLOW_AUTO_PROVISION=false

# Admin padrão (mude no primeiro acesso)
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123

# Caminho do banco de dados (opcional)
DB_PATH=./license.db
```

### Variáveis de Ambiente do Frontend

#### Desenvolvimento (`frontend/.env`):
```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

#### Produção (`frontend/.env.production`):
```env
VITE_API_BASE_URL=https://api.fartgreen.fun
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

# Sirva a pasta dist com qualquer servidor
# Exemplo com Python:
cd dist
python -m http.server 8000
```

Acesse: `http://localhost:8000`

---

## 💻 Como Usar em Outro PC

### Passo 1: Copiar o Projeto

Copie toda a pasta `protecao` para o outro PC (via USB, rede, Git, etc.)

### Passo 2: Instalar Dependências no Novo PC

#### Backend:
```bash
cd protecao/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

#### Frontend (se for desenvolver):
```bash
cd protecao/frontend
npm install
```

### Passo 3: Configurar

1. **Backend:** Ajuste o `.env` na pasta `api/` se necessário
2. **Frontend:** Ajuste o `.env` na pasta `frontend/` com a URL correta da API

### Passo 4: Rodar

```bash
# Terminal 1 - Backend
cd protecao/api
python app.py

# Terminal 2 - Frontend (desenvolvimento)
cd protecao/frontend
npm run dev
```

### Passo 5: Acessar o Dashboard

Abra o navegador em `http://localhost:5173` e faça login.

---

## 📁 Estrutura do Projeto

```
protecao/
├── api/                    # Backend Flask
│   ├── app.py              # Aplicação principal
│   ├── config.py           # Configurações
│   ├── db.py               # Banco de dados SQLite
│   ├── license_service.py  # Lógica de licenças
│   ├── requirements.txt    # Dependências Python
│   ├── license.db         # Banco SQLite (criado automaticamente)
│   └── .env               # Variáveis de ambiente (criar manualmente)
│
├── frontend/               # Dashboard React
│   ├── src/
│   │   ├── main.ts        # Código principal
│   │   └── style.css      # Estilos
│   ├── dist/              # Build de produção
│   ├── package.json       # Dependências Node
│   └── .env              # Config dev (criar manualmente)
│
├── cs-client/             # Cliente C# (exemplo)
│   └── Program.cs
│
├── docs/                  # Documentação
│   ├── install.md
│   └── api.md
│
├── firebase.json          # Config Firebase
├── .firebaserc           # Projeto Firebase
└── README.md             # Este arquivo
```

---

## 🔧 Troubleshooting

### Erro: "Python não foi encontrado"
- Instale Python 3.11+ e marque "Add Python to PATH" durante a instalação
- Reinicie o terminal após instalar

### Erro: "pip não foi encontrado"
- Certifique-se de que o ambiente virtual está ativado
- Reinstale Python com "Add Python to PATH" marcado

### Erro: "ModuleNotFoundError: No module named 'flask'"
- Ative o ambiente virtual: `.venv\Scripts\Activate.ps1`
- Instale as dependências: `pip install -r requirements.txt`

### Erro: "VITE_API_BASE_URL não configurada"
- Crie o arquivo `frontend/.env` com: `VITE_API_BASE_URL=http://127.0.0.1:5000`
- Reinicie o servidor Vite

### Erro: "CORS policy" no navegador
- Verifique se a URL da API no `.env` do frontend está correta
- Verifique se o backend está rodando
- No `api/app.py`, verifique se o domínio está na lista de CORS permitidos

### Dashboard não carrega licenças
- Verifique se está logado (token no localStorage)
- Verifique se o backend está rodando
- Abra o Console do navegador (F12) para ver erros

### Banco de dados não existe
- O banco `license.db` é criado automaticamente na primeira execução
- Se precisar resetar, delete o arquivo `api/license.db` e reinicie o servidor

### Primeiro acesso ao dashboard
- Use: `admin` / `admin123`
- Você será obrigado a trocar a senha no primeiro acesso
- A nova senha será salva no banco de dados

---

## 📝 Próximos Passos

1. **Configurar Cloudflare Tunnel** (para expor a API em produção)
2. **Configurar Firebase Hosting** (para o dashboard em produção)
3. **Criar licenças** através do dashboard
4. **Testar clientes** (C# ou AutoHotkey) conectando à API

---

## 📞 Suporte

Para mais detalhes, consulte:
- `docs/install.md` - Guia detalhado de instalação
- `docs/api.md` - Documentação da API

---

**Desenvolvido com ❤️ para gerenciamento de licenças**





