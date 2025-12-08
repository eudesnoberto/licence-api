# 📋 Resumo Rápido: Como Criar os Servidores

## 🎯 Resposta Direta

Você precisa fazer **deploy da mesma API em 3 serviços diferentes**:

1. **Railway.app** → Servidor Principal
2. **Render.com** → Backup 1  
3. **Fly.io** → Backup 2 (opcional)

---

## 🚀 Passo a Passo Simplificado

### **1. Subir Código para GitHub** (Já feito se seguiu guia anterior)

```bash
cd C:\protecao
git init
git remote add origin https://github.com/eudesnoberto/licence-api.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

### **2. Deploy no Railway (Servidor Principal)**

1. Acesse: https://railway.app
2. Login com GitHub
3. New Project → Deploy from GitHub
4. Selecione: `eudesnoberto/licence-api`
5. Configure variáveis de ambiente
6. Deploy automático!
7. **Copie a URL**: `https://xxx.railway.app`

### **3. Deploy no Render (Backup 1)**

1. Acesse: https://render.com
2. Login com GitHub
3. New → Web Service
4. Selecione: `eudesnoberto/licence-api`
5. Build: `pip install -r requirements.txt`
6. Start: `cd api && python app.py`
7. Configure variáveis (PORT=10000)
8. Deploy!
9. **Copie a URL**: `https://xxx.onrender.com`

### **4. Deploy no Fly.io (Backup 2 - Opcional)**

1. Instale CLI: `iwr https://fly.io/install.ps1 -useb | iex`
2. `fly auth login`
3. `cd C:\protecao`
4. `fly launch`
5. `fly deploy`
6. **Copie a URL**: `https://xxx.fly.dev`

---

## 🔧 Configurar no Cliente AHK

Depois de obter as 3 URLs, atualize `SOLUCAO_COM_REDUNDANCIA.ahk`:

```autohotkey
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://SUA-URL-RAILWAY.railway.app"    ; Cole URL do Railway
g_LicenseAPI_Servers[2] := "https://SUA-URL-RENDER.onrender.com"    ; Cole URL do Render
g_LicenseAPI_Servers[3] := "https://SUA-URL-FLY.fly.dev"            ; Cole URL do Fly.io
```

---

## ✅ Checklist

- [ ] Código no GitHub
- [ ] Deploy Railway feito → URL obtida
- [ ] Deploy Render feito → URL obtida
- [ ] (Opcional) Deploy Fly.io feito → URL obtida
- [ ] URLs configuradas no cliente AHK
- [ ] Testado funcionamento

---

## 📚 Guias Detalhados

- `GUIA_CRIAR_MULTIPLOS_SERVIDORES.md` - Guia completo passo a passo
- `PASSO_A_PASSO_GITHUB_RENDER.md` - Guia específico Render
- `GUIA_DEPLOY_RAILWAY.md` - Guia específico Railway

---

**Pronto!** Agora você sabe como criar os servidores! 🚀

