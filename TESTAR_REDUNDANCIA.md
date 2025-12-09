# 🧪 Testar Redundância de Servidores

## ✅ Servidores Configurados

1. **Servidor Principal**: `https://api.fartgreen.fun`
2. **Backup 1 (Render)**: `https://licence-api-zsbg.onrender.com`
3. **Backup 2 (Koyeb)**: `https://thick-beverly-easyplayrockola-37418eab.koyeb.app`

---

## 🧪 Testes Realizados

### **1. Teste de Health Check**

```bash
# Servidor Principal
curl https://api.fartgreen.fun/health
# ✅ Resposta: {"status":"ok"}

# Backup 1 (Render)
curl https://licence-api-zsbg.onrender.com/health
# ✅ Resposta: {"status":"ok"}

# Backup 2 (Koyeb)
curl https://shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app/health
# ✅ Resposta: {"status":"ok"}
```

### **2. Teste de Ping (Keep-Alive)**

```bash
# Todos os servidores
curl https://api.fartgreen.fun/ping
curl https://licence-api-zsbg.onrender.com/ping
curl https://shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app/ping
```

---

## 🔄 Como Testar Redundância no Frontend

1. **Abra o Dashboard**: `https://fartgreen.fun/#dashboard`
2. **Abra o Console do Navegador** (F12)
3. **Verifique os logs**:
   ```
   ✅ Servidores carregados: ['https://api.fartgreen.fun', 'https://licence-api-zsbg.onrender.com', 'https://shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app']
   ```

4. **Teste de Fallback**:
   - Desative o servidor principal temporariamente
   - O sistema deve automaticamente tentar o Backup 1 (Render)
   - Se Backup 1 falhar, tenta Backup 2 (Koyeb)

---

## 🔄 Como Testar Redundância no AHK

1. **Use o script**: `SOLUCAO_COM_REDUNDANCIA.ahk`
2. **Verifique os logs** em:
   - `%A_Temp%\license_server_failover.txt` (tentativas de servidores)
   - `%A_Temp%\license_server_used.txt` (servidor que funcionou)
   - `%A_Temp%\license_offline_success.txt` (modo offline ativado)

3. **Teste de Fallback**:
   - Desative o servidor principal
   - Execute o script AHK
   - Deve tentar automaticamente os backups

---

## 📊 Status dos Servidores

| Servidor | Status | URL | Keep-Alive |
|----------|--------|-----|------------|
| Principal | ✅ Online | `https://api.fartgreen.fun` | ✅ Configurado |
| Render | ✅ Online | `https://licence-api-zsbg.onrender.com` | ✅ Configurado |
| Koyeb | ✅ Online | `https://shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app` | ✅ Configurado |

---

## 🔍 Verificação Manual

### **Frontend**
```javascript
// No console do navegador
console.log('Servidores:', API_SERVERS)
```

### **AHK**
```autohotkey
; Verificar servidores configurados
for index, server in g_LicenseAPI_Servers {
    MsgBox, Servidor %index%: %server%
}
```

---

## ⚠️ Importante

- **Ordem de prioridade**: Principal → Render → Koyeb
- **Fallback automático**: Se um servidor falhar, tenta o próximo
- **Modo offline**: Se todos falharem, usa modo offline (7 dias de graça)
- **Cache**: O sistema lembra qual servidor funcionou por último

---

**Última atualização**: 08/12/2025

