# 🚂 Guia: Deploy da API no Railway.app (Gratuito)

## 📋 Pré-requisitos

- Conta no GitHub
- Código da API no repositório GitHub
- Conta no Railway.app (gratuita)

---

## 🚀 Passo a Passo

### **Passo 1: Preparar o Repositório**

1. Crie um repositório no GitHub (ou use um existente)
2. Adicione os arquivos da API:
   - `api/app.py`
   - `api/config.py`
   - `api/db.py`
   - `api/license_service.py`
   - `api/email_service.py`
   - `requirements.txt`

### **Passo 2: Criar requirements.txt**

Crie o arquivo `requirements.txt` na raiz do projeto:

```txt
Flask==3.0.0
flask-cors==4.0.0
werkzeug==3.0.1
APScheduler==3.10.4
```

### **Passo 3: Criar Procfile (Opcional)**

Crie o arquivo `Procfile` na raiz:

```
web: cd api && python app.py
```

### **Passo 4: Configurar Railway**

1. Acesse: https://railway.app
2. Clique em "Login" e conecte com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha seu repositório
6. Railway detectará automaticamente Python

### **Passo 5: Configurar Variáveis de Ambiente**

No Railway, vá em "Variables" e adicione:

```
FLASK_ENV=production
PORT=5000
DB_PATH=/data/protecao.db
API_KEY=CFEC44D0118C85FBA54A4B96C89140C6
SHARED_SECRET=BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
SMTP_ENABLED=false
```

### **Passo 6: Configurar Porta**

No Railway, vá em "Settings" > "Networking":
- Port: `5000`
- Public: `true`

### **Passo 7: Deploy**

Railway fará deploy automático! Aguarde alguns minutos.

### **Passo 8: Obter URL**

Após deploy, Railway fornecerá uma URL como:
```
https://seu-projeto.railway.app
```

Use esta URL no cliente AHK!

---

## 🔄 Configurar Múltiplos Servidores (Redundância)

### **Servidor 1: Railway**
- URL: `https://api1.railway.app`

### **Servidor 2: Render**
- URL: `https://api2.onrender.com`

### **Servidor 3: Fly.io**
- URL: `https://api3.fly.dev`

### **No Cliente AHK:**

```autohotkey
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://api1.railway.app"
g_LicenseAPI_Servers[2] := "https://api2.onrender.com"
g_LicenseAPI_Servers[3] := "https://api3.fly.dev"
```

---

## 📝 Arquivos Necessários para Deploy

### **requirements.txt**
```txt
Flask==3.0.0
flask-cors==4.0.0
werkzeug==3.0.1
APScheduler==3.10.4
```

### **Procfile** (opcional)
```
web: cd api && python app.py
```

### **runtime.txt** (opcional - especifica versão Python)
```
python-3.11.0
```

---

## ⚙️ Ajustes no app.py para Railway

Railway pode precisar de alguns ajustes:

```python
# No final do app.py, altere para:
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

---

## 🎯 Próximos Passos

1. ✅ Deploy no Railway
2. ✅ Testar URL
3. ✅ Configurar cliente AHK com nova URL
4. ✅ Deploy em segundo servidor (Render/Fly.io)
5. ✅ Configurar redundância no cliente

---

**Documento criado em**: 2024-12-15

