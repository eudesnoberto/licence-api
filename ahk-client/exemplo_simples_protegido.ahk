; ============================================================================
; EXEMPLO: Script Simples Protegido com Sistema de Licenças
; ============================================================================
; Este é um exemplo mínimo de como integrar o sistema de proteção
; em qualquer script AutoHotkey.

#NoTrayIcon
#SingleInstance, Force

; ============================================================================
; CONFIGURAÇÃO DO SISTEMA DE LICENÇAS
; ============================================================================
; IMPORTANTE: Substitua pelos valores corretos do seu servidor
global g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
global g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
global g_LicenseAPI_Secret := "SEU_SHARED_SECRET_AQUI"  ; ⚠️ SUBSTITUA AQUI
global g_LicenseAPI_Version := "1.0.0"

; Variáveis globais para resultado da verificação
global g_LicenseVerify_DeviceId := ""
global g_LicenseVerify_Message := ""
global g_LicenseVerify_Offline := false

; ============================================================================
; NOTA: As funções License_GetDeviceId(), License_SHA256() e License_Verify()
; devem ser copiadas do arquivo youtube_tv_standalone.ahk
; 
; Por questões de espaço, não estão incluídas aqui, mas você pode:
; 1. Copiar as funções do arquivo original (linhas ~23-431)
; 2. Ou usar #Include se criar um arquivo separado
; ============================================================================

; ============================================================================
; VERIFICAÇÃO DE LICENÇA - BLOQUEIA SE NÃO TIVER LICENÇA
; ============================================================================
deviceId := License_GetDeviceId()

If (!deviceId Or StrLen(deviceId) < 16) {
    MsgBox, 16, Erro Critico, Nao foi possivel gerar Device ID.`n`nTente executar como administrador ou verifique as permissoes da pasta.`n`nPasta do script: %A_ScriptDir%
    ExitApp
}

; Verifica licença
isValid := License_Verify()

If (!isValid) {
    ; Obtém informações da verificação
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message
    
    ; Garante que temos o Device ID
    displayDeviceId := g_LicenseVerify_DeviceId
    If (!displayDeviceId) {
        displayDeviceId := deviceId
    }
    
    ; Copia Device ID para área de transferência ANTES de mostrar mensagem
    Clipboard := displayDeviceId
    
    ; Monta mensagem melhorada
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
; A partir daqui, seu script pode executar normalmente
; A licença foi verificada e está válida

MsgBox, 64, Licenca Valida, Licenca verificada com sucesso!`n`nDevice ID: %deviceId%`n`nO script continuara normalmente.

; Exemplo: seu código aqui
; Hotkey, ^j, MeuComando
; return
;
; MeuComando:
;     MsgBox, Você pressionou Ctrl+J!
; return

; ... resto do seu código ...




