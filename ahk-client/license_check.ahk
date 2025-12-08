; ============================================================================
; VERIFICAÇÃO MÍNIMA DE LICENÇA
; Use este arquivo se você NÃO quer modificar seu código original
; ============================================================================

; Configurações (ALTERE AQUI)
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "change_me_secret_key"
g_LicenseAPI_Secret := "change_me_shared_secret"
g_LicenseAPI_Version := "1.0.0"

; ============================================================================
; Gera Device ID único baseado no hardware
; ============================================================================
License_GetDeviceId() {
    deviceIdFile := A_ScriptDir . "\device.id"
    
    IfExist, %deviceIdFile%
    {
        FileRead, deviceId, %deviceIdFile%
        deviceId := Trim(deviceId, " `r`n`t")
        If (StrLen(deviceId) >= 16) {
            return deviceId
        }
    }
    
    DriveGet, volSerial, Serial, C:
    EnvGet, computerName, COMPUTERNAME
    FormatTime, timestamp, , yyyyMMddHHmmss
    combined := volSerial . computerName . timestamp . A_TickCount
    
    cmd := "powershell -Command ""[System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes('" . combined . "'))) -replace '-',''"""
    RunWait, %ComSpec% /c %cmd% > %A_Temp%\sha256.tmp, , Hide
    FileRead, hash, %A_Temp%\sha256.tmp
    FileDelete, %A_Temp%\sha256.tmp
    hash := Trim(hash, " `r`n`t")
    StringLower, hash, hash
    deviceId := SubStr(hash, 1, 32)
    
    FileDelete, %deviceIdFile%
    FileAppend, %deviceId%, %deviceIdFile%
    return deviceId
}

; ============================================================================
; Calcula SHA256
; ============================================================================
License_SHA256(text) {
    cmd := "powershell -Command ""[System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes('" . text . "'))) -replace '-',''"""
    RunWait, %ComSpec% /c %cmd% > %A_Temp%\sha256.tmp, , Hide
    FileRead, hash, %A_Temp%\sha256.tmp
    FileDelete, %A_Temp%\sha256.tmp
    hash := Trim(hash, " `r`n`t")
    StringLower, hash, hash
    return hash
}

; ============================================================================
; Verifica licença no servidor
; ============================================================================
License_Verify() {
    global g_LicenseAPI_BaseURL, g_LicenseAPI_Key, g_LicenseAPI_Secret, g_LicenseAPI_Version
    
    deviceId := License_GetDeviceId()
    If (!deviceId) {
        return false
    }
    
    FormatTime, timestamp, , yyyyMMddHHmmss
    combined := deviceId . "|" . g_LicenseAPI_Version . "|" . timestamp . "|" . g_LicenseAPI_Secret
    signature := License_SHA256(combined)
    
    EnvGet, hostname, COMPUTERNAME
    EnvGet, username, USERNAME
    
    url := g_LicenseAPI_BaseURL . "/verify"
    url .= "?id=" . deviceId
    url .= "&version=" . g_LicenseAPI_Version
    url .= "&ts=" . timestamp
    url .= "&sig=" . signature
    url .= "&api_key=" . g_LicenseAPI_Key
    url .= "&hostname=" . hostname
    url .= "&username=" . username
    
    cmd := "powershell -Command ""try { $r = Invoke-WebRequest -Uri '" . url . "' -TimeoutSec 10 -UseBasicParsing; $r.Content } catch { 'ERROR:' + $_.Exception.Message }"""
    tempFile := A_Temp . "\license_" . A_TickCount . ".tmp"
    RunWait, %ComSpec% /c %cmd% > %tempFile%, , Hide
    FileRead, response, %tempFile%
    FileDelete, %tempFile%
    response := Trim(response, " `r`n`t")
    
    If (InStr(response, "ERROR:") = 1) {
        return false
    }
    
    If (InStr(response, """allow"":true") > 0) {
        return true
    }
    
    return false
}

; ============================================================================
; VERIFICAÇÃO NO INÍCIO - BLOQUEIA SE NÃO TIVER LICENÇA
; ============================================================================
If (!License_Verify()) {
    deviceId := License_GetDeviceId()
    MsgBox, 16, Licença Inválida, Sua licença não é válida ou expirou.`n`nDevice ID: %deviceId%`n`nEntre em contato com o suporte.
    ExitApp
}





