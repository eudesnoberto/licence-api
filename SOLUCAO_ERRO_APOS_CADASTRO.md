# 🔧 Solução: Erro Após Cadastrar no Dashboard

## ❌ Problema

Licença cadastrada no dashboard (status ACTIVE), mas ainda aparece erro "Licença inválida".

---

## ✅ Soluções

### 1. Verificar URL da API (MAIS COMUM)

**O script está configurado para usar:**
- **Desenvolvimento:** `http://127.0.0.1:5000` (localhost)
- **Produção:** `https://api.fartgreen.fun`

**Verifique:**
1. Se o backend está rodando localmente → use `http://127.0.0.1:5000`
2. Se o backend está em produção → use `https://api.fartgreen.fun`

**Como alterar:**
- Edite `youtube_tv_standalone.ahk` linha 11
- Altere para a URL correta

---

### 2. Verificar se Backend está Rodando

```powershell
# Teste se está respondendo
curl http://127.0.0.1:5000/health

# Ou abra no navegador:
# http://127.0.0.1:5000/health
```

**Se não responder:**
```powershell
cd C:\protecao
.\iniciar-backend.ps1
```

---

### 3. Verificar Status da Licença

No dashboard, verifique:
- **Status deve ser:** `ACTIVE` (não `PENDING`)
- **Data de fim:** deve ser futura
- **Device ID:** deve corresponder exatamente

**Se estiver PENDING:**
- A licença não será aceita
- Altere o status para `ACTIVE` no banco de dados ou recrie a licença

---

### 4. Verificar Credenciais

**Backend (`api/.env`):**
```env
API_KEY=CFEC44D0118C85FBA54A4B96C89140C6
SHARED_SECRET=BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D
```

**Cliente (`youtube_tv_standalone.ahk` linhas 12-13):**
```autohotkey
g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
g_LicenseAPI_Secret := "BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
```

**Devem ser IGUAIS!**

---

### 5. Testar Manualmente a API

```powershell
# Substitua DEVICE_ID pelo Device ID cadastrado
$deviceId = "2049365993desktop-j65uer12025112"
$url = "http://127.0.0.1:5000/verify?id=$deviceId&version=1.0.0&ts=20250101120000&sig=test&api_key=CFEC44D0118C85FBA54A4B96C89140C6"
Invoke-WebRequest -Uri $url
```

**Deve retornar:**
```json
{"allow": true, "msg": "Licença válida"}
```

---

### 6. Ativar Debug (Opcional)

O código agora salva a resposta em `%TEMP%\license_debug.txt` para análise.

**Para ativar:**
1. Descomente a linha no código:
   ```autohotkey
   FileAppend, %response%`n, %A_Temp%\license_debug.txt
   ```
2. Execute o script
3. Veja o arquivo `%TEMP%\license_debug.txt` para ver a resposta exata

---

## 🔍 Checklist

- [ ] Backend rodando (`python app.py` ou `.\iniciar-backend.ps1`)
- [ ] URL da API correta (localhost ou produção)
- [ ] Credenciais iguais no backend e cliente
- [ ] Status da licença é `ACTIVE` (não `PENDING`)
- [ ] Device ID corresponde exatamente
- [ ] Data de fim é futura

---

## 🎯 Passo a Passo

1. **Verifique o backend:**
   ```powershell
   curl http://127.0.0.1:5000/health
   ```

2. **Verifique a URL no script:**
   - Linha 11: deve ser `http://127.0.0.1:5000` para desenvolvimento

3. **Teste a API manualmente:**
   - Use o PowerShell para testar o endpoint `/verify`

4. **Verifique o status no dashboard:**
   - Deve ser `ACTIVE`, não `PENDING`

5. **Execute o script novamente**

---

**Problema resolvido!** O código agora verifica múltiplas formas de resposta e mostra mensagens mais claras. 🎉





