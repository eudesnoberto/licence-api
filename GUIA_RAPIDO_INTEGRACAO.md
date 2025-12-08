# 🚀 Guia Rápido: Como Adicionar Proteção no Seu Arquivo AHK

## 📋 Passo a Passo Simples

### **Passo 1: Abrir o Arquivo com as Funções**

Abra este arquivo no editor:
```
C:\protecao\ahk-client\youtube_tv_standalone.ahk
```

### **Passo 2: Copiar as Configurações**

Copie estas linhas (aproximadamente linhas 17-20):

```autohotkey
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
g_LicenseAPI_Secret := "BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
g_LicenseAPI_Version := "1.0.0"

global g_LicenseVerify_DeviceId := ""
global g_LicenseVerify_Message := ""
global g_LicenseVerify_Offline := false
```

### **Passo 3: Copiar as 3 Funções**

Você precisa copiar **3 funções completas**:

#### **Função 1: `License_GetDeviceId()`**
- **Localização**: Linhas ~25-100
- **Como encontrar**: Busque por `License_GetDeviceId() {`
- **Copie**: Desde `License_GetDeviceId() {` até o `}` final

#### **Função 2: `License_SHA256(text)`**
- **Localização**: Linhas ~102-180
- **Como encontrar**: Busque por `License_SHA256(text) {`
- **Copie**: Desde `License_SHA256(text) {` até o `}` final

#### **Função 3: `License_Verify()`**
- **Localização**: Linhas ~211-500
- **Como encontrar**: Busque por `License_Verify() {`
- **Copie**: Desde `License_Verify() {` até o `}` final

**⚠️ IMPORTANTE**: Copie também estas funções auxiliares que `License_Verify()` usa:
- `License_SHA256_Alt()` (se existir)
- `License_Verify_Offline()` (linhas ~519-626)
- `License_SaveToken()` (linhas ~643-663)
- `License_LoadToken()` (linhas ~665-688)

### **Passo 4: Copiar o Código de Verificação**

Copie este código (aproximadamente linhas 704-750):

```autohotkey
deviceId := License_GetDeviceId()

If (!deviceId Or StrLen(deviceId) < 16) {
    MsgBox, 16, Erro Crítico, Não foi possível gerar Device ID.`n`nTente executar como administrador ou verifique as permissões da pasta.`n`nPasta do script: %A_ScriptDir%
    ExitApp
}

; Verifica licença (tenta online primeiro, depois offline se necessário)
isValid := License_Verify()

; Se falhou e está offline, tenta validar com token salvo (fallback adicional)
If (!isValid And g_LicenseVerify_Offline) {
    tokenJson := License_LoadToken()
    If (tokenJson And StrLen(tokenJson) > 0) {
        isValid := License_Verify_Offline(tokenJson)
        If (isValid) {
            ; Modo offline ativado - permite uso
            g_LicenseVerify_Offline := true
        }
    }
}

; Se licença inválida, exibe erro e encerra
If (!isValid) {
    ; Obtém informações da verificação
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message
    
    ; Garante que temos o Device ID
    displayDeviceId := g_LicenseVerify_DeviceId
    If (!displayDeviceId) {
        displayDeviceId := deviceId
    }
    
    ; Copia Device ID para área de transferência
    Clipboard := displayDeviceId
    
    ; Monta mensagem
    msgText := "Sua licença não é válida ou expirou.`n`n"
    If (g_LicenseVerify_Message) {
        msgText .= "Mensagem: " . g_LicenseVerify_Message . "`n`n"
    }
    msgText .= "========================================`n"
    msgText .= "Device ID (JÁ COPIADO!):`n"
    msgText .= displayDeviceId . "`n"
    msgText .= "========================================`n`n"
    msgText .= "[OK] O Device ID foi copiado automaticamente!`n"
    msgText .= "[OK] Cole em qualquer lugar com Ctrl+V`n`n"
    msgText .= "Envie este Device ID para cadastrar a licença no dashboard.`n`n"
    msgText .= "O programa será encerrado."
    
    ; Mostra mensagem
    MsgBox, 16, Licença Inválida, %msgText%
    
    ExitApp
}
```

### **Passo 5: Colar no Seu Arquivo**

1. Abra seu arquivo `.ahk` no editor
2. Cole tudo no **INÍCIO** do arquivo (antes do seu código)
3. A estrutura deve ficar assim:

```autohotkey
; ============================================================================
; CONFIGURAÇÕES
; ============================================================================
g_LicenseAPI_BaseURL := "..."
g_LicenseAPI_Key := "..."
; ... outras configurações

; ============================================================================
; FUNÇÕES DE LICENCIAMENTO (COPIADAS)
; ============================================================================
License_GetDeviceId() {
    ; ... código copiado
}

License_SHA256(text) {
    ; ... código copiado
}

License_Verify() {
    ; ... código copiado
}

License_Verify_Offline(licenseTokenJson) {
    ; ... código copiado
}

License_SaveToken(licenseTokenJson) {
    ; ... código copiado
}

License_LoadToken() {
    ; ... código copiado
}

; ============================================================================
; VERIFICAÇÃO DE LICENÇA
; ============================================================================
deviceId := License_GetDeviceId()
isValid := License_Verify()
; ... código de verificação

; ============================================================================
; SEU CÓDIGO ORIGINAL AQUI
; ============================================================================
; ... resto do seu script
```

## ✅ Checklist

- [ ] Copiei as configurações (linhas 17-20)
- [ ] Copiei `License_GetDeviceId()` completa
- [ ] Copiei `License_SHA256()` completa
- [ ] Copiei `License_Verify()` completa
- [ ] Copiei `License_Verify_Offline()` completa
- [ ] Copiei `License_SaveToken()` completa
- [ ] Copiei `License_LoadToken()` completa
- [ ] Copiei o código de verificação (linhas 704-750)
- [ ] Colei tudo no INÍCIO do meu arquivo
- [ ] Meu código original está DEPOIS da verificação

## 🎯 Estrutura Final

```
SEU_ARQUIVO.ahk
│
├─ [1] Configurações (g_LicenseAPI_*)
│
├─ [2] Funções de Licenciamento
│   ├─ License_GetDeviceId()
│   ├─ License_SHA256()
│   ├─ License_Verify()
│   ├─ License_Verify_Offline()
│   ├─ License_SaveToken()
│   └─ License_LoadToken()
│
├─ [3] Verificação de Licença
│   └─ (código que verifica e bloqueia se inválida)
│
└─ [4] Seu Código Original
    └─ (resto do seu script)
```

## ⚠️ Dicas Importantes

1. **Salve como UTF-8 com BOM** para exibir acentos corretamente
2. **Teste primeiro** com servidor online para garantir que funciona
3. **Verifique se todas as funções foram copiadas** completamente
4. **Não modifique as funções** copiadas, apenas as configurações

## 🐛 Se Der Erro

### "Function not found"
- Verifique se todas as funções foram copiadas
- Certifique-se de que estão ANTES de serem chamadas

### "Variable not found"
- Verifique se as variáveis `g_LicenseAPI_*` foram definidas
- Certifique-se de que estão no início do script

### "Missing closing brace"
- Verifique se copiou até o `}` final de cada função
- Use um editor com destaque de sintaxe

---

**Pronto!** Agora seu script está protegido! 🛡️

