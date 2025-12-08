# 🚀 Guia Rápido - Como Rodar o Dashboard

## ⚡ Início Rápido (5 minutos)

### 1. Backend (API Flask)

```powershell
# Entre na pasta
cd C:\protecao\api

# Crie e ative ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instale dependências
pip install -r requirements.txt

# Inicie o servidor
python app.py
```

✅ **Servidor rodando em:** `http://localhost:5000`

---

### 2. Frontend (Dashboard)

**Opção A - Desenvolvimento (com Node.js):**

```powershell
# Em outro terminal
cd C:\protecao\frontend

# Instale dependências (só na primeira vez)
npm install

# Crie arquivo .env
"VITE_API_BASE_URL=http://127.0.0.1:5000" | Out-File -Encoding utf8 .env

# Inicie o servidor
npm run dev
```

✅ **Dashboard em:** `http://localhost:5173`

**Opção B - Produção (já compilado):**

```powershell
cd C:\protecao\frontend\dist
python -m http.server 8000
```

✅ **Dashboard em:** `http://localhost:8000`

---

### 3. Acessar o Dashboard

1. Abra o navegador: `http://localhost:5173`
2. **Login:**
   - Usuário: `admin`
   - Senha: `admin123`
3. **Primeiro acesso:** Você será obrigado a trocar a senha
4. Pronto! Você está no dashboard.

---

## 📋 Checklist para Outro PC

- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ instalado (se for desenvolver)
- [ ] Projeto copiado para o novo PC
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Backend rodando (`python app.py`)
- [ ] Frontend rodando (`npm run dev`)
- [ ] Arquivo `.env` criado no frontend com URL correta

---

## 🔧 Comandos Úteis

### Compilar Frontend para Produção
```powershell
cd frontend
npm run build
```

### Verificar se o backend está rodando
```powershell
curl http://localhost:5000/health
# Ou abra no navegador: http://localhost:5000/health
```

### Resetar banco de dados
```powershell
# Pare o servidor Flask
# Delete o arquivo:
Remove-Item api\license.db
# Reinicie o servidor (o banco será recriado)
```

---

## ❓ Problemas Comuns

| Problema | Solução |
|----------|---------|
| `Python não encontrado` | Instale Python e marque "Add to PATH" |
| `pip não encontrado` | Ative o ambiente virtual primeiro |
| `ModuleNotFoundError` | Execute `pip install -r requirements.txt` |
| Dashboard não carrega | Verifique se o backend está rodando |
| CORS error | Verifique o `.env` do frontend |

---

**Dúvidas?** Consulte o `README.md` completo.





