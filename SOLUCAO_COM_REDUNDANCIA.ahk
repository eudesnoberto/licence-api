; ============================================================================
; SOLUÇÃO COMPLETA COM REDUNDÂNCIA DE SERVIDORES
; ============================================================================
; Este arquivo suporta múltiplos servidores para alta disponibilidade
; Se um servidor cair, tenta automaticamente o próximo
; ============================================================================

; ============================================================================
; CONFIGURAÇÕES - SERVIDORES COM REDUNDÂNCIA
; ============================================================================
; Configure múltiplos servidores em ordem de prioridade
; O sistema tentará cada servidor até encontrar um que funcione

; MÉTODO 1: Array de servidores (RECOMENDADO)
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://api.fartgreen.fun"        ; Servidor Principal
g_LicenseAPI_Servers[2] := "https://api-backup1.fartgreen.fun" ; Backup 1
g_LicenseAPI_Servers[3] := "https://api-backup2.fartgreen.fun" ; Backup 2

; OU MÉTODO 2: Servidor único (compatibilidade)
; Descomente se quiser usar apenas um servidor:
; g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"

; Configurações de API
g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
g_LicenseAPI_Secret := "BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
g_LicenseAPI_Version := "1.0.0"

global g_LicenseVerify_DeviceId := ""
global g_LicenseVerify_Message := ""
global g_LicenseVerify_Offline := false
g_LicenseOffline_GracePeriodDays := 7

; ============================================================================
; FUNÇÃO: Obtém servidor atual (com suporte a redundância)
; ============================================================================
License_GetCurrentServer(serverIndex := 1) {
    global g_LicenseAPI_Servers, g_LicenseAPI_BaseURL
    
    ; Se usar array de servidores
    If (IsObject(g_LicenseAPI_Servers) And g_LicenseAPI_Servers.Length() > 0) {
        If (serverIndex <= g_LicenseAPI_Servers.Length()) {
            return g_LicenseAPI_Servers[serverIndex]
        }
    }
    
    ; Fallback para servidor único (compatibilidade)
    If (g_LicenseAPI_BaseURL) {
        return g_LicenseAPI_BaseURL
    }
    
    ; Fallback padrão
    return "https://api.fartgreen.fun"
}

; ============================================================================
; FUNÇÃO 1: License_GetDeviceId()
; ============================================================================
License_GetDeviceId() {
    deviceIdFile := A_ScriptDir . "\device.id"
    deviceIdFileAlt := A_AppData . "\LicenseSystem\device.id"
    
    IfExist, %deviceIdFile%
    {
        FileRead, deviceId, %deviceIdFile%
        deviceId := Trim(deviceId, " `r`n`t")
        If (StrLen(deviceId) >= 16) {
            return deviceId
        }
    }
    
    IfExist, %deviceIdFileAlt%
    {
        FileRead, deviceId, %deviceIdFileAlt%
        deviceId := Trim(deviceId, " `r`n`t")
        If (StrLen(deviceId) >= 16) {
            FileCopy, %deviceIdFileAlt%, %deviceIdFile%, 1
            return deviceId
        }
    }
    
    DriveGet, volSerial, Serial, C:
    EnvGet, computerName, COMPUTERNAME
    FormatTime, timestamp, , yyyyMMddHHmmss
    combined := volSerial . computerName . timestamp . A_TickCount
    
    deviceId := ""
    tempHashFile := A_Temp . "\sha256_" . A_TickCount . ".tmp"
    cmd := "powershell -Command ""try { [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes('" . combined . "'))) -replace '-','' } catch { '' }"""
    
    RunWait, %ComSpec% /c %cmd% > %tempHashFile%, , Hide
    
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
    
    If (!deviceId) {
        StringLower, combined, combined
        StringReplace, combined, combined, %A_Space%, , All
        deviceId := SubStr(combined . volSerial . computerName, 1, 32)
    }
    
    success := false
    If (deviceId) {
        FileDelete, %deviceIdFile%
        FileAppend, %deviceId%, %deviceIdFile%
        If (!ErrorLevel) {
            success := true
        }
    }
    
    If (!success And deviceId) {
        FileCreateDir, %A_AppData%\LicenseSystem
        If (!ErrorLevel) {
            FileDelete, %deviceIdFileAlt%
            FileAppend, %deviceId%, %deviceIdFileAlt%
            If (!ErrorLevel) {
                success := true
            }
        }
    }
    
    return deviceId
}

; ============================================================================
; FUNÇÃO 2: License_SHA256()
; ============================================================================
License_SHA256(text) {
    tempPsFile := A_Temp . "\sha256_" . A_TickCount . ".ps1"
    tempOutFile := A_Temp . "\sha256_out_" . A_TickCount . ".tmp"
    
    StringReplace, textEscaped, text, ', '', All
    
    psScript := "$text = '" . textEscaped . "'`n"
    psScript .= "$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)`n"
    psScript .= "$sha256 = [System.Security.Cryptography.SHA256]::Create()`n"
    psScript .= "$hashBytes = $sha256.ComputeHash($bytes)`n"
    psScript .= "$hashString = [System.BitConverter]::ToString($hashBytes) -replace '-',''`n"
    psScript .= "$hashString.ToLower() | Out-File -FilePath '" . tempOutFile . "' -Encoding ASCII -NoNewline`n"
    
    FileDelete, %tempPsFile%
    FileAppend, %psScript%, %tempPsFile%
    RunWait, powershell.exe -ExecutionPolicy Bypass -File "%tempPsFile%", , Hide
    
    hash := ""
    IfExist, %tempOutFile%
    {
        FileRead, hash, %tempOutFile%
        FileDelete, %tempOutFile%
        hash := Trim(hash, " `r`n`t")
        StringLower, hash, hash
    }
    
    FileDelete, %tempPsFile%
    
    If (!hash Or StrLen(hash) < 64) {
        hash := License_SHA256_Alt(text)
    }
    
    return hash
}

; ============================================================================
; FUNÇÃO 2B: License_SHA256_Alt()
; ============================================================================
License_SHA256_Alt(text) {
    tempPsFile := A_Temp . "\sha256_alt_" . A_TickCount . ".ps1"
    tempOutFile := A_Temp . "\sha256_alt_out_" . A_TickCount . ".tmp"
    
    StringReplace, textEscaped, text, ', '', All
    StringReplace, textEscaped, textEscaped, ", `", All
    StringReplace, textEscaped, textEscaped, $, `$, All
    
    psScript := "$text = '" . textEscaped . "'`n"
    psScript .= "$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)`n"
    psScript .= "$sha256 = [System.Security.Cryptography.SHA256]::Create()`n"
    psScript .= "$hashBytes = $sha256.ComputeHash($bytes)`n"
    psScript .= "$hashString = [System.BitConverter]::ToString($hashBytes) -replace '-',''`n"
    psScript .= "$hashString.ToLower() | Out-File -FilePath '" . tempOutFile . "' -Encoding ASCII -NoNewline`n"
    
    FileDelete, %tempPsFile%
    FileAppend, %psScript%, %tempPsFile%
    RunWait, powershell.exe -ExecutionPolicy Bypass -File "%tempPsFile%", , Hide
    
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
; FUNÇÃO 3: License_Verify() - COM SUPORTE A REDUNDÂNCIA
; ============================================================================
License_Verify() {
    global g_LicenseAPI_Key, g_LicenseAPI_Secret, g_LicenseAPI_Version
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message, g_LicenseVerify_Offline
    global g_LicenseAPI_Servers
    
    g_LicenseVerify_DeviceId := ""
    g_LicenseVerify_Message := ""
    g_LicenseVerify_Offline := false
    
    deviceId := License_GetDeviceId()
    If (!deviceId) {
        g_LicenseVerify_Message := "Erro ao gerar Device ID"
        return false
    }
    
    g_LicenseVerify_DeviceId := deviceId
    
    FormatTime, timestamp, , yyyyMMddHHmmss
    combined := deviceId . "|" . g_LicenseAPI_Version . "|" . timestamp . "|" . g_LicenseAPI_Secret
    signature := License_SHA256(combined)
    
    sigLen := StrLen(signature)
    If (!signature Or sigLen = 0 Or sigLen < 64) {
        signature := License_SHA256_Alt(combined)
        sigLen := StrLen(signature)
        If (!signature Or sigLen = 0 Or sigLen < 64) {
            g_LicenseVerify_Message := "Erro ao gerar assinatura criptográfica"
            return false
        }
    }
    
    EnvGet, hostname, COMPUTERNAME
    EnvGet, username, USERNAME
    StringReplace, hostname, hostname, %A_Space%, `%20, All
    StringReplace, username, username, %A_Space%, `%20, All
    
    ; ========================================================================
    ; TENTA CADA SERVIDOR EM ORDEM (REDUNDÂNCIA)
    ; ========================================================================
    maxServers := 1
    If (IsObject(g_LicenseAPI_Servers)) {
        maxServers := g_LicenseAPI_Servers.Length()
    }
    
    Loop, %maxServers%
    {
        currentServer := License_GetCurrentServer(A_Index)
        
        ; Monta URL para este servidor
        url := currentServer . "/verify"
        url .= "?id=" . deviceId
        url .= "&version=" . g_LicenseAPI_Version
        url .= "&ts=" . timestamp
        url .= "&sig=" . signature
        url .= "&api_key=" . g_LicenseAPI_Key
        url .= "&hostname=" . hostname
        url .= "&username=" . username
        
        ; Faz requisição
        tempFile := A_Temp . "\license_resp_" . A_TickCount . "_" . A_Index . ".tmp"
        tempPsFile := A_Temp . "\license_ps_" . A_TickCount . "_" . A_Index . ".ps1"
        
        psScript := "$ErrorActionPreference = 'Continue'`n"
        psScript .= "try {`n"
        psScript .= "  $response = Invoke-WebRequest -Uri '" . url . "' -TimeoutSec 10 -UseBasicParsing`n"
        psScript .= "  $response.Content | Out-File -FilePath '" . tempFile . "' -Encoding UTF8 -NoNewline`n"
        psScript .= "} catch {`n"
        psScript .= "  if ($_.Exception.Response) {`n"
        psScript .= "    try {`n"
        psScript .= "      $stream = $_.Exception.Response.GetResponseStream()`n"
        psScript .= "      $stream.Position = 0`n"
        psScript .= "      $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)`n"
        psScript .= "      $content = $reader.ReadToEnd()`n"
        psScript .= "      $reader.Close()`n"
        psScript .= "      $stream.Close()`n"
        psScript .= "      if ($content) {`n"
        psScript .= "        $content | Out-File -FilePath '" . tempFile . "' -Encoding UTF8 -NoNewline`n"
        psScript .= "      } else {`n"
        psScript .= "        ('ERROR: HTTP ' + $_.Exception.Response.StatusCode.value__ + ' - ' + $_.Exception.Message) | Out-File -FilePath '" . tempFile . "' -Encoding UTF8 -NoNewline`n"
        psScript .= "      }`n"
        psScript .= "    } catch {`n"
        psScript .= "      ('ERROR: ' + $_.Exception.Message) | Out-File -FilePath '" . tempFile . "' -Encoding UTF8 -NoNewline`n"
        psScript .= "    }`n"
        psScript .= "  } else {`n"
        psScript .= "    ('ERROR: ' + $_.Exception.Message) | Out-File -FilePath '" . tempFile . "' -Encoding UTF8 -NoNewline`n"
        psScript .= "  }`n"
        psScript .= "}`n"
        
        FileDelete, %tempPsFile%
        FileAppend, %psScript%, %tempPsFile%
        RunWait, powershell.exe -ExecutionPolicy Bypass -File "%tempPsFile%", , Hide
        
        response := ""
        IfExist, %tempFile%
        {
            FileRead, response, %tempFile%
            FileDelete, %tempFile%
            response := Trim(response, " `r`n`t")
        }
        
        FileDelete, %tempPsFile%
        
        ; Se obteve resposta válida (não é erro), processa
        If (response And StrLen(response) > 0 And InStr(response, "ERROR:") != 1) {
            ; Verifica se é sucesso
            allowTrue := false
            If (InStr(response, """allow"":true") > 0) {
                allowTrue := true
            } Else If (InStr(response, """allow"": true") > 0) {
                allowTrue := true
            }
            
            If (allowTrue) {
                ; Salva token para offline
                tokenSaved := false
                If (InStr(response, """license_token"":") > 0) {
                    startPos := InStr(response, """license_token"":")
                    If (startPos > 0) {
                        pos := startPos + 17
                        While (pos <= StrLen(response) And (SubStr(response, pos, 1) = " " Or SubStr(response, pos, 1) = "`t")) {
                            pos++
                        }
                        
                        If (pos <= StrLen(response) And SubStr(response, pos, 1) = "{") {
                            bracketCount := 0
                            tokenJson := ""
                            
                            Loop, % StrLen(response)
                            {
                                If (pos > StrLen(response)) {
                                    Break
                                }
                                char := SubStr(response, pos, 1)
                                
                                If (char = "{") {
                                    bracketCount++
                                } Else If (char = "}") {
                                    bracketCount--
                                }
                                
                                tokenJson .= char
                                pos++
                                
                                If (bracketCount = 0) {
                                    Break
                                }
                            }
                            
                            tokenJsonLen := StrLen(tokenJson)
                            If (tokenJsonLen > 20 And InStr(tokenJson, "{") = 1 And SubStr(tokenJson, -1) = "}") {
                                If (License_SaveToken(tokenJson)) {
                                    tokenSaved := true
                                }
                            }
                        }
                    }
                }
                
                ; Log de sucesso com servidor usado
                FileAppend, Licença válida - Servidor usado: %currentServer% (índice: %A_Index%)`n, %A_Temp%\license_server_used.txt
                
                g_LicenseVerify_Message := "Licença válida"
                return true
            }
            
            ; Se foi negado explicitamente
            allowFalse := false
            If (InStr(response, """allow"":false") > 0) {
                allowFalse := true
            } Else If (InStr(response, """allow"": false") > 0) {
                allowFalse := true
            }
            
            If (allowFalse) {
                msg := "Licença inválida ou expirada"
                If (InStr(response, """msg"":""") > 0) {
                    RegExMatch(response, """msg"":""([^""]+)""", match)
                    If (match1) {
                        msg := match1
                    }
                }
                g_LicenseVerify_Message := msg
                return false
            }
        }
        
        ; Se chegou aqui, este servidor falhou - tenta próximo
        If (A_Index < maxServers) {
            FileAppend, Servidor %A_Index% falhou (%currentServer%) - Tentando próximo...`n, %A_Temp%\license_server_failover.txt
            Continue
        }
    }
    
    ; Se todos os servidores falharam, tenta modo offline
    g_LicenseVerify_Message := "Todos os servidores indisponíveis"
    g_LicenseVerify_Offline := true
    
    tokenJson := License_LoadToken()
    If (tokenJson And StrLen(tokenJson) > 0) {
        offlineValid := License_Verify_Offline(tokenJson)
        If (offlineValid) {
            g_LicenseVerify_Message := "Licença válida (modo offline - todos os servidores indisponíveis)"
            g_LicenseVerify_Offline := true
            return true
        }
    }
    
    return false
}

; ============================================================================
; FUNÇÃO 4: License_Verify_Offline()
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
; FUNÇÃO 5: License_SaveToken()
; ============================================================================
License_SaveToken(licenseTokenJson) {
    tokenFile := A_ScriptDir . "\license_token.json"
    tokenFileAlt := A_AppData . "\LicenseSystem\license_token.json"
    
    FileDelete, %tokenFile%
    FileAppend, %licenseTokenJson%, %tokenFile%
    If (!ErrorLevel) {
        return true
    }
    
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
; FUNÇÃO 6: License_LoadToken()
; ============================================================================
License_LoadToken() {
    tokenFile := A_ScriptDir . "\license_token.json"
    tokenFileAlt := A_AppData . "\LicenseSystem\license_token.json"
    
    IfExist, %tokenFile%
    {
        FileRead, tokenJson, %tokenFile%
        tokenJson := Trim(tokenJson, " `r`n`t")
        If (StrLen(tokenJson) > 0) {
            return tokenJson
        }
    }
    
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
; VERIFICAÇÃO DE LICENÇA - EXECUTA AUTOMATICAMENTE
; ============================================================================
deviceId := License_GetDeviceId()

If (!deviceId Or StrLen(deviceId) < 16) {
    MsgBox, 16, Erro Crítico, Não foi possível gerar Device ID.`n`nTente executar como administrador ou verifique as permissões da pasta.`n`nPasta do script: %A_ScriptDir%
    ExitApp
}

isValid := License_Verify()

If (!isValid And g_LicenseVerify_Offline) {
    tokenJson := License_LoadToken()
    If (tokenJson And StrLen(tokenJson) > 0) {
        isValid := License_Verify_Offline(tokenJson)
        If (isValid) {
            g_LicenseVerify_Offline := true
        }
    }
}

If (!isValid) {
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message
    
    displayDeviceId := g_LicenseVerify_DeviceId
    If (!displayDeviceId) {
        displayDeviceId := deviceId
    }
    
    Clipboard := displayDeviceId
    
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
    
    MsgBox, 16, Licença Inválida, %msgText%
    
    ExitApp
}

; ============================================================================
; SEU CÓDIGO ORIGINAL AQUI
; ============================================================================
; A partir daqui, seu script pode executar normalmente
; A licença foi verificada e está válida

