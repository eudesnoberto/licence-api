; ============================================================================
; EXEMPLO DE INTEGRAÇÃO - Como proteger seu script AutoHotkey
; ============================================================================

#SingleInstance,Force

; ============================================================================
; PASSO 1: Inclua o módulo de verificação no início do script
; ============================================================================
#Include license_verify.ahk

; ============================================================================
; PASSO 2: Verifique a licença ANTES de qualquer outra coisa
; ============================================================================
licenseResult := License_Verify()

If (!licenseResult.allow) {
    ; Se não tiver licença válida, bloqueia a execução
    License_ShowError(licenseResult.msg . "`n`nDevice ID: " . licenseResult.deviceId)
    ExitApp
}

; ============================================================================
; PASSO 3: Se chegou aqui, a licença é válida - continue normalmente
; ============================================================================

; Seu código original começa aqui...
MsgBox, 0, Licença OK, Licença verificada com sucesso!`nDevice ID: %licenseResult.deviceId%

; Exemplo: seu código original
; #Include performace.ahk
; IniRead, leter, %A_WorkingDir%\config.ini, Teclas, youtube
; ... resto do código ...

return





