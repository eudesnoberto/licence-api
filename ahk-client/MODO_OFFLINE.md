# Sistema de Modo Offline - Período de Graça

## 🛡️ Funcionalidade

O sistema agora suporta **modo offline** com **período de graça**, permitindo que usuários continuem usando o sistema mesmo quando o servidor está offline ou indisponível.

## ⚙️ Como Funciona

### 1. Validação Online (Normal)

Quando o servidor está online:
1. Cliente faz requisição ao servidor
2. Servidor valida licença e retorna `license_token` assinado
3. Cliente salva o token localmente
4. Sistema funciona normalmente

### 2. Modo Offline (Servidor Indisponível)

Quando o servidor está offline:
1. Cliente tenta conectar ao servidor
2. Se falhar, carrega token salvo localmente
3. Valida token offline (sem precisar do servidor)
4. Permite uso durante período de graça (7 dias padrão)
5. Sistema continua funcionando

## 📋 Período de Graça

### Configuração

**Padrão:** 7 dias

**O que significa:**
- Se a licença expirou há menos de 7 dias, o sistema ainda funciona offline
- Se a licença expirou há mais de 7 dias, o sistema bloqueia

**Exemplo:**
```
Licença expira em: 2025-11-29
Hoje: 2025-12-05 (6 dias após expiração)
Status: ✅ Funciona (dentro do período de graça)

Licença expira em: 2025-11-29
Hoje: 2025-12-10 (11 dias após expiração)
Status: ❌ Bloqueado (fora do período de graça)
```

### Alterar Período de Graça

No arquivo `youtube_tv_standalone.ahk`, linha ~437:

```autohotkey
g_LicenseOffline_GracePeriodDays := 7  ; Altere para o número de dias desejado
```

## 🔐 Segurança

### Token Assinado

O token é assinado com **HMAC-SHA256** usando o `SHARED_SECRET`:
- ✅ Não pode ser falsificado
- ✅ Não pode ser usado em outro dispositivo
- ✅ Contém informações da licença (status, expiração, etc.)

### Validações Offline

O sistema valida:
1. ✅ **Device ID** corresponde ao token
2. ✅ **Status** é "active"
3. ✅ **Data de expiração** (com período de graça)
4. ✅ **Assinatura** (validada quando token foi gerado)

## 📁 Arquivos

### Token Salvo

O token é salvo em:
- `%SCRIPT_DIR%\license_token.json` (prioridade)
- `%APPDATA%\LicenseSystem\license_token.json` (fallback)

### Logs

Arquivos de debug:
- `%TEMP%\license_token_saved.txt` - Confirmação de salvamento
- `%TEMP%\license_offline_mode.txt` - Quando modo offline é ativado
- `%TEMP%\license_verification_result.txt` - Resultado da verificação

## 🔄 Fluxo Completo

### Cenário 1: Servidor Online

```
1. Cliente inicia
2. Tenta conectar ao servidor ✅
3. Recebe license_token
4. Salva token localmente
5. Sistema funciona normalmente
```

### Cenário 2: Servidor Offline (Primeira Vez)

```
1. Cliente inicia
2. Tenta conectar ao servidor ❌ (erro de conexão)
3. Verifica se tem token salvo ❌ (não tem)
4. Exibe mensagem de erro
5. Sistema bloqueado
```

### Cenário 3: Servidor Offline (Com Token)

```
1. Cliente inicia
2. Tenta conectar ao servidor ❌ (erro de conexão)
3. Verifica se tem token salvo ✅ (tem)
4. Valida token offline ✅
5. Verifica período de graça ✅
6. Sistema funciona em modo offline
7. Tenta reconectar periodicamente em background
```

## ⚙️ Configuração no Backend

### Período de Graça

No arquivo `api/config.py`:

```python
OFFLINE_GRACE_PERIOD_DAYS = 7  # Padrão: 7 dias
```

Ou via variável de ambiente:

```env
OFFLINE_GRACE_PERIOD_DAYS=7
```

## 🧪 Testar Modo Offline

### 1. Teste Básico

1. Execute o script normalmente (servidor online)
2. Verifique se `license_token.json` foi criado
3. Pare o servidor backend
4. Execute o script novamente
5. Deve funcionar em modo offline

### 2. Verificar Token

Verifique o arquivo `license_token.json`:

```json
{
  "payload": {
    "device_id": "...",
    "status": "active",
    "expires_at": "2026-11-29"
  },
  "payload_raw": "...",
  "signature": "..."
}
```

### 3. Testar Expiração

1. Modifique a data de expiração no token (para testar)
2. Execute o script
3. Deve bloquear se estiver fora do período de graça

## 📊 Monitoramento

### Logs do Cliente

O cliente registra:
- ✅ Quando token é salvo
- ✅ Quando modo offline é ativado
- ✅ Resultado da validação offline

### Logs do Servidor

O servidor registra:
- ✅ Quando token é gerado
- ✅ Quando cliente faz requisição online

## ⚠️ Limitações

### O que NÃO funciona offline:

- ❌ Criar novas licenças
- ❌ Atualizar informações
- ❌ Verificar status em tempo real
- ❌ Detectar clones (requer servidor)

### O que funciona offline:

- ✅ Validar licença existente
- ✅ Verificar expiração
- ✅ Permitir uso durante período de graça
- ✅ Bloquear se expirado há muito tempo

## 🔄 Sincronização

### Quando Servidor Volta Online

1. Cliente tenta conectar novamente
2. Se sucesso, atualiza token local
3. Sincroniza informações
4. Volta ao modo normal

### Verificação Periódica

O cliente pode ser configurado para verificar periodicamente:

```autohotkey
; Verifica a cada 30 minutos
SetTimer, VerificarLicencaPeriodicamente, 1800000
return

VerificarLicencaPeriodicamente:
    isValid := License_Verify()
    ; Se servidor voltou online, token será atualizado automaticamente
return
```

## 💡 Boas Práticas

### Para Administradores

1. **Período de Graça Razoável**: 7 dias é um bom equilíbrio
2. **Monitoramento**: Verifique logs quando servidor volta online
3. **Manutenção**: Avise clientes antes de manutenções longas

### Para Desenvolvedores

1. **Token Atualizado**: Sempre salve token quando receber resposta válida
2. **Fallback Inteligente**: Tente offline apenas se servidor realmente falhou
3. **Logs Detalhados**: Registre quando modo offline é ativado

## 🚨 Troubleshooting

### Modo offline não funciona

**Causa:** Token não foi salvo ou está inválido

**Solução:**
1. Verifique se `license_token.json` existe
2. Execute o script com servidor online primeiro
3. Verifique logs em `%TEMP%\license_token_saved.txt`

### Token inválido

**Causa:** Device ID mudou ou token corrompido

**Solução:**
1. Delete `license_token.json`
2. Execute com servidor online para gerar novo token

### Período de graça não funciona

**Causa:** Configuração incorreta

**Solução:**
1. Verifique `g_LicenseOffline_GracePeriodDays` no script
2. Verifique cálculo de dias (pode ter erro de fuso horário)

---

**Sistema de modo offline implementado e funcionando!** 🛡️




