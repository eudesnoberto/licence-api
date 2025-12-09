# 🔧 Adicionar Variáveis de Ambiente no Koyeb

## ✅ Sim, você precisa adicionar as variáveis!

As variáveis de ambiente **NÃO** são aplicadas automaticamente do `koyeb.toml`. Você precisa adicioná-las manualmente no dashboard.

---

## 📋 Passo a Passo

### **1. Acessar Configurações**

1. Acesse: https://app.koyeb.com
2. Faça login
3. Vá no seu app: `thick-beverly-easyplayrockola-37418eab.koyeb.app`
4. Clique em **"Settings"** (ou **"Configure"**)

### **2. Adicionar Variáveis de Ambiente**

1. Vá em **"Environment"** ou **"Environment Variables"**
2. Clique em **"Add Environment Variable"** (ou **"+"**)

### **3. Adicionar Cada Variável**

Adicione **uma por uma** as seguintes variáveis:

#### **Variável 1:**
- **Key**: `DB_TYPE`
- **Value**: `mysql`
- Clique em **"Save"** ou **"Add"**

#### **Variável 2:**
- **Key**: `MYSQL_HOST`
- **Value**: `108.179.252.54`
- Clique em **"Save"** ou **"Add"**

#### **Variável 3:**
- **Key**: `MYSQL_PORT`
- **Value**: `3306`
- Clique em **"Save"** ou **"Add"**

#### **Variável 4:**
- **Key**: `MYSQL_DATABASE`
- **Value**: `scpmtc84_api`
- Clique em **"Save"** ou **"Add"**

#### **Variável 5:**
- **Key**: `MYSQL_USER`
- **Value**: `scpmtc84_api`
- Clique em **"Save"** ou **"Add"**

#### **Variável 6:**
- **Key**: `MYSQL_PASSWORD`
- **Value**: `nQT-8gW%-qCY`
- Clique em **"Save"** ou **"Add"**

---

## ✅ Checklist

Após adicionar todas, você deve ter:

- [ ] `DB_TYPE` = `mysql`
- [ ] `MYSQL_HOST` = `108.179.252.54`
- [ ] `MYSQL_PORT` = `3306`
- [ ] `MYSQL_DATABASE` = `scpmtc84_api`
- [ ] `MYSQL_USER` = `scpmtc84_api`
- [ ] `MYSQL_PASSWORD` = `nQT-8gW%-qCY`

**Total: 6 variáveis**

---

## 🔄 Após Adicionar

1. O Koyeb pode fazer **redeploy automático** após adicionar variáveis
2. Se não fizer, clique em **"Redeploy"** ou **"Deploy"**
3. Verifique os logs para confirmar que está conectando ao MySQL

---

## 🧪 Testar Conexão

Após o deploy, teste:

```bash
curl https://seu-app.koyeb.app/health
```

Deve retornar:
```json
{
  "status": "ok",
  "message": "Server is alive",
  "server": "license-api"
}
```

---

## ⚠️ Importante

- **Não compartilhe** as variáveis de ambiente publicamente
- **Não commite** senhas no código
- As variáveis no `koyeb.toml` são apenas para referência, **não são aplicadas automaticamente**

---

**Pronto!** Após adicionar todas as variáveis, o app deve conectar ao MySQL. 🚀

