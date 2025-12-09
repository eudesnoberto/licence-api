# 🔄 Como Configurar UptimeRobot para Keep-Alive

## 🎯 Objetivo

Manter o servidor Render ativo fazendo ping a cada 5 minutos, evitando que ele "durma".

---

## 📋 Passo a Passo

### **Passo 1: Criar Conta no UptimeRobot**

1. Acesse: https://uptimerobot.com
2. Clique em **"Sign Up"** (canto superior direito)
3. Preencha:
   - Email
   - Senha
   - Confirme senha
4. Clique em **"Create Account"**
5. Verifique seu email e confirme a conta

---

### **Passo 2: Adicionar Monitor**

1. Após login, você verá o dashboard
2. Clique no botão **"+ Add New Monitor"** (canto superior direito)

3. **Preencha o formulário:**
   - **Monitor Type**: Selecione **"HTTP(s)"**
   - **Friendly Name**: `License API Render`
   - **URL (or IP)**: `https://licence-api-6evg.onrender.com/ping`
   - **Monitoring Interval**: Selecione **"5 minutes"** (mínimo no plano free)
   - **Alert Contacts**: (Opcional) Adicione seu email para receber alertas

4. Clique em **"Create Monitor"**

---

### **Passo 2.5: Adicionar Monitor para Koyeb (Opcional mas Recomendado)**

1. Clique em **"+ Add New Monitor"** novamente

2. **Preencha o formulário:**
   - **Monitor Type**: Selecione **"HTTP(s)"**
   - **Friendly Name**: `License API Koyeb`
   - **URL (or IP)**: `https://working-cecilla-easyplayrockola-9b0c7243.koyeb.app/ping`
     - ⚠️ **Substitua pela URL real do seu app Koyeb**
   - **Monitoring Interval**: Selecione **"5 minutes"**
   - **Alert Contacts**: (Opcional) Adicione seu email

3. Clique em **"Create Monitor"**

📖 **Guia completo**: Veja `CONFIGURAR_PING_KOYEB.md` para mais detalhes.

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
   - Histórico

---

## ✅ Resultado

Agora o UptimeRobot fará ping no seu servidor a cada 5 minutos:
- ✅ Mantém servidor ativo (não "dorme")
- ✅ Evita delay de 50+ segundos
- ✅ Preserva dados do banco
- ✅ Grátis (até 50 monitores)

---

## 🔍 Verificar se Está Funcionando

### **1. Logs do Render:**
- Dashboard → Seu serviço → Logs
- Deve ver requisições GET em `/ping` a cada 5 minutos

### **2. UptimeRobot Dashboard:**
- Mostra status e tempo de resposta
- Histórico de verificações

### **3. Teste Manual:**
```bash
curl https://licence-api-6evg.onrender.com/ping
```

Deve retornar:
```json
{
  "status": "ok",
  "message": "Server is alive",
  "timestamp": "...",
  "server": "license-api"
}
```

---

## ⚙️ Configurações Avançadas (Opcional)

### **Alertas por Email:**
1. Dashboard → Alert Contacts
2. Adicione seu email
3. Configure alertas (quando servidor cair, etc.)

### **Status Page (Público):**
1. Dashboard → Status Pages
2. Crie uma página pública mostrando status do servidor
3. Compartilhe com usuários

---

## 🎯 Alternativas

Se não quiser usar UptimeRobot:

1. **cron-job.org** - Similar, também gratuito
2. **Script Python local** - Use `keep_alive.py` se tiver PC sempre ligado
3. **GitHub Actions** - Pode fazer ping via workflow (gratuito)

---

**Pronto!** Configure o UptimeRobot e seu servidor não vai mais "dormir"! 🚀

