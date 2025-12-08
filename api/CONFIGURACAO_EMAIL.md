# Configuração de Email - Alertas de Expiração

## 📧 Funcionalidade

O sistema envia emails automáticos quando a licença está próxima do vencimento:
- **3 dias antes** da expiração
- **2 dias antes** da expiração  
- **1 dia antes** da expiração

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Adicione no arquivo `api/.env`:

```env
# Email SMTP
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
SMTP_FROM_EMAIL=seu-email@gmail.com
SMTP_FROM_NAME=Sistema de Licenciamento
SMTP_USE_TLS=true
```

### 2. Gmail (Recomendado)

#### Passo 1: Criar Senha de App

1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione "App" → "Email"
3. Selecione "Outro (Nome personalizado)" → Digite "Sistema Licenciamento"
4. Clique em "Gerar"
5. **Copie a senha gerada** (16 caracteres)

#### Passo 2: Configurar

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Senha de app gerada
SMTP_USE_TLS=true
```

### 3. Outlook/Hotmail

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=seu-email@outlook.com
SMTP_PASSWORD=sua-senha
SMTP_USE_TLS=true
```

### 4. Servidor SMTP Personalizado

```env
SMTP_HOST=mail.seudominio.com
SMTP_PORT=587
SMTP_USER=noreply@seudominio.com
SMTP_PASSWORD=sua-senha
SMTP_USE_TLS=true
```

## 🕐 Agendamento

Os emails são enviados **diariamente às 09:00** (horário do servidor).

Para alterar, edite `api/app.py`:

```python
scheduler.add_job(
    check_and_send_expiration_emails,
    trigger=CronTrigger(hour=9, minute=0),  # Altere aqui
    ...
)
```

## 📝 Template de Email

O email é enviado em HTML moderno e responsivo, incluindo:

- ✅ Design moderno com gradiente
- ✅ Cores diferentes por urgência (vermelho para 1 dia, laranja para 2, azul para 3)
- ✅ Informações da licença
- ✅ Botão de ação para renovar
- ✅ Responsivo (funciona em mobile)

## 🧪 Testar

### 1. Teste Manual

Execute no Python:

```python
from email_service import check_and_send_expiration_emails
check_and_send_expiration_emails()
```

### 2. Verificar Logs

Os logs mostrarão:

```
Email enviado para cliente@email.com - 3 dias restantes
Email enviado para cliente@email.com - 2 dias restantes
Email enviado para cliente@email.com - 1 dias restantes
```

### 3. Verificar no Banco

Os envios são registrados na tabela `access_logs`:

```sql
SELECT * FROM access_logs 
WHERE message LIKE '%Email enviado%' 
ORDER BY created_at DESC;
```

## ⚠️ Troubleshooting

### Email não está sendo enviado

1. **Verifique se SMTP_ENABLED=true**
2. **Verifique credenciais** no `.env`
3. **Teste conexão SMTP** manualmente
4. **Verifique logs** do backend

### Erro: "Authentication failed"

- Gmail: Use **Senha de App**, não a senha normal
- Outlook: Pode precisar habilitar "Aplicativos menos seguros"
- Verifique se `SMTP_USER` e `SMTP_PASSWORD` estão corretos

### Erro: "Connection refused"

- Verifique `SMTP_HOST` e `SMTP_PORT`
- Verifique firewall/antivírus
- Teste conexão: `telnet smtp.gmail.com 587`

### Emails não chegam

- Verifique pasta de **Spam/Lixo Eletrônico**
- Verifique se o email do cliente está correto no cadastro
- Verifique logs para ver se foi enviado com sucesso

## 🔒 Segurança

- ⚠️ **NUNCA** commite o arquivo `.env` no Git
- ⚠️ Use **Senha de App** para Gmail (não senha normal)
- ⚠️ Mantenha as credenciais seguras

## 📊 Monitoramento

O sistema registra cada envio de email na tabela `access_logs` com a mensagem:
- `"Email enviado: 3 dias restantes"`
- `"Email enviado: 2 dias restantes"`
- `"Email enviado: 1 dias restantes"`

Isso evita envios duplicados no mesmo dia.

---

**Sistema de emails configurado e funcionando!** 📧




