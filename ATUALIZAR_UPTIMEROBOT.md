# 🔄 Atualizar Monitoramento UptimeRobot

## ⚠️ Problema Identificado

O monitoramento está configurado para o servidor **antigo**:
- ❌ **Antigo**: `licence-api-zsbg.onrender.com` (OFFLINE)
- ✅ **Novo**: `licence-api-6evg.onrender.com` (ONLINE)

## 🔧 Como Atualizar

### **Passo 1: Acessar UptimeRobot**

1. Acesse: https://uptimerobot.com
2. Faça login na sua conta
3. Vá em **My Monitors**

### **Passo 2: Editar Monitor**

1. Encontre o monitor para `licence-api-zsbg.onrender.com/ping`
2. Clique em **Edit** (ou no ícone de lápis)
3. Altere a **URL** de:
   ```
   https://licence-api-zsbg.onrender.com/ping
   ```
   Para:
   ```
   https://licence-api-6evg.onrender.com/ping
   ```
4. Clique em **Save**

### **Passo 3: Verificar**

Após salvar, aguarde alguns minutos e verifique:
- ✅ Status deve mudar para **UP**
- ✅ Response time deve aparecer
- ✅ Uptime deve começar a melhorar

---

## 📊 URLs dos Servidores

### **Servidor Principal (Render)**
- **URL**: `https://licence-api-6evg.onrender.com/ping`
- **Status**: ✅ ONLINE
- **Endpoint**: `/ping` ou `/health`

### **Servidor Backup (Koyeb)**
- **URL**: `https://shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app/ping`
- **Status**: ⚠️ Verificar

### **Servidor Principal (Cloudflare)**
- **URL**: `https://api.fartgreen.fun/ping`
- **Status**: ❌ OFFLINE

---

## 🎯 Recomendação

Configure **múltiplos monitores** para redundância:

1. **Monitor Principal**: `licence-api-6evg.onrender.com/ping`
2. **Monitor Backup**: `shiny-jemmie-easyplayrockola-6d2e5ef0.koyeb.app/ping`

Isso permite monitorar ambos os servidores e receber alertas se algum cair.

---

## ✅ Após Atualizar

O monitoramento deve mostrar:
- ✅ Status: **UP**
- ✅ Response time: ~100-300ms
- ✅ Uptime: Começando a melhorar

---

**Importante**: O servidor antigo (`licence-api-zsbg`) foi deletado e substituído pelo novo (`licence-api-6evg`).

