# 🔐 Como Configurar as Credenciais (API_KEY e SHARED_SECRET)

## 🎯 O que são essas credenciais?

- **API_KEY**: Chave de autenticação (como uma senha para a API)
- **SHARED_SECRET**: Segredo compartilhado (usado para assinaturas criptográficas)

**IMPORTANTE:** Devem ser **iguais** no backend e no cliente!

---

## 🚀 Método 1: Gerar Automaticamente (RECOMENDADO)

### Execute o script:

```powershell
.\gerar_credenciais.ps1
```

O script vai:
1. ✅ Gerar credenciais seguras automaticamente
2. ✅ Salvar no `api/.env` (se você quiser)
3. ✅ Mostrar as credenciais para você copiar
4. ✅ Copiar automaticamente para área de transferência

### Depois:

1. **No backend (`api/.env`):**
   - As credenciais já estarão salvas (se você escolheu salvar)

2. **No cliente (`youtube_tv_standalone.ahk`):**
   - Cole as credenciais nas linhas 12-13

---

## 🔧 Método 2: Criar Manualmente

### 1. Crie valores aleatórios:

**API_KEY:** 32 caracteres (letras e números)
- Exemplo: `SUA_API_KEY_32_CARACTERES_AQUI`

**SHARED_SECRET:** 64 caracteres (letras e números) - mais longo
- Exemplo: `SEU_SHARED_SECRET_64_CARACTERES_AQUI`

### 2. Configure no Backend:

Crie/edite o arquivo `api/.env`:

```env
API_KEY=SUA_API_KEY_32_CARACTERES_AQUI
SHARED_SECRET=SEU_SHARED_SECRET_64_CARACTERES_AQUI
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
ALLOW_AUTO_PROVISION=false
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123
```

### 3. Configure no Cliente:

Edite `youtube_tv_standalone.ahk` (linhas 11-13):

```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "SUA_API_KEY_32_CARACTERES_AQUI"
g_LicenseAPI_Secret := "SEU_SHARED_SECRET_64_CARACTERES_AQUI"
```

**Use os MESMOS valores em ambos os lugares!**

---

## 📋 Passo a Passo Completo

### 1. Gere as credenciais:

```powershell
cd C:\protecao
.\gerar_credenciais.ps1
```

### 2. Configure no Backend:

O script já salva no `api/.env` automaticamente (se você escolher).

### 3. Configure no Cliente:

1. Abra `youtube_tv_standalone.ahk`
2. Substitua as linhas 12-13 com as credenciais geradas
3. Salve o arquivo

### 4. Reinicie o Backend:

```powershell
cd api
python app.py
```

### 5. Compile o Cliente:

- Compile `youtube_tv_standalone.ahk` com Ahk2Exe
- Distribua o `.exe`

---

## ⚠️ IMPORTANTE

- ✅ **Use as MESMAS credenciais** no backend e no cliente
- ✅ **Mantenha seguras** - não compartilhe publicamente
- ✅ **Não use valores simples** como "123" ou "abc"
- ✅ **Gere valores aleatórios** longos e complexos

---

## 🔍 Verificar se está correto

### Backend:
- Arquivo `api/.env` existe e tem as credenciais
- Backend está rodando (`python app.py`)

### Cliente:
- Arquivo `youtube_tv_standalone.ahk` tem as mesmas credenciais
- Script compilado

### Teste:
- Execute o script protegido
- Se der erro "API key inválida" → credenciais diferentes
- Se funcionar → está correto! ✅

---

## 🎯 Resumo Rápido

1. Execute: `.\gerar_credenciais.ps1`
2. Copie as credenciais geradas
3. Cole no `youtube_tv_standalone.ahk` (linhas 12-13)
4. Pronto!

---

**Agora você tem credenciais seguras!** 🔐





