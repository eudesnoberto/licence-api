; ============================================================================
; SCRIPT AUXILIAR - Obter Device ID do Computador
; ============================================================================
; Use este script para obter o Device ID de um computador
; Execute este script no PC cliente para ver o Device ID

#SingleInstance,Force

; Inclui o módulo de verificação (que gera o Device ID)
#Include license_check.ahk

; Obtém o Device ID
deviceId := License_GetDeviceId()

; Verifica se o arquivo device.id existe
deviceIdFile := A_ScriptDir . "\device.id"

; Mostra o Device ID de forma clara
MsgBox, 64, Device ID do Computador, 
(
Device ID deste computador:

%deviceId%

Este ID foi salvo no arquivo:
%deviceIdFile%

Copie este ID e envie para cadastrar a licença no dashboard.
)

; Copia o Device ID para a área de transferência
Clipboard := deviceId

; Mostra confirmação
MsgBox, 64, Device ID Copiado, Device ID copiado para a área de transferência!`n`nCole em qualquer lugar com Ctrl+V.

ExitApp





