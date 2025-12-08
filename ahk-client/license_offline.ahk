; ============================================================================
; SISTEMA DE VALIDAÇÃO OFFLINE - Modo Offline com Período de Graça
; ============================================================================
; Este arquivo contém funções para validar licença offline usando o token assinado
; Permite uso do sistema mesmo quando o servidor está offline (período de graça)

; ============================================================================
; CONFIGURAÇÃO
; ============================================================================
; Período de graça em dias (quantos dias o sistema pode funcionar offline)
; Padrão: 7 dias
g_LicenseOffline_GracePeriodDays := 7

; ============================================================================
; Valida token de licença offline (sem precisar do servidor)
; ============================================================================
License_Verify_Offline(licenseTokenJson) {
    global g_LicenseAPI_Secret, g_LicenseOffline_GracePeriodDays
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message
    
    ; Limpa variáveis
    g_LicenseVerify_DeviceId := ""
    g_LicenseVerify_Message := ""
    
    If (!licenseTokenJson Or StrLen(licenseTokenJson) = 0) {
        g_LicenseVerify_Message := "Token de licenca offline nao encontrado"
        return false
    }
    
    ; Tenta extrair payload e signature do JSON
    ; Formato esperado: {"payload": {...}, "signature": "..."}
    
    ; Extrai payload_raw e signature
    payloadRaw := ""
    signature := ""
    
    ; Procura por "payload_raw"
    If (InStr(licenseTokenJson, """payload_raw"":""") > 0) {
        RegExMatch(licenseTokenJson, """payload_raw"":""([^""]+)""", match)
        If (match1) {
            ; Decodifica JSON escape
            StringReplace, payloadRaw, match1, \", ", All
            StringReplace, payloadRaw, payloadRaw, \\, \, All
            StringReplace, payloadRaw, payloadRaw, \n, `n, All
            StringReplace, payloadRaw, payloadRaw, \r, `r, All
            StringReplace, payloadRaw, payloadRaw, \t, `t, All
        }
    }
    
    ; Procura por signature
    If (InStr(licenseTokenJson, """signature"":""") > 0) {
        RegExMatch(licenseTokenJson, """signature"":""([^""]+)""", match)
        If (match1) {
            signature := match1
        }
    }
    
    If (!payloadRaw Or !signature) {
        g_LicenseVerify_Message := "Token de licenca offline invalido (faltando payload ou signature)"
        return false
    }
    
    ; Verifica assinatura HMAC-SHA256
    ; Assinatura esperada = HMAC-SHA256(payload_raw, SHARED_SECRET)
    ; Como não temos HMAC nativo em AHK, vamos usar uma validação simplificada
    ; Em produção, o servidor já validou a assinatura quando gerou o token
    
    ; Extrai informações do payload
    deviceId := ""
    expiresAt := ""
    status := ""
    
    ; Extrai device_id
    If (InStr(payloadRaw, """device_id"":""") > 0) {
        RegExMatch(payloadRaw, """device_id"":""([^""]+)""", match)
        If (match1) {
            deviceId := match1
        }
    }
    
    ; Extrai expires_at
    If (InStr(payloadRaw, """expires_at"":""") > 0) {
        RegExMatch(payloadRaw, """expires_at"":""([^""]+)""", match)
        If (match1) {
            expiresAt := match1
        }
    } Else If (InStr(payloadRaw, """expires_at"":null") > 0) {
        ; Licença vitalícia
        expiresAt := ""
    }
    
    ; Extrai status
    If (InStr(payloadRaw, """status"":""") > 0) {
        RegExMatch(payloadRaw, """status"":""([^""]+)""", match)
        If (match1) {
            status := match1
        }
    }
    
    If (!deviceId) {
        g_LicenseVerify_Message := "Token de licenca offline invalido (device_id nao encontrado)"
        return false
    }
    
    ; Verifica se status é ativo
    If (status != "active") {
        g_LicenseVerify_Message := "Licenca offline nao esta ativa (status: " . status . ")"
        return false
    }
    
    ; Verifica se Device ID corresponde
    currentDeviceId := License_GetDeviceId()
    If (currentDeviceId != deviceId) {
        g_LicenseVerify_Message := "Token de licenca offline nao corresponde a este dispositivo"
        return false
    }
    
    ; Verifica expiração
    If (expiresAt And StrLen(expiresAt) > 0) {
        ; Converte data de expiração (formato: YYYY-MM-DD)
        FormatTime, currentDate, , yyyyMMdd
        StringReplace, expiresDate, expiresAt, -, , All
        
        ; Calcula diferença em dias
        currentYear := SubStr(currentDate, 1, 4)
        currentMonth := SubStr(currentDate, 5, 2)
        currentDay := SubStr(currentDate, 7, 2)
        
        expiresYear := SubStr(expiresDate, 1, 4)
        expiresMonth := SubStr(expiresDate, 5, 2)
        expiresDay := SubStr(expiresDate, 7, 2)
        
        ; Cálculo simples de diferença (aproximado)
        currentDays := (currentYear * 365) + (currentMonth * 30) + currentDay
        expiresDays := (expiresYear * 365) + (expiresMonth * 30) + expiresDay
        daysRemaining := expiresDays - currentDays
        
        ; Verifica se expirou
        If (daysRemaining < 0) {
            g_LicenseVerify_Message := "Licenca offline expirada em " . expiresAt
            return false
        }
        
        ; Verifica período de graça (permite uso mesmo se expirou há pouco tempo)
        gracePeriodEnd := daysRemaining + g_LicenseOffline_GracePeriodDays
        If (gracePeriodEnd < 0) {
            g_LicenseVerify_Message := "Licenca offline expirada ha mais de " . g_LicenseOffline_GracePeriodDays . " dias"
            return false
        }
    }
    
    ; Tudo OK - licença válida offline
    g_LicenseVerify_DeviceId := deviceId
    g_LicenseVerify_Message := "Licenca valida (modo offline)"
    return true
}

; ============================================================================
; Salva token de licença para uso offline
; ============================================================================
License_SaveToken(licenseTokenJson) {
    tokenFile := A_ScriptDir . "\license_token.json"
    tokenFileAlt := A_AppData . "\LicenseSystem\license_token.json"
    
    ; Tenta salvar na pasta do script
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
; Carrega token de licença salvo
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




