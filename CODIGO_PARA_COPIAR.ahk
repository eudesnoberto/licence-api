; ============================================================================
; CÓDIGO PARA COPIAR NO SEU ARQUIVO FONTE
; ============================================================================
; Copie este código e cole no INÍCIO do seu arquivo .ahk
; ANTES do seu código original
; ============================================================================

; ============================================================================
; 1. CONFIGURAÇÕES - ALTERE AQUI COM OS VALORES DO SEU SERVIDOR
; ============================================================================
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
g_LicenseAPI_Secret := "BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
g_LicenseAPI_Version := "1.0.0"

; Variáveis globais para resultado da verificação
global g_LicenseVerify_DeviceId := ""
global g_LicenseVerify_Message := ""
global g_LicenseVerify_Offline := false

; ============================================================================
; 2. COPIE AS 3 FUNÇÕES DO ARQUIVO youtube_tv_standalone.ahk
; ============================================================================
; Você precisa copiar estas 3 funções COMPLETAS:
;
; 1. License_GetDeviceId() - Linhas ~25-100
; 2. License_SHA256() - Linhas ~102-180  
; 3. License_Verify() - Linhas ~211-500
;
; Abra o arquivo: C:\protecao\ahk-client\youtube_tv_standalone.ahk
; E copie as 3 funções completas (desde o { até o } final)
; ============================================================================

; ============================================================================
; 3. VERIFICAÇÃO DE LICENÇA - COLE ESTE CÓDIGO DEPOIS DAS FUNÇÕES
; ============================================================================
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

; ============================================================================
; 4. SEU CÓDIGO ORIGINAL AQUI
; ============================================================================
; A partir daqui, seu script pode executar normalmente
; A licença foi verificada e está válida

; ... seu código original continua aqui ...

