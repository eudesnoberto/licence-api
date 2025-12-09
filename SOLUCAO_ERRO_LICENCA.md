# 🔧 Solução: Erro "Licença Inválida"

## ❌ Problema

Aparece mensagem "Licença Inválida" com Device ID vazio ou licença não encontrada.

---

## ✅ Soluções

### 1. Verificar se o Device ID foi gerado

O Device ID é gerado automaticamente na primeira execução e salvo em:
- `device.id` (na mesma pasta do script)

**Verificar:**
1. Procure o arquivo `device.id` na pasta do script
2. Abra com Bloco de Notas
3. Copie o conteúdo (é o Device ID)

---

### 2. Cadastrar o Device ID no Dashboard

1. **Acesse o dashboard:** `http://localhost:5173`
2. **Login:** `admin` / `admin123`
3. **Seção "Cadastro Rápido por Device ID":**
   - Cole o Device ID
   - Escolha o tipo de licença
   - Clique "Criar Licença"

**Pronto!** Execute o script novamente.

---

### 3. Verificar se o Backend está rodando

```powershell
# Teste se a API está respondendo
curl http://localhost:5000/health

# Ou abra no navegador:
# http://localhost:5000/health
```

**Se não responder:**
- Inicie o backend: `.\iniciar-backend.ps1`
- Verifique se está na porta 5000

---

### 4. Verificar Credenciais

**Backend (`api/.env`):**
```env
# ⚠️ IMPORTANTE: Substitua pelos valores reais
API_KEY=SUA_API_KEY_AQUI
SHARED_SECRET=SEU_SHARED_SECRET_AQUI
```

**Cliente (`youtube_tv_standalone.ahk` linhas 12-13):**
```autohotkey
g_LicenseAPI_Key := "SUA_API_KEY_AQUI"
g_LicenseAPI_Secret := "SEU_SHARED_SECRET_AQUI"
```

**Devem ser IGUAIS!**

---

### 5. Verificar URL da API

**Cliente (`youtube_tv_standalone.ahk` linha 11):**

**Desenvolvimento (local):**
```autohotkey
g_LicenseAPI_BaseURL := "http://127.0.0.1:5000"
```

**Produção:**
```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
```

---

## 🔍 Passo a Passo para Resolver

### Passo 1: Obter o Device ID

**Opção A - Arquivo:**
- Procure `device.id` na pasta do script
- Abra e copie o conteúdo

**Opção B - Mensagem de erro:**
- A mensagem agora mostra o Device ID
- Copie da mensagem

**Opção C - Script auxiliar:**
- Execute `obter_device_id.ahk`
- O ID é copiado automaticamente

### Passo 2: Verificar Backend

```powershell
# Inicie o backend se não estiver rodando
cd C:\protecao
.\iniciar-backend.ps1
```

### Passo 3: Cadastrar no Dashboard

1. Acesse: `http://localhost:5173`
2. Login: `admin` / `admin123`
3. Cole o Device ID
4. Escolha o plano
5. Clique "Criar Licença"

### Passo 4: Testar Novamente

- Execute o script protegido
- Deve funcionar agora! ✅

---

## 🐛 Troubleshooting

### Device ID vazio na mensagem
- ✅ **Corrigido!** Agora o código garante que o Device ID seja sempre exibido
- O Device ID é copiado automaticamente para área de transferência

### "Erro de conexão"
- Verifique se o backend está rodando
- Verifique a URL no script (linha 11)
- Verifique firewall/antivírus

### "API key inválida"
- Verifique se as credenciais estão iguais no backend e cliente
- Execute `.\gerar_credenciais.ps1` novamente se necessário

### "ID não registrado"
- Cadastre o Device ID no dashboard
- Ou ative `ALLOW_AUTO_PROVISION=true` no backend (menos seguro)

---

## ✅ Checklist

- [ ] Device ID obtido (arquivo ou mensagem)
- [ ] Backend rodando (`python app.py`)
- [ ] Credenciais iguais no backend e cliente
- [ ] URL da API correta (localhost ou produção)
- [ ] Device ID cadastrado no dashboard
- [ ] Licença com status "active" no dashboard

---

**Problema resolvido!** O código agora mostra o Device ID corretamente e copia automaticamente. 🎉





