; ============================================================================
; Módulo de Verificação de Licença
; Compatível com AutoHotkey v1.1
; ============================================================================

; Carrega configurações do arquivo INI (se existir)
License_LoadConfig() {
    global
    configFile := A_ScriptDir . "\config_license.ini"
    
    ; Valores padrão
    g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
    g_LicenseAPI_Key := "change_me_secret_key"
    g_LicenseAPI_Secret := "change_me_shared_secret"
    g_LicenseAPI_Version := "1.0.0"
    g_LicenseAPI_Timeout := 10000
    
    ; Tenta carregar do INI
    IfExist, %configFile%
    {
        IniRead, url, %configFile%, License, API_URL, %g_LicenseAPI_BaseURL%
        IniRead, key, %configFile%, License, API_KEY, %g_LicenseAPI_Key%
        IniRead, secret, %configFile%, License, SHARED_SECRET, %g_LicenseAPI_Secret%
        IniRead, version, %configFile%, License, VERSION, %g_LicenseAPI_Version%
        IniRead, timeout, %configFile%, License, TIMEOUT, %g_LicenseAPI_Timeout%
        
        g_LicenseAPI_BaseURL := url
        g_LicenseAPI_Key := key
        g_LicenseAPI_Secret := secret
        g_LicenseAPI_Version := version
        g_LicenseAPI_Timeout := timeout
    }
}

; Inicializa configurações
License_LoadConfig()

; ============================================================================
; Gera ou recupera o Device ID
; ============================================================================
License_GetDeviceId() {
    global
    deviceIdFile := A_ScriptDir . "\device.id"
    
    ; Tenta ler o ID existente
    IfExist, %deviceIdFile%
    {
        FileRead, deviceId, %deviceIdFile%
        deviceId := Trim(deviceId, " `r`n`t")
        If (StrLen(deviceId) >= 16) {
            return deviceId
        }
    }
    
    ; Gera um novo ID (baseado em hardware + timestamp)
    ; Usa Volume Serial Number + Computer Name + Timestamp
    DriveGet, volSerial, Serial, C:
    EnvGet, computerName, COMPUTERNAME
    FormatTime, timestamp, , yyyyMMddHHmmss
    
    ; Combina e faz hash simples (MD5-like usando SHA256)
    combined := volSerial . computerName . timestamp . A_TickCount
    deviceId := License_SHA256(combined)
    deviceId := SubStr(deviceId, 1, 32)  ; Primeiros 32 caracteres
    
    ; Salva o ID
    FileDelete, %deviceIdFile%
    FileAppend, %deviceId%, %deviceIdFile%
    
    return deviceId
}

; ============================================================================
; Calcula SHA256 (simplificado usando PowerShell)
; ============================================================================
License_SHA256(text) {
    ; Usa PowerShell para calcular SHA256
    cmd := "powershell -Command ""[System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes('" . text . "'))) -replace '-',''"""
    
    ; Executa e captura resultado
    RunWait, %ComSpec% /c %cmd% > %A_Temp%\sha256.tmp, , Hide
    FileRead, hash, %A_Temp%\sha256.tmp
    FileDelete, %A_Temp%\sha256.tmp
    
    hash := Trim(hash, " `r`n`t")
    StringLower, hash, hash
    return hash
}

; ============================================================================
; Gera timestamp no formato YYYYMMDDHHmmss
; ============================================================================
License_GetTimestamp() {
    FormatTime, ts, , yyyyMMddHHmmss
    return ts
}

; ============================================================================
; Gera assinatura SHA256 para a requisição
; ============================================================================
License_GenerateSignature(deviceId, version, timestamp) {
    global g_LicenseAPI_Secret
    combined := deviceId . "|" . version . "|" . timestamp . "|" . g_LicenseAPI_Secret
    return License_SHA256(combined)
}

; ============================================================================
; Faz requisição HTTP GET (usando PowerShell)
; ============================================================================
License_HttpGet(url) {
    global g_LicenseAPI_Timeout
    
    ; Usa PowerShell Invoke-WebRequest
    cmd := "powershell -Command ""try { $r = Invoke-WebRequest -Uri '" . url . "' -TimeoutSec " . (g_LicenseAPI_Timeout / 1000) . " -UseBasicParsing; $r.Content } catch { Write-Output 'ERROR:' $_.Exception.Message }"""
    
    tempFile := A_Temp . "\license_response_" . A_TickCount . ".tmp"
    RunWait, %ComSpec% /c %cmd% > %tempFile%, , Hide
    
    FileRead, response, %tempFile%
    FileDelete, %tempFile%
    
    ; Remove BOM e espaços
    response := Trim(response, " `r`n`t")
    
    ; Verifica se é erro
    If (InStr(response, "ERROR:") = 1) {
        return "ERROR:" . SubStr(response, 7)
    }
    
    return response
}

; ============================================================================
; Verifica a licença no servidor
; Retorna: objeto com allow, msg, config
; ============================================================================
License_Verify() {
    global g_LicenseAPI_BaseURL, g_LicenseAPI_Key, g_LicenseAPI_Version
    
    ; Obtém device ID
    deviceId := License_GetDeviceId()
    If (!deviceId) {
        return {allow: false, msg: "Erro ao gerar Device ID"}
    }
    
    ; Prepara parâmetros
    timestamp := License_GetTimestamp()
    signature := License_GenerateSignature(deviceId, g_LicenseAPI_Version, timestamp)
    
    ; Obtém informações do sistema
    EnvGet, hostname, COMPUTERNAME
    EnvGet, username, USERNAME
    
    ; Monta URL
    url := g_LicenseAPI_BaseURL . "/verify"
    url .= "?id=" . deviceId
    url .= "&version=" . g_LicenseAPI_Version
    url .= "&ts=" . timestamp
    url .= "&sig=" . signature
    url .= "&api_key=" . g_LicenseAPI_Key
    url .= "&hostname=" . hostname
    url .= "&username=" . username
    
    ; Faz requisição
    response := License_HttpGet(url)
    
    ; Verifica erro de rede
    If (InStr(response, "ERROR:") = 1) {
        return {allow: false, msg: "Erro de conexão: " . SubStr(response, 7), offline: true}
    }
    
    ; Parse JSON (simplificado)
    ; Procura por "allow":true ou "allow":false
    allow := false
    msg := "Resposta inválida do servidor"
    
    If (InStr(response, """allow"":true") > 0) {
        allow := true
        msg := "Licença válida"
    } Else If (InStr(response, """allow"":false") > 0) {
        allow := false
        ; Tenta extrair mensagem
        RegExMatch(response, """msg"":""([^""]+)""", match)
        If (match1) {
            msg := match1
        } Else {
            msg := "Licença inválida ou expirada"
        }
    }
    
    return {allow: allow, msg: msg, deviceId: deviceId}
}

; ============================================================================
; Exibe mensagem de erro e encerra o script
; ============================================================================
License_ShowError(msg, allowOffline := false) {
    If (allowOffline) {
        ; Modo offline - permite continuar (opcional)
        MsgBox, 48, Licença - Modo Offline, %msg%`n`nO programa continuará em modo limitado.
        return
    }
    
    ; Bloqueia execução
    MsgBox, 16, Erro de Licença, %msg%`n`nO programa será encerrado.
    ExitApp
}

