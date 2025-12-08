# Guia de Integração - Sistema de Proteção de Licenças

Este guia explica como integrar o sistema de proteção de licenças em qualquer script AutoHotkey.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Método 1: Copiar Funções (Recomendado)](#método-1-copiar-funções-recomendado)
3. [Método 2: Arquivo Separado](#método-2-arquivo-separado)
4. [Exemplo Prático](#exemplo-prático)
5. [Configuração](#configuração)
6. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O sistema de proteção verifica se o computador tem uma licença válida antes de executar o script. Se não tiver, exibe uma mensagem com o Device ID e encerra o programa.

### Componentes Necessários

1. **Funções de licenciamento** (3 funções principais)
2. **Variáveis globais de configuração**
3. **Código de verificação no início do script**

---

## Método 1: Copiar Funções (Recomendado)

Este é o método mais simples e recomendado. Você copia as funções diretamente no seu script.

### Passo 1: Copiar as Funções

Copie estas 3 funções do arquivo `youtube_tv_standalone.ahk`:

1. `License_GetDeviceId()` - Gera/obtém o Device ID único
2. `License_SHA256()` - Calcula hash SHA256
3. `License_Verify()` - Verifica a licença no servidor

**Localização no arquivo original:**
- `License_GetDeviceId()`: linhas ~23-100
- `License_SHA256()`: linhas ~102-180
- `License_Verify()`: linhas ~209-431

### Passo 2: Adicionar Variáveis Globais

No início do seu script, adicione:

```autohotkey
; ============================================================================
; CONFIGURAÇÃO DO SISTEMA DE LICENÇAS
; ============================================================================
global g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
global g_LicenseAPI_Key := "SUA_API_KEY_AQUI"
global g_LicenseAPI_Secret := "SEU_SHARED_SECRET_AQUI"
global g_LicenseAPI_Version := "1.0.0"

; Variáveis globais para resultado da verificação
global g_LicenseVerify_DeviceId := ""
global g_LicenseVerify_Message := ""
global g_LicenseVerify_Offline := false
```

### Passo 3: Adicionar Verificação no Início

Logo após as variáveis globais, adicione:

```autohotkey
; ============================================================================
; VERIFICAÇÃO DE LICENÇA - BLOQUEIA SE NÃO TIVER LICENÇA
; ============================================================================
deviceId := License_GetDeviceId()

If (!deviceId Or StrLen(deviceId) < 16) {
    MsgBox, 16, Erro Critico, Nao foi possivel gerar Device ID.`n`nTente executar como administrador.
    ExitApp
}

; Verifica licença
isValid := License_Verify()

If (!isValid) {
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message
    
    displayDeviceId := g_LicenseVerify_DeviceId
    If (!displayDeviceId) {
        displayDeviceId := deviceId
    }
    
    ; Copia Device ID para área de transferência
    Clipboard := displayDeviceId
    
    ; Monta mensagem
    msgText := "Sua licenca nao e valida ou expirou.`n`n"
    If (g_LicenseVerify_Message) {
        msgText .= "Mensagem: " . g_LicenseVerify_Message . "`n`n"
    }
    msgText .= "========================================`n"
    msgText .= "Device ID (JA COPIADO!):`n"
    msgText .= displayDeviceId . "`n"
    msgText .= "========================================`n`n"
    msgText .= "[OK] O Device ID foi copiado automaticamente!`n"
    msgText .= "[OK] Cole em qualquer lugar com Ctrl+V`n`n"
    msgText .= "Envie este Device ID para cadastrar a licenca no dashboard.`n`n"
    msgText .= "O programa sera encerrado."
    
    ; Mostra mensagem
    MsgBox, 16, Licenca Invalida, %msgText%
    
    ExitApp
}

; ============================================================================
; SEU CÓDIGO ORIGINAL AQUI
; ============================================================================
```

---

## Método 2: Arquivo Separado

Se você tem vários scripts, pode criar um arquivo separado com as funções.

### Passo 1: Criar arquivo `license_check.ahk`

Crie um arquivo com todas as funções de licenciamento.

### Passo 2: Incluir no seu script

No início do seu script:

```autohotkey
#Include license_check.ahk

; Configuração
global g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
global g_LicenseAPI_Key := "SUA_API_KEY_AQUI"
global g_LicenseAPI_Secret := "SEU_SHARED_SECRET_AQUI"
global g_LicenseAPI_Version := "1.0.0"

; Verificação (mesmo código do Método 1)
deviceId := License_GetDeviceId()
; ... resto do código de verificação
```

**⚠️ Nota:** Este método requer que o arquivo `license_check.ahk` esteja na mesma pasta do seu script.

---

## Exemplo Prático

Aqui está um exemplo completo de um script simples protegido:

```autohotkey
; ============================================================================
; MEU SCRIPT PROTEGIDO
; ============================================================================

; Configuração do sistema de licenças
global g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
global g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
global g_LicenseAPI_Secret := "SEU_SHARED_SECRET_AQUI"
global g_LicenseAPI_Version := "1.0.0"

global g_LicenseVerify_DeviceId := ""
global g_LicenseVerify_Message := ""
global g_LicenseVerify_Offline := false

; ============================================================================
; FUNÇÕES DE LICENCIAMENTO (copie do youtube_tv_standalone.ahk)
; ============================================================================
; ... (cole aqui as 3 funções: License_GetDeviceId, License_SHA256, License_Verify)

; ============================================================================
; VERIFICAÇÃO DE LICENÇA
; ============================================================================
deviceId := License_GetDeviceId()

If (!deviceId Or StrLen(deviceId) < 16) {
    MsgBox, 16, Erro Critico, Nao foi possivel gerar Device ID.
    ExitApp
}

isValid := License_Verify()

If (!isValid) {
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message
    displayDeviceId := g_LicenseVerify_DeviceId ? g_LicenseVerify_DeviceId : deviceId
    Clipboard := displayDeviceId
    
    msgText := "Sua licenca nao e valida ou expirou.`n`n"
    msgText .= "Mensagem: " . g_LicenseVerify_Message . "`n`n"
    msgText .= "Device ID (JA COPIADO!): " . displayDeviceId . "`n`n"
    msgText .= "Envie este Device ID para cadastrar a licenca no dashboard."
    
    MsgBox, 16, Licenca Invalida, %msgText%
    ExitApp
}

; ============================================================================
; SEU CÓDIGO ORIGINAL
; ============================================================================
MsgBox, 64, Sucesso, Licenca verificada! O script pode continuar.

; Seu código aqui...
```

---

## Configuração

### 1. Obter Credenciais

Você precisa de 3 valores:

1. **API_KEY**: Chave de API do servidor
2. **SHARED_SECRET**: Segredo compartilhado para assinatura
3. **BaseURL**: URL do servidor (geralmente `https://api.fartgreen.fun`)

**Como obter:**
- Execute o script `gerar_credenciais.ps1` na pasta raiz
- Ou verifique o arquivo `api/.env`

### 2. Atualizar no Script

Substitua no seu script:

```autohotkey
global g_LicenseAPI_Key := "SUA_API_KEY_AQUI"
global g_LicenseAPI_Secret := "SEU_SHARED_SECRET_AQUI"
```

### 3. Testar

1. Execute o script
2. Se não tiver licença, aparecerá o Device ID
3. Cadastre o Device ID no dashboard
4. Execute novamente - deve funcionar

---

## Troubleshooting

### Erro: "Device ID não encontrado"

**Causa:** Problema de permissões ao salvar o arquivo `device.id`

**Solução:**
- Execute o script como administrador
- Ou verifique se a pasta `%APPDATA%\LicenseSystem` existe

### Erro: "Erro ao gerar assinatura criptográfica"

**Causa:** Problema com SHA256 ou credenciais incorretas

**Solução:**
- Verifique se `g_LicenseAPI_Secret` está correto
- Verifique o arquivo `%TEMP%\license_sig_debug.txt`

### Erro: "Resposta vazia do servidor"

**Causa:** Servidor não acessível ou offline

**Solução:**
- Verifique se o servidor está rodando
- Verifique se `g_LicenseAPI_BaseURL` está correto
- Verifique conexão com internet

### Erro: "Licença inválida ou expirada"

**Causa:** Device ID não cadastrado ou licença expirada

**Solução:**
1. Copie o Device ID exibido
2. Acesse o dashboard
3. Cadastre o Device ID com o tipo de licença desejado

### Script não verifica licença

**Causa:** Funções não foram copiadas corretamente ou código de verificação não foi adicionado

**Solução:**
- Verifique se todas as 3 funções foram copiadas
- Verifique se o código de verificação está no início do script (antes do seu código)

---

## Estrutura Recomendada do Script

```autohotkey
; ============================================================================
; 1. CONFIGURAÇÕES GLOBAIS
; ============================================================================
#NoTrayIcon
#SingleInstance, Force

; ============================================================================
; 2. CONFIGURAÇÃO DO SISTEMA DE LICENÇAS
; ============================================================================
global g_LicenseAPI_BaseURL := "..."
global g_LicenseAPI_Key := "..."
; ... outras variáveis

; ============================================================================
; 3. FUNÇÕES DE LICENCIAMENTO
; ============================================================================
License_GetDeviceId() {
    ; ... código da função
}

License_SHA256(text) {
    ; ... código da função
}

License_Verify() {
    ; ... código da função
}

; ============================================================================
; 4. VERIFICAÇÃO DE LICENÇA (BLOQUEIA SE INVÁLIDA)
; ============================================================================
deviceId := License_GetDeviceId()
isValid := License_Verify()
If (!isValid) {
    ; ... exibe mensagem e encerra
    ExitApp
}

; ============================================================================
; 5. SEU CÓDIGO ORIGINAL
; ============================================================================
; ... resto do seu script aqui
```

---

## Dicas Importantes

1. **Sempre verifique primeiro**: Coloque a verificação de licença no início do script, antes de qualquer outra coisa.

2. **Mantenha as credenciais seguras**: Não compartilhe `API_KEY` e `SHARED_SECRET` publicamente.

3. **Teste sem licença**: Para testar, remova temporariamente o Device ID do banco de dados e veja se a mensagem aparece.

4. **Device ID único**: Cada computador tem um Device ID único baseado no hardware. Não pode ser alterado facilmente.

5. **Compilação**: Ao compilar o script para `.exe`, todas as funções serão incluídas automaticamente.

---

## Suporte

Se tiver problemas:

1. Verifique os arquivos de debug em `%TEMP%\`:
   - `license_debug.txt`
   - `license_response_full.txt`
   - `license_verification_result.txt`

2. Verifique os logs do servidor no terminal do backend

3. Verifique se o Device ID está cadastrado no dashboard

---

**Pronto!** Agora você pode proteger qualquer script AutoHotkey com o sistema de licenças.




