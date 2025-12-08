# 🌐 Configuração para Produção (Clientes)

## ⚠️ IMPORTANTE

Quando você compilar o `.exe` para distribuir aos clientes, o script **DEVE** usar a URL de produção, não localhost!

---

## ✅ Configuração Correta

### No Script (`youtube_tv_standalone.ahk`):

```autohotkey
; Linha 11 - URL da API
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
```

**NÃO use `http://127.0.0.1:5000` para clientes!**

---

## 🔧 Como Funciona

### 1. Desenvolvimento (Você testando):
- Use: `http://127.0.0.1:5000`
- Backend rodando localmente
- Para testar antes de distribuir

### 2. Produção (Clientes):
- Use: `https://api.fartgreen.fun`
- Backend rodando no servidor
- Clientes acessam pela internet

---

## 📋 Checklist Antes de Distribuir

- [ ] URL configurada para `https://api.fartgreen.fun`
- [ ] Credenciais corretas (API_KEY e SHARED_SECRET)
- [ ] Backend rodando e acessível publicamente
- [ ] Testado se a API responde em `https://api.fartgreen.fun/health`
- [ ] Compilado o `.exe` com essas configurações

---

## 🚀 Deploy do Backend

Para que os clientes possam usar, o backend precisa estar:

1. **Rodando em um servidor acessível pela internet**
2. **Com domínio configurado:** `api.fartgreen.fun`
3. **Com SSL/HTTPS configurado**
4. **Com firewall permitindo conexões na porta 443 (HTTPS)**

---

## 🧪 Como Testar

### Teste Local (Desenvolvimento):
```powershell
# Use localhost
$url = "http://127.0.0.1:5000/health"
Invoke-WebRequest -Uri $url
```

### Teste Produção (Clientes):
```powershell
# Use produção
$url = "https://api.fartgreen.fun/health"
Invoke-WebRequest -Uri $url
```

**Ambos devem responder!**

---

## 🔍 Verificar se Backend está Acessível

```powershell
# Teste de conectividade
Test-NetConnection api.fartgreen.fun -Port 443

# Teste HTTP
Invoke-WebRequest -Uri "https://api.fartgreen.fun/health"
```

**Se não responder:**
- Backend não está rodando no servidor
- Firewall bloqueando
- DNS não configurado
- SSL não configurado

---

## ⚙️ Duas Versões (Opcional)

Se quiser manter duas versões:

### `youtube_tv_standalone_dev.ahk` (Desenvolvimento):
```autohotkey
g_LicenseAPI_BaseURL := "http://127.0.0.1:5000"
```

### `youtube_tv_standalone_prod.ahk` (Produção):
```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
```

**Compile apenas a versão PROD para distribuir!**

---

## 🎯 Resumo

- ✅ **Desenvolvimento:** `http://127.0.0.1:5000`
- ✅ **Produção (Clientes):** `https://api.fartgreen.fun`
- ✅ **Sempre use produção ao compilar para distribuir!**

---

**Agora está configurado corretamente para produção!** 🚀





