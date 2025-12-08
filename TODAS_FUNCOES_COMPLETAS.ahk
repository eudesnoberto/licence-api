; ============================================================================
; TODAS AS FUNÇÕES NECESSÁRIAS PARA PROTEÇÃO DE LICENÇA
; ============================================================================
; COPIE ESTE ARQUIVO COMPLETO E COLE NO INÍCIO DO SEU ARQUIVO .ahk
; ANTES DO SEU CÓDIGO ORIGINAL
; ============================================================================

; ============================================================================
; CONFIGURAÇÕES - ALTERE AQUI COM OS VALORES DO SEU SERVIDOR
; ============================================================================
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
g_LicenseAPI_Secret := "BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
g_LicenseAPI_Version := "1.0.0"

; Variáveis globais para resultado da verificação
global g_LicenseVerify_DeviceId := ""
global g_LicenseVerify_Message := ""
global g_LicenseVerify_Offline := false

; Período de graça em dias (quantos dias o sistema pode funcionar offline)
g_LicenseOffline_GracePeriodDays := 7

; ============================================================================
; FUNÇÃO 1: Gera Device ID único baseado no hardware
; ============================================================================
License_GetDeviceId() {
    ; Tenta usar pasta do script primeiro, depois %APPDATA% como fallback
    deviceIdFile := A_ScriptDir . "\device.id"
    deviceIdFileAlt := A_AppData . "\LicenseSystem\device.id"
    
    ; Tenta ler da pasta do script
    IfExist, %deviceIdFile%
    {
        FileRead, deviceId, %deviceIdFile%
        deviceId := Trim(deviceId, " `r`n`t")
        If (StrLen(deviceId) >= 16) {
            return deviceId
        }
    }
    
    ; Tenta ler da pasta alternativa
    IfExist, %deviceIdFileAlt%
    {
        FileRead, deviceId, %deviceIdFileAlt%
        deviceId := Trim(deviceId, " `r`n`t")
        If (StrLen(deviceId) >= 16) {
            ; Copia para pasta do script se conseguir
            FileCopy, %deviceIdFileAlt%, %deviceIdFile%, 1
            return deviceId
        }
    }
    
    ; Gera novo Device ID
    DriveGet, volSerial, Serial, C:
    EnvGet, computerName, COMPUTERNAME
    FormatTime, timestamp, , yyyyMMddHHmmss
    combined := volSerial . computerName . timestamp . A_TickCount
    
    ; Gera hash SHA256 usando PowerShell (com tratamento de erro)
    deviceId := ""
    tempHashFile := A_Temp . "\sha256_" . A_TickCount . ".tmp"
    cmd := "powershell -Command ""try { [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes('" . combined . "'))) -replace '-','' } catch { '' }"""
    
    RunWait, %ComSpec% /c %cmd% > %tempHashFile%, , Hide
    
    ; Lê o hash
    IfExist, %tempHashFile%
    {
        FileRead, hash, %tempHashFile%
        FileDelete, %tempHashFile%
        hash := Trim(hash, " `r`n`t")
        StringLower, hash, hash
        If (StrLen(hash) >= 32) {
            deviceId := SubStr(hash, 1, 32)
        }
    }
    
    ; Se PowerShell falhou, usa método alternativo simples
    If (!deviceId) {
        ; Método alternativo: combina e usa substring
        StringLower, combined, combined
        ; Remove caracteres especiais e limita tamanho
        StringReplace, combined, combined, %A_Space%, , All
        deviceId := SubStr(combined . volSerial . computerName, 1, 32)
    }
    
    ; Tenta salvar na pasta do script
    success := false
    If (deviceId) {
        FileDelete, %deviceIdFile%
        FileAppend, %deviceId%, %deviceIdFile%
        If (!ErrorLevel) {
            success := true
        }
    }
    
    ; Se falhar, tenta salvar em %APPDATA%
    If (!success And deviceId) {
        ; Cria pasta se não existir
        FileCreateDir, %A_AppData%\LicenseSystem
        If (!ErrorLevel) {
            FileDelete, %deviceIdFileAlt%
            FileAppend, %deviceId%, %deviceIdFileAlt%
            If (!ErrorLevel) {
                success := true
            }
        }
    }
    
    ; Retorna o ID mesmo se não conseguir salvar
    return deviceId
}

; ============================================================================
; FUNÇÃO 2: Calcula SHA256 - versão simplificada e mais confiável
; ============================================================================
License_SHA256(text) {
    ; Método usando script PowerShell temporário (compatível com AHK v1.1)
    tempPsFile := A_Temp . "\sha256_" . A_TickCount . ".ps1"
    tempOutFile := A_Temp . "\sha256_out_" . A_TickCount . ".tmp"
    
    ; Escapa apenas aspas simples (substitui ' por '' para PowerShell)
    StringReplace, textEscaped, text, ', '', All
    
    ; Cria script PowerShell simples e direto
    psScript := "$text = '" . textEscaped . "'`n"
    psScript .= "$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)`n"
    psScript .= "$sha256 = [System.Security.Cryptography.SHA256]::Create()`n"
    psScript .= "$hashBytes = $sha256.ComputeHash($bytes)`n"
    psScript .= "$hashString = [System.BitConverter]::ToString($hashBytes) -replace '-',''`n"
    psScript .= "$hashString.ToLower() | Out-File -FilePath '" . tempOutFile . "' -Encoding ASCII -NoNewline`n"
    
    ; Salva script
    FileDelete, %tempPsFile%
    FileAppend, %psScript%, %tempPsFile%
    
    ; Executa script
    RunWait, powershell.exe -ExecutionPolicy Bypass -File "%tempPsFile%", , Hide
    
    ; Lê resultado
    hash := ""
    IfExist, %tempOutFile%
    {
        FileRead, hash, %tempOutFile%
        FileDelete, %tempOutFile%
        hash := Trim(hash, " `r`n`t")
        StringLower, hash, hash
    }
    
    ; Limpa script temporário
    FileDelete, %tempPsFile%
    
    ; Se falhou, tenta método alternativo
    If (!hash Or StrLen(hash) < 64) {
        hash := License_SHA256_Alt(text)
    }
    
    return hash
}

; ============================================================================
; FUNÇÃO 2B: Método alternativo SHA256 (fallback)
; ============================================================================
License_SHA256_Alt(text) {
    tempPsFile := A_Temp . "\sha256_alt_" . A_TickCount . ".ps1"
    tempOutFile := A_Temp . "\sha256_alt_out_" . A_TickCount . ".tmp"
    
    ; Escapa caracteres especiais
    StringReplace, textEscaped, text, ', '', All
    StringReplace, textEscaped, textEscaped, ", `", All
    StringReplace, textEscaped, textEscaped, $, `$, All
    
    ; Cria script PowerShell
    psScript := "$text = '" . textEscaped . "'`n"
    psScript .= "$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)`n"
    psScript .= "$sha256 = [System.Security.Cryptography.SHA256]::Create()`n"
    psScript .= "$hashBytes = $sha256.ComputeHash($bytes)`n"
    psScript .= "$hashString = [System.BitConverter]::ToString($hashBytes) -replace '-',''`n"
    psScript .= "$hashString.ToLower() | Out-File -FilePath '" . tempOutFile . "' -Encoding ASCII -NoNewline`n"
    
    ; Salva e executa
    FileDelete, %tempPsFile%
    FileAppend, %psScript%, %tempPsFile%
    RunWait, powershell.exe -ExecutionPolicy Bypass -File "%tempPsFile%", , Hide
    
    ; Lê resultado
    hash := ""
    IfExist, %tempOutFile%
    {
        FileRead, hash, %tempOutFile%
        FileDelete, %tempOutFile%
        hash := Trim(hash, " `r`n`t")
        StringLower, hash, hash
    }
    
    FileDelete, %tempPsFile%
    return hash
}

; ============================================================================
; FUNÇÃO 3: Verifica licença no servidor (FUNÇÃO PRINCIPAL - MUITO LONGA)
; ============================================================================
; NOTA: Esta função é muito longa. Você precisa copiar ela COMPLETA do arquivo
; youtube_tv_standalone.ahk (linhas ~211-500)
; 
; Por questões de espaço, não está incluída aqui completamente.
; Abra o arquivo C:\protecao\ahk-client\youtube_tv_standalone.ahk
; E copie a função License_Verify() COMPLETA (desde { até })
; ============================================================================

; ============================================================================
; FUNÇÃO 4: Valida token de licença offline
; ============================================================================
License_Verify_Offline(licenseTokenJson) {
    global g_LicenseOffline_GracePeriodDays
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message
    
    g_LicenseVerify_DeviceId := ""
    g_LicenseVerify_Message := ""
    
    If (!licenseTokenJson Or StrLen(licenseTokenJson) = 0) {
        g_LicenseVerify_Message := "Token de licença offline não encontrado"
        return false
    }
    
    ; Extrai payload_raw e signature
    payloadRaw := ""
    signature := ""
    
    If (InStr(licenseTokenJson, """payload_raw"":""") > 0) {
        RegExMatch(licenseTokenJson, """payload_raw"":""([^""]+)""", match)
        If (match1) {
            StringReplace, payloadRaw, match1, \", ", All
            StringReplace, payloadRaw, payloadRaw, \\, \, All
        }
    }
    
    If (InStr(licenseTokenJson, """signature"":""") > 0) {
        RegExMatch(licenseTokenJson, """signature"":""([^""]+)""", match)
        If (match1) {
            signature := match1
        }
    }
    
    If (!payloadRaw Or !signature) {
        g_LicenseVerify_Message := "Token de licença offline inválido"
        return false
    }
    
    ; Extrai informações do payload
    deviceId := ""
    expiresAt := ""
    status := ""
    
    If (InStr(payloadRaw, """device_id"":""") > 0) {
        RegExMatch(payloadRaw, """device_id"":""([^""]+)""", match)
        If (match1) {
            deviceId := match1
        }
    }
    
    If (InStr(payloadRaw, """expires_at"":""") > 0) {
        RegExMatch(payloadRaw, """expires_at"":""([^""]+)""", match)
        If (match1) {
            expiresAt := match1
        }
    } Else If (InStr(payloadRaw, """expires_at"":null") > 0) {
        expiresAt := ""
    }
    
    If (InStr(payloadRaw, """status"":""") > 0) {
        RegExMatch(payloadRaw, """status"":""([^""]+)""", match)
        If (match1) {
            status := match1
        }
    }
    
    If (!deviceId) {
        g_LicenseVerify_Message := "Token de licença offline inválido"
        return false
    }
    
    If (status != "active") {
        g_LicenseVerify_Message := "Licença offline não está ativa"
        return false
    }
    
    currentDeviceId := License_GetDeviceId()
    If (currentDeviceId != deviceId) {
        g_LicenseVerify_Message := "Token não corresponde a este dispositivo"
        return false
    }
    
    ; Verifica expiração com período de graça
    If (expiresAt And StrLen(expiresAt) > 0) {
        FormatTime, currentDate, , yyyyMMdd
        StringReplace, expiresDate, expiresAt, -, , All
        
        currentYear := SubStr(currentDate, 1, 4)
        currentMonth := SubStr(currentDate, 5, 2)
        currentDay := SubStr(currentDate, 7, 2)
        
        expiresYear := SubStr(expiresDate, 1, 4)
        expiresMonth := SubStr(expiresDate, 5, 2)
        expiresDay := SubStr(expiresDate, 7, 2)
        
        currentDays := (currentYear * 365) + (currentMonth * 30) + currentDay
        expiresDays := (expiresYear * 365) + (expiresMonth * 30) + expiresDay
        daysRemaining := expiresDays - currentDays
        
        gracePeriodEnd := daysRemaining + g_LicenseOffline_GracePeriodDays
        If (gracePeriodEnd < 0) {
            g_LicenseVerify_Message := "Licença offline expirada há mais de " . g_LicenseOffline_GracePeriodDays . " dias"
            return false
        }
    }
    
    g_LicenseVerify_DeviceId := deviceId
    g_LicenseVerify_Message := "Licença válida (modo offline)"
    return true
}

; ============================================================================
; FUNÇÃO 5: Salva token de licença para uso offline
; ============================================================================
License_SaveToken(licenseTokenJson) {
    tokenFile := A_ScriptDir . "\license_token.json"
    tokenFileAlt := A_AppData . "\LicenseSystem\license_token.json"
    
    ; Tenta salvar na pasta do script primeiro
    FileDelete, %tokenFile%
    FileAppend, %licenseTokenJson%, %tokenFile%
    If (!ErrorLevel) {
        return true
    }
    
    ; Se falhar, tenta salvar em %APPDATA%
    FileCreateDir, %A_AppData%\LicenseSystem
    If (!ErrorLevel) {
        FileDelete, %tokenFileAlt%
        FileAppend, %licenseTokenJson%, %tokenFileAlt%
        If (!ErrorLevel) {
            return true
        }
    }
    
    return false
}

; ============================================================================
; FUNÇÃO 6: Carrega token de licença salvo
; ============================================================================
License_LoadToken() {
    tokenFile := A_ScriptDir . "\license_token.json"
    tokenFileAlt := A_AppData . "\LicenseSystem\license_token.json"
    
    ; Tenta ler da pasta do script
    IfExist, %tokenFile%
    {
        FileRead, tokenJson, %tokenFile%
        tokenJson := Trim(tokenJson, " `r`n`t")
        If (StrLen(tokenJson) > 0) {
            return tokenJson
        }
    }
    
    ; Tenta ler de %APPDATA%
    IfExist, %tokenFileAlt%
    {
        FileRead, tokenJson, %tokenFileAlt%
        tokenJson := Trim(tokenJson, " `r`n`t")
        If (StrLen(tokenJson) > 0) {
            return tokenJson
        }
    }
    
    return ""
}

; ============================================================================
; VERIFICAÇÃO DE LICENÇA - COLE ESTE CÓDIGO DEPOIS DAS FUNÇÕES
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
; SEU CÓDIGO ORIGINAL AQUI
; ============================================================================
; A partir daqui, seu script pode executar normalmente
; A licença foi verificada e está válida

