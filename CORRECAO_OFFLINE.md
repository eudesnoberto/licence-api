# 🔧 Correção do Sistema Offline - 7 Dias de Graça

## Problema Identificado

O sistema offline não estava funcionando corretamente quando o servidor estava offline. O AHK exibia mensagem de "software não foi registrado" mesmo quando deveria funcionar em modo offline com período de graça de 7 dias.

## Correções Aplicadas

### 1. **Melhorias no Tratamento de Erros de Conexão**

Adicionado logs detalhados para debug quando o servidor está offline:

- ✅ Log quando tenta validar offline
- ✅ Log quando token é encontrado/carregado
- ✅ Log quando validação offline é bem-sucedida
- ✅ Log quando validação offline falha (com motivo)

### 2. **Melhorias nas Funções de Token**

#### `License_SaveToken()`:
- ✅ Logs detalhados quando salva token
- ✅ Indica onde o token foi salvo (pasta do script ou %APPDATA%)
- ✅ Log de erro se falhar ao salvar

#### `License_LoadToken()`:
- ✅ Logs quando carrega token
- ✅ Indica de onde o token foi carregado
- ✅ Log quando token não é encontrado

### 3. **Fallback Duplo para Offline**

Agora o sistema tenta validar offline em **duas etapas**:

1. **Dentro de `License_Verify()`**: Quando detecta erro de conexão, tenta validar offline imediatamente
2. **Fora de `License_Verify()`**: Se ainda falhou, tenta novamente como fallback adicional

### 4. **Arquivos de Debug Criados**

Os seguintes arquivos são criados em `%TEMP%` para debug:

- `license_offline_attempt.txt` - Quando tenta validar offline
- `license_offline_success.txt` - Quando modo offline é ativado com sucesso
- `license_offline_failed.txt` - Quando validação offline falha
- `license_offline_no_token.txt` - Quando token não é encontrado
- `license_token_save_log.txt` - Log de salvamento de token
- `license_token_load_log.txt` - Log de carregamento de token
- `license_token_not_found.txt` - Quando token não é encontrado
- `license_verification_result.txt` - Resultado completo da verificação

## Como Testar

### 1. **Primeiro: Verificar se Token está sendo Salvo**

1. Execute o script com servidor **ONLINE**
2. Verifique se o token foi salvo:
   - `%TEMP%\license_token_save_log.txt` deve existir
   - `license_token.json` deve existir na pasta do script ou `%APPDATA%\LicenseSystem\`

### 2. **Depois: Testar Modo Offline**

1. **Desligue o servidor** (ou bloqueie acesso à URL da API)
2. Execute o script novamente
3. Verifique os logs em `%TEMP%`:
   - `license_offline_attempt.txt` - Deve indicar tentativa de validação offline
   - `license_offline_success.txt` - Deve indicar sucesso (se token válido)
   - `license_offline_failed.txt` - Deve indicar motivo da falha (se falhou)

### 3. **Verificar Mensagem de Erro**

Se ainda exibir "software não foi registrado", verifique:

1. **Token existe?**
   - Verifique `license_token.json` na pasta do script
   - Verifique `%APPDATA%\LicenseSystem\license_token.json`

2. **Token é válido?**
   - Abra o arquivo e verifique se contém `"license_token"` com `payload` e `signature`

3. **Device ID corresponde?**
   - O token deve ter o mesmo `device_id` do computador atual
   - Verifique em `license_verification_result.txt`

## Requisitos para Modo Offline Funcionar

✅ **Token deve ter sido salvo anteriormente** (quando servidor estava online)  
✅ **Token deve ser válido** (não expirado ou dentro do período de graça)  
✅ **Device ID deve corresponder** ao token salvo  
✅ **Status da licença deve ser "active"** no token

## Período de Graça

- **Padrão**: 7 dias (`g_LicenseOffline_GracePeriodDays := 7`)
- **Funcionamento**: Permite uso offline mesmo se licença expirou há menos de 7 dias
- **Após período**: Requer conexão online obrigatória

## Próximos Passos se Ainda Não Funcionar

1. **Verifique os logs** em `%TEMP%` para identificar o problema exato
2. **Verifique se o token foi salvo** na primeira execução online
3. **Verifique se o Device ID corresponde** ao token
4. **Verifique se a licença não expirou** há mais de 7 dias

## Arquivos Modificados

- `ahk-client/youtube_tv_standalone.ahk`
  - Função `License_Verify()` - Melhor tratamento de erros offline
  - Função `License_SaveToken()` - Logs detalhados
  - Função `License_LoadToken()` - Logs detalhados
  - Fallback duplo para validação offline

---

**Data da Correção**: 2024-12-15  
**Versão**: 1.1.0

