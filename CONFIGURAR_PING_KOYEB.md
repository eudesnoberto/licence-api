# 🔄 Configurar Ping/Keep-Alive para Koyeb

## 🎯 Objetivo

Configurar monitoramento e keep-alive para o servidor Koyeb, garantindo que ele esteja sempre ativo e monitorado.

**Nota**: Diferente do Render, o Koyeb **não "dorme"** no plano free, mas o ping é útil para:
- ✅ Monitoramento de status
- ✅ Alertas quando o servidor cair
- ✅ Histórico de uptime
- ✅ Garantir que o servidor está respondendo

---

## 📋 Opção 1: UptimeRobot (Recomendado)

### **Passo 1: Acessar UptimeRobot**

1. Acesse: https://uptimerobot.com
2. Faça login na sua conta

### **Passo 2: Adicionar Monitor para Koyeb**

1. Clique em **"+ Add New Monitor"** (canto superior direito)

2. **Preencha o formulário:**
   - **Monitor Type**: Selecione **"HTTP(s)"**
   - **Friendly Name**: `License API Koyeb`
   - **URL (or IP)**: `https://working-cecilla-easyplayrockola-9b0c7243.koyeb.app/ping`
     - ⚠️ **Substitua pela URL real do seu app Koyeb**
   - **Monitoring Interval**: Selecione **"5 minutes"** (mínimo no plano free)
   - **Alert Contacts**: (Opcional) Adicione seu email para receber alertas

3. Clique em **"Create Monitor"**

---

### **Passo 3: Verificar Funcionamento**

1. Aguarde alguns minutos
2. No dashboard, você verá o status do monitor:
   - 🟢 **Green** = Servidor online
   - 🔴 **Red** = Servidor offline
   - 🟡 **Yellow** = Verificando

3. Clique no monitor para ver detalhes:
   - Última verificação
   - Tempo de resposta
   - Histórico de uptime

---

## 📋 Opção 2: Múltiplos Monitores (Recomendado)

Configure monitores para **todos os servidores**:

### **Monitor 1: Render**
- **Friendly Name**: `License API Render`
- **URL**: `https://licence-api-6evg.onrender.com/ping`

### **Monitor 2: Koyeb**
- **Friendly Name**: `License API Koyeb`
- **URL**: `https://working-cecilla-easyplayrockola-9b0c7243.koyeb.app/ping`

### **Monitor 3: Servidor Principal (se aplicável)**
- **Friendly Name**: `License API Principal`
- **URL**: `https://api.fartgreen.fun/ping`

---

## 🧪 Testar Endpoint Manualmente

Antes de configurar o monitor, teste se o endpoint está funcionando:

```bash
# Teste do ping
curl https://working-cecilla-easyplayrockola-9b0c7243.koyeb.app/ping
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "message": "Server is alive",
  "timestamp": "2025-12-09T00:30:00.123456",
  "server": "license-api"
}
```

---

## ✅ Resultado

Após configurar, o UptimeRobot fará ping no servidor Koyeb a cada 5 minutos:
- ✅ Monitora status do servidor
- ✅ Envia alertas se o servidor cair
- ✅ Mantém histórico de uptime
- ✅ Grátis (até 50 monitores)

---

## 🔍 Verificar se Está Funcionando

### **1. Logs do Koyeb:**
- Dashboard → Seu app → Logs
- Deve ver requisições GET em `/ping` a cada 5 minutos

### **2. UptimeRobot Dashboard:**
- Mostra status e tempo de resposta
- Histórico de verificações
- Gráficos de uptime

### **3. Teste Manual:**
```bash
curl https://seu-app.koyeb.app/ping
```

---

## ⚙️ Configurações Avançadas (Opcional)

### **Alertas por Email:**
1. Dashboard → Alert Contacts
2. Adicione seu email
3. Configure alertas:
   - Quando servidor cair
   - Quando servidor voltar
   - Alertas de tempo de resposta lento

### **Status Page (Público):**
1. Dashboard → Status Pages
2. Crie uma página pública mostrando status de todos os servidores
3. Compartilhe com usuários

---

## 🎯 Alternativas ao UptimeRobot

Se não quiser usar UptimeRobot:

1. **cron-job.org** - Similar, também gratuito
2. **Script Python local** - Use `keep_alive.py` se tiver PC sempre ligado
3. **GitHub Actions** - Pode fazer ping via workflow (gratuito)
4. **Pingdom** - Alternativa paga com mais recursos

---

## 📊 Monitoramento Completo

Para monitoramento completo, configure:

1. ✅ **UptimeRobot** - Monitora todos os servidores
2. ✅ **Script de Verificação** - Use `VERIFICAR_SERVIDORES.ps1` localmente
3. ✅ **Logs do Koyeb** - Verifique logs periodicamente

---

## 🔗 URLs dos Servidores

Atualize estas URLs conforme necessário:

- **Render**: `https://licence-api-6evg.onrender.com/ping`
- **Koyeb**: `https://working-cecilla-easyplayrockola-9b0c7243.koyeb.app/ping`
- **Principal**: `https://api.fartgreen.fun/ping` (se aplicável)

---

**Pronto!** Configure o UptimeRobot e seu servidor Koyeb estará monitorado! 🚀

