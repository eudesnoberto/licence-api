# 🔍 Diagnóstico: Erro "Todos os servidores indisponíveis"

## ❌ Problema

O script AHK está exibindo:
- **Mensagem**: "Todos os servidores indisponíveis e modo offline não disponível"
- **Device ID**: `2049365993desktop-j65uer12025112`

## ✅ Status dos Servidores

- ✅ **Render**: ONLINE (`https://licence-api-6evg.onrender.com`)
- ❌ **Principal**: OFFLINE (`https://api.fartgreen.fun`)
- ❌ **Koyeb**: OFFLINE

## ✅ Status da Licença no Banco

- ✅ **Device ID**: `2049365993desktop-j65uer12025112` está no banco MySQL
- ✅ **Status**: `active`
- ✅ **Tipo**: `mensal`
- ✅ **Proprietário**: Francieudes Silva N. Alves

## 🔍 Possíveis Causas

### 1. **Timeout muito curto**
O script usa `-TimeoutSec 10` no PowerShell. O Render pode estar demorando mais de 10 segundos para responder (servidor "dormindo").

### 2. **CORS ou bloqueio de requisições**
O PowerShell pode estar sendo bloqueado pelo servidor.

### 3. **Token não salvo**
Como é a primeira execução, não há token salvo para modo offline.

### 4. **Erro na requisição HTTP**
O PowerShell pode estar falhando silenciosamente.

## 🔧 Soluções

### **Solução 1: Aumentar timeout**

No arquivo `SOLUCAO_COM_REDUNDANCIA.ahk`, linha ~277:

```ahk
; ANTES:
psScript .= "  $response = Invoke-WebRequest -Uri '" . url . "' -TimeoutSec 10 -UseBasicParsing`n"

; DEPOIS:
psScript .= "  $response = Invoke-WebRequest -Uri '" . url . "' -TimeoutSec 30 -UseBasicParsing`n"
```

### **Solução 2: Verificar logs**

Verifique os arquivos de log em `%TEMP%`:
- `license_server_failover.txt` - Logs de tentativas de servidores
- `license_offline_no_token.txt` - Se token não foi encontrado

### **Solução 3: Testar manualmente**

Execute no PowerShell:
```powershell
$url = "https://licence-api-6evg.onrender.com/verify?id=2049365993desktop-j65uer12025112&version=1.0.0&ts=20251208203000&sig=test&api_key=SUA_API_KEY_AQUI"
Invoke-WebRequest -Uri $url -TimeoutSec 30 -UseBasicParsing
```

### **Solução 4: Verificar se Render está respondendo**

O Render pode estar "dormindo" (free tier). Primeira requisição pode demorar 30-50 segundos.

---

## 📋 Checklist

- [ ] Render está online? ✅ SIM
- [ ] Licença está no banco? ✅ SIM
- [ ] Timeout é suficiente? ⚠️ Pode ser curto (10s)
- [ ] Token foi salvo? ❌ NÃO (primeira execução)
- [ ] Requisição está funcionando? ❓ Precisa testar

---

## 🚀 Próximos Passos

1. **Aumentar timeout** para 30 segundos
2. **Testar requisição manual** no PowerShell
3. **Verificar logs** em `%TEMP%`
4. **Aguardar primeira resposta** do Render (pode demorar)

