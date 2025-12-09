# 🔄 Reiniciar Servidor para Usar MySQL

## ✅ Status

- ✅ Arquivo `api/.env` configurado com MySQL
- ✅ `pymysql` instalado
- ✅ Conexão MySQL testada e funcionando
- ⚠️ **Servidor precisa ser reiniciado**

---

## 🔄 Como Reiniciar

### **Passo 1: Parar o Servidor Atual**

No terminal onde o servidor está rodando:
1. Pressione **Ctrl+C** para parar o servidor

### **Passo 2: Iniciar Novamente**

```powershell
cd C:\protecao\api
python app.py
```

---

## ✅ Verificar se Está Usando MySQL

Após reiniciar, nos logs você deve ver:

- ✅ **SEM** aviso: `⚠️  pymysql não instalado`
- ✅ **SEM** aviso sobre SQLite
- ✅ Conexão estabelecida com MySQL

**Se ainda aparecer avisos:**
1. Verifique se o arquivo `api/.env` existe
2. Verifique se `DB_TYPE=mysql` está no `.env`
3. Verifique se todas as variáveis MySQL estão preenchidas

---

## 🧪 Testar Após Reiniciar

Após reiniciar o servidor, teste:

```bash
# Health check
curl http://localhost:5000/health

# Ping
curl http://localhost:5000/ping

# Login (deve funcionar com dados do MySQL)
curl -X POST http://localhost:5000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 📋 Checklist

- [ ] Servidor parado (Ctrl+C)
- [ ] Servidor reiniciado (`python app.py`)
- [ ] Logs não mostram avisos sobre pymysql
- [ ] Logs não mostram avisos sobre SQLite
- [ ] Teste de conexão funcionando

---

**Após reiniciar, o servidor usará o MySQL remoto!** 🚀

