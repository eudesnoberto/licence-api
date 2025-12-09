# 🔧 Configurar MySQL Remoto no Servidor Local

## ❌ Problema

O servidor local não está conectando ao MySQL remoto e está usando SQLite local.

## ✅ Solução

### **Passo 1: Criar arquivo `.env` na pasta `api/`**

1. Navegue até a pasta `api/`:
   ```powershell
   cd C:\protecao\api
   ```

2. Crie o arquivo `.env` (se não existir):
   ```powershell
   # Copie o template
   Copy-Item ..\env.example .env
   ```

3. Edite o arquivo `.env` e configure:

```env
# Tipo de banco: "mysql" (IMPORTANTE!)
DB_TYPE=mysql

# Configuração MySQL (HostGator)
MYSQL_HOST=108.179.252.54
MYSQL_PORT=3306
MYSQL_DATABASE=scpmtc84_api
MYSQL_USER=scpmtc84_api
MYSQL_PASSWORD=nQT-8gW%-qCY

# API Keys (configure suas credenciais)
API_KEY=SUA_API_KEY_AQUI
SHARED_SECRET=SEU_SHARED_SECRET_AQUI
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true

# Admin padrão
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123
```

### **Passo 2: Verificar se pymysql está instalado**

```powershell
cd C:\protecao\api
pip install pymysql
```

Ou instale todas as dependências:
```powershell
pip install -r requirements.txt
```

### **Passo 3: Reiniciar o servidor**

1. Pare o servidor atual (Ctrl+C)
2. Inicie novamente:
   ```powershell
   cd C:\protecao\api
   python app.py
   ```

### **Passo 4: Verificar conexão**

Nos logs, você deve ver:
- ✅ Sem aviso sobre "pymysql não instalado"
- ✅ Sem aviso sobre "SQLite"
- ✅ Conexão estabelecida com MySQL

---

## 🔍 Verificar Configuração Atual

Execute este comando para verificar:

```powershell
cd C:\protecao\api
if (Test-Path .env) {
    Write-Host "✅ Arquivo .env existe" -ForegroundColor Green
    Write-Host ""
    Write-Host "Conteúdo:" -ForegroundColor Cyan
    Get-Content .env | Select-String -Pattern "DB_TYPE|MYSQL"
} else {
    Write-Host "❌ Arquivo .env NÃO existe" -ForegroundColor Red
    Write-Host ""
    Write-Host "Crie o arquivo .env com:" -ForegroundColor Yellow
    Write-Host "DB_TYPE=mysql" -ForegroundColor Gray
    Write-Host "MYSQL_HOST=108.179.252.54" -ForegroundColor Gray
    Write-Host "MYSQL_PORT=3306" -ForegroundColor Gray
    Write-Host "MYSQL_DATABASE=scpmtc84_api" -ForegroundColor Gray
    Write-Host "MYSQL_USER=scpmtc84_api" -ForegroundColor Gray
    Write-Host "MYSQL_PASSWORD=nQT-8gW%-qCY" -ForegroundColor Gray
}
```

---

## ⚠️ Importante

1. **O arquivo `.env` deve estar em `api/.env`** (não na raiz)
2. **`DB_TYPE=mysql`** é obrigatório
3. **Todas as variáveis MySQL** devem estar preenchidas
4. **pymysql deve estar instalado**: `pip install pymysql`

---

## 🧪 Testar Conexão MySQL

Após configurar, teste a conexão:

```powershell
cd C:\protecao
python testar_mysql.py
```

Deve retornar:
- ✅ Conexão estabelecida
- ✅ Versão MySQL
- ✅ Tabelas listadas

---

## 📋 Checklist

- [ ] Arquivo `api/.env` criado
- [ ] `DB_TYPE=mysql` configurado
- [ ] Todas as variáveis MySQL preenchidas
- [ ] `pymysql` instalado (`pip install pymysql`)
- [ ] Servidor reiniciado
- [ ] Logs mostram conexão MySQL (sem avisos)

---

**Após configurar, o servidor local usará o MySQL remoto!** 🚀

