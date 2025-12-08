#SingleInstance,Force
; IMPORTANTE: Este arquivo deve ser salvo como UTF-8 com BOM para exibir corretamente acentos
; No SciTE/Editor: File > Encoding > UTF-8 with BOM

; ============================================================================
; PROTEÇÃO DE LICENÇA - TUDO EM UM ARQUIVO (Standalone)
; Não precisa do arquivo license_check.ahk separado
; ============================================================================

; ============================================================================
; CONFIGURAÇÕES - ALTERE AQUI
; ============================================================================
; URL da API
; IMPORTANTE: Para clientes, use sempre a URL de producao!
; Para desenvolvimento local, use: http://127.0.0.1:5000
; Para producao (clientes), use: https://api.fartgreen.fun
g_LicenseAPI_BaseURL := "https://api.fartgreen.fun"
g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
g_LicenseAPI_Secret := "BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
g_LicenseAPI_Version := "1.0.0"

; ============================================================================
; Gera Device ID único baseado no hardware
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
; Calcula SHA256 - versão simplificada e mais confiável
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
; Método alternativo SHA256 (fallback) - usando script temporário
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
    
    ; Limpa
    FileDelete, %tempPsFile%
    
    return hash
}

; Variáveis globais para armazenar resultado da verificação
g_LicenseVerify_DeviceId := ""
g_LicenseVerify_Message := ""
g_LicenseVerify_Offline := false

; ============================================================================
; Verifica licença no servidor
; Retorna: true se válida, false se inválida
; Armazena informações em variáveis globais: g_LicenseVerify_DeviceId, g_LicenseVerify_Message
; ============================================================================
License_Verify() {
    global g_LicenseAPI_BaseURL, g_LicenseAPI_Key, g_LicenseAPI_Secret, g_LicenseAPI_Version
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message, g_LicenseVerify_Offline
    
    ; Limpa variáveis anteriores
    g_LicenseVerify_DeviceId := ""
    g_LicenseVerify_Message := ""
    g_LicenseVerify_Offline := false
    
    deviceId := License_GetDeviceId()
    If (!deviceId) {
        g_LicenseVerify_DeviceId := ""
        g_LicenseVerify_Message := "Erro ao gerar Device ID"
        return false
    }
    
    g_LicenseVerify_DeviceId := deviceId
    
    FormatTime, timestamp, , yyyyMMddHHmmss
    combined := deviceId . "|" . g_LicenseAPI_Version . "|" . timestamp . "|" . g_LicenseAPI_Secret
    
    ; Gera assinatura SHA256
    signature := License_SHA256(combined)
    
    ; Debug: salva informações para análise (ATIVADO)
    sigLen := StrLen(signature)
    FileAppend, Combined: %combined%`nSignature: %signature%`nTamanho: %sigLen%`n, %A_Temp%\license_sig_debug.txt
    
    ; Verifica se a assinatura foi gerada corretamente (SHA256 tem 64 caracteres hex)
    sigLen := StrLen(signature)
    If (!signature Or sigLen = 0 Or sigLen < 64) {
        ; Tenta gerar novamente com método alternativo
        FileAppend, Tentando metodo alternativo...`n, %A_Temp%\license_sig_debug.txt
        signature := License_SHA256_Alt(combined)
        sigLen := StrLen(signature)
        FileAppend, Signature Alt: %signature%`nTamanho Alt: %sigLen%`n, %A_Temp%\license_sig_debug.txt
        
        If (!signature Or sigLen = 0 Or sigLen < 64) {
            ; Salva debug do erro
            FileAppend, ERRO SHA256 - Combined: %combined%`nSignature gerada: %signature%`nTamanho: %sigLen%`n, %A_Temp%\license_sig_error.txt
            g_LicenseVerify_Message := "Erro ao gerar assinatura criptográfica (tamanho: " . sigLen . "). Verifique %TEMP%\license_sig_debug.txt"
            return false
        }
    }
    
    EnvGet, hostname, COMPUTERNAME
    EnvGet, username, USERNAME
    
    ; Codifica parâmetros da URL (especialmente hostname e username que podem ter caracteres especiais)
    ; AutoHotkey não tem função nativa, então vamos usar substituições simples
    StringReplace, hostname, hostname, %A_Space%, `%20, All
    StringReplace, username, username, %A_Space%, `%20, All
    
    url := g_LicenseAPI_BaseURL . "/verify"
    url .= "?id=" . deviceId
    url .= "&version=" . g_LicenseAPI_Version
    url .= "&ts=" . timestamp
    url .= "&sig=" . signature
    url .= "&api_key=" . g_LicenseAPI_Key
    url .= "&hostname=" . hostname
    url .= "&username=" . username
    
    ; Faz requisição HTTP usando método mais confiável
    tempFile := A_Temp . "\license_resp_" . A_TickCount . ".tmp"
    tempPsFile := A_Temp . "\license_ps_" . A_TickCount . ".ps1"
    
    ; Cria script PowerShell temporário para evitar problemas de escape
    ; Melhorado para capturar corpo da resposta mesmo em erros HTTP (400, 403, etc.)
    psScript := "$ErrorActionPreference = 'Continue'`n"
    psScript .= "try {`n"
    psScript .= "  $response = Invoke-WebRequest -Uri '" . url . "' -TimeoutSec 15 -UseBasicParsing`n"
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
    
    ; Salva script temporário
    FileDelete, %tempPsFile%
    FileAppend, %psScript%, %tempPsFile%
    
    ; Executa script PowerShell
    RunWait, powershell.exe -ExecutionPolicy Bypass -File "%tempPsFile%", , Hide
    
    ; Lê resposta
    response := ""
    IfExist, %tempFile%
    {
        FileRead, response, %tempFile%
        FileDelete, %tempFile%
        response := Trim(response, " `r`n`t")
    }
    
    ; Limpa script temporário
    FileDelete, %tempPsFile%
    
    ; Debug: salva resposta em arquivo temporário para análise (ATIVADO)
    respLen := StrLen(response)
    FileAppend, URL: %url%`nResponse Length: %respLen%`nResponse: %response%`n`n, %A_Temp%\license_debug.txt
    
    ; Se a resposta está vazia, tenta ler novamente (pode ser problema de timing)
    If (!response Or StrLen(response) = 0) {
        Sleep, 500
        IfExist, %tempFile%
        {
            FileRead, response, %tempFile%
            FileDelete, %tempFile%
            response := Trim(response, " `r`n`t")
            respLen := StrLen(response)
            FileAppend, Retry - Response Length: %respLen%`nResponse: %response%`n`n, %A_Temp%\license_debug.txt
        }
    }
    
    ; Verifica erro de conexao
    If (InStr(response, "ERROR:") = 1) {
        errorMsg := SubStr(response, 7)
        ; Limita tamanho da mensagem de erro
        If (StrLen(errorMsg) > 100) {
            errorMsg := SubStr(errorMsg, 1, 100) . "..."
        }
        g_LicenseVerify_Message := "Erro de conexão: " . errorMsg . "`nVerifique se o servidor está acessível: " . g_LicenseAPI_BaseURL
        g_LicenseVerify_Offline := true
        
        ; Tenta validar offline usando token salvo
        tokenJson := License_LoadToken()
        If (tokenJson And StrLen(tokenJson) > 0) {
            ; Debug: salva que tentou usar token offline
            FileAppend, Tentando validar offline - Token encontrado (tamanho: %StrLen(tokenJson)%)`n, %A_Temp%\license_offline_attempt.txt
            ; Valida offline
            offlineValid := License_Verify_Offline(tokenJson)
            If (offlineValid) {
                g_LicenseVerify_Message := "Licença válida (modo offline - servidor indisponível)"
                g_LicenseVerify_Offline := true
                FileAppend, Modo offline ativado com sucesso`n, %A_Temp%\license_offline_success.txt
                return true
            } Else {
                FileAppend, Validação offline falhou: %g_LicenseVerify_Message%`n, %A_Temp%\license_offline_failed.txt
            }
        } Else {
            FileAppend, Token offline não encontrado - Servidor offline e sem token salvo`n, %A_Temp%\license_offline_no_token.txt
        }
        
        return false
    }
    
    ; Verifica se a resposta está vazia
    If (!response Or StrLen(response) = 0) {
        g_LicenseVerify_Message := "Resposta vazia do servidor. Verifique se " . g_LicenseAPI_BaseURL . " está acessível."
        g_LicenseVerify_Offline := true
        
        ; Tenta validar offline usando token salvo
        tokenJson := License_LoadToken()
        If (tokenJson And StrLen(tokenJson) > 0) {
            ; Debug: salva que tentou usar token offline
            FileAppend, Tentando validar offline (resposta vazia) - Token encontrado (tamanho: %StrLen(tokenJson)%)`n, %A_Temp%\license_offline_attempt.txt
            ; Valida offline
            offlineValid := License_Verify_Offline(tokenJson)
            If (offlineValid) {
                g_LicenseVerify_Message := "Licença válida (modo offline - servidor indisponível)"
                g_LicenseVerify_Offline := true
                FileAppend, Modo offline ativado com sucesso (resposta vazia)`n, %A_Temp%\license_offline_success.txt
                return true
            } Else {
                FileAppend, Validação offline falhou (resposta vazia): %g_LicenseVerify_Message%`n, %A_Temp%\license_offline_failed.txt
            }
        } Else {
            FileAppend, Token offline não encontrado (resposta vazia) - Servidor offline e sem token salvo`n, %A_Temp%\license_offline_no_token.txt
        }
        
        return false
    }
    
    ; Debug: salva resposta completa para análise
    FileAppend, === RESPOSTA COMPLETA ===`n%response%`n`n, %A_Temp%\license_response_full.txt
    
    ; Verifica se licenca e valida (múltiplas formas de verificar)
    ; Procura por "allow":true em várias variações
    allowTrue := false
    If (InStr(response, """allow"":true") > 0) {
        allowTrue := true
    } Else If (InStr(response, """allow"": true") > 0) {
        allowTrue := true
    } Else If (InStr(response, """allow"":true") > 0) {
        allowTrue := true
    } Else If (InStr(response, "allow"":true") > 0) {
        allowTrue := true
    } Else If (InStr(response, "'allow':true") > 0) {
        allowTrue := true
    }
    
    If (allowTrue) {
        ; Salva token de licença para uso offline
        ; Extrai license_token da resposta JSON (método robusto para JSON aninhado)
        tokenSaved := false
        If (InStr(response, """license_token"":") > 0) {
            ; Encontra início do objeto license_token
            startPos := InStr(response, """license_token"":")
            If (startPos > 0) {
                ; Pula "license_token": e espaços
                pos := startPos + 17
                While (pos <= StrLen(response) And (SubStr(response, pos, 1) = " " Or SubStr(response, pos, 1) = "`t")) {
                    pos++
                }
                
                ; Se começa com {, extrai objeto completo contando chaves
                If (pos <= StrLen(response) And SubStr(response, pos, 1) = "{") {
                    bracketCount := 0
                    tokenJson := ""
                    startBracket := pos
                    
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
                        
                        ; Quando fecha todas as chaves, objeto completo
                        If (bracketCount = 0) {
                            Break
                        }
                    }
                    
                    ; Verifica se extraiu objeto válido
                    tokenJsonLen := StrLen(tokenJson)
                    If (tokenJsonLen > 20 And InStr(tokenJson, "{") = 1 And SubStr(tokenJson, -1) = "}") {
                        ; Salva token para uso offline
                        If (License_SaveToken(tokenJson)) {
                            tokenSaved := true
                            FileAppend, Token salvo para modo offline (tamanho: %tokenJsonLen% caracteres)`n, %A_Temp%\license_token_saved.txt
                        } Else {
                            FileAppend, ERRO ao salvar token (tamanho: %tokenJsonLen% caracteres)`n, %A_Temp%\license_token_save_error.txt
                        }
                    } Else {
                        FileAppend, Token extraído inválido (tamanho: %tokenJsonLen%, primeiro char: %SubStr(tokenJson, 1, 1)%, último char: %SubStr(tokenJson, -1)%)`n, %A_Temp%\license_token_extract_error.txt
                    }
                }
            }
        } Else {
            FileAppend, AVISO: license_token não encontrado na resposta do servidor`n, %A_Temp%\license_token_not_in_response.txt
        }
        
        g_LicenseVerify_Message := "Licença válida"
        return true
    }
    
    ; Verifica se foi negado explicitamente (múltiplas formas)
    allowFalse := false
    If (InStr(response, """allow"":false") > 0) {
        allowFalse := true
    } Else If (InStr(response, """allow"": false") > 0) {
        allowFalse := true
    } Else If (InStr(response, """allow"":false") > 0) {
        allowFalse := true
    } Else If (InStr(response, "allow"":false") > 0) {
        allowFalse := true
    } Else If (InStr(response, "'allow':false") > 0) {
        allowFalse := true
    }
    
    If (allowFalse) {
        ; Tenta extrair mensagem de erro da resposta
        msg := "Licença inválida ou expirada"
        If (InStr(response, """msg"":""") > 0) {
            RegExMatch(response, """msg"":""([^""]+)""", match)
            If (match1) {
                msg := match1
            }
        } Else If (InStr(response, """msg"": """) > 0) {
            RegExMatch(response, """msg"": ""([^""]+)""", match)
            If (match1) {
                msg := match1
            }
        }
        g_LicenseVerify_Message := msg
        return false
    }
    
    ; Se não encontrou allow, assume inválido
    msg := "Resposta invalida do servidor"
    If (InStr(response, """msg"":""") > 0) {
        RegExMatch(response, """msg"":""([^""]+)""", match)
        If (match1) {
            msg := match1
        }
    } Else If (InStr(response, """msg"": """) > 0) {
        RegExMatch(response, """msg"": ""([^""]+)""", match)
        If (match1) {
            msg := match1
        }
    }
    
    ; Salva resposta completa para debug
    FileAppend, Resposta não reconhecida: %response%`n, %A_Temp%\license_response_error.txt
    
    g_LicenseVerify_Message := msg . " (Resposta: " . SubStr(response, 1, 150) . ")"
    return false
}

; ============================================================================
; FUNÇÕES DE VALIDAÇÃO OFFLINE
; ============================================================================
; Período de graça em dias (quantos dias o sistema pode funcionar offline)
g_LicenseOffline_GracePeriodDays := 7

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

License_SaveToken(licenseTokenJson) {
    tokenFile := A_ScriptDir . "\license_token.json"
    tokenFileAlt := A_AppData . "\LicenseSystem\license_token.json"
    
    ; Tenta salvar na pasta do script primeiro
    FileDelete, %tokenFile%
    FileAppend, %licenseTokenJson%, %tokenFile%
    If (!ErrorLevel) {
        FileAppend, Token salvo com sucesso em: %tokenFile%`nTamanho: %StrLen(licenseTokenJson)% caracteres`n, %A_Temp%\license_token_save_log.txt
        return true
    }
    
    ; Se falhar, tenta salvar em %APPDATA%
    FileCreateDir, %A_AppData%\LicenseSystem
    If (!ErrorLevel) {
        FileDelete, %tokenFileAlt%
        FileAppend, %licenseTokenJson%, %tokenFileAlt%
        If (!ErrorLevel) {
            FileAppend, Token salvo com sucesso em: %tokenFileAlt%`nTamanho: %StrLen(licenseTokenJson)% caracteres`n, %A_Temp%\license_token_save_log.txt
            return true
        }
    }
    
    FileAppend, ERRO ao salvar token - Pasta script: %ErrorLevel%, Pasta AppData: %ErrorLevel%`n, %A_Temp%\license_token_save_error.txt
    return false
}

License_LoadToken() {
    tokenFile := A_ScriptDir . "\license_token.json"
    tokenFileAlt := A_AppData . "\LicenseSystem\license_token.json"
    
    ; Tenta ler da pasta do script
    IfExist, %tokenFile%
    {
        FileRead, tokenJson, %tokenFile%
        tokenJson := Trim(tokenJson, " `r`n`t")
        If (StrLen(tokenJson) > 0) {
            FileAppend, Token carregado de: %tokenFile%`nTamanho: %StrLen(tokenJson)% caracteres`n, %A_Temp%\license_token_load_log.txt
            return tokenJson
        }
    }
    
    ; Tenta ler de %APPDATA%
    IfExist, %tokenFileAlt%
    {
        FileRead, tokenJson, %tokenFileAlt%
        tokenJson := Trim(tokenJson, " `r`n`t")
        If (StrLen(tokenJson) > 0) {
            FileAppend, Token carregado de: %tokenFileAlt%`nTamanho: %StrLen(tokenJson)% caracteres`n, %A_Temp%\license_token_load_log.txt
            return tokenJson
        }
    }
    
    FileAppend, Token não encontrado - Verificou: %tokenFile% e %tokenFileAlt%`n, %A_Temp%\license_token_not_found.txt
    return ""
}

; ============================================================================
; VERIFICAÇÃO NO INÍCIO - BLOQUEIA SE NÃO TIVER LICENÇA
; ============================================================================
; Configuração: Exibir mensagem de sucesso? (altere para true se quiser ver)
SHOW_SUCCESS_MSG := false

deviceId := License_GetDeviceId()

If (!deviceId Or StrLen(deviceId) < 16) {
    ; Tenta gerar um ID simples como fallback
    DriveGet, volSerial, Serial, C:
    EnvGet, computerName, COMPUTERNAME
    FormatTime, timestamp, , yyyyMMddHHmmss
    deviceId := volSerial . computerName . timestamp
    deviceId := SubStr(deviceId, 1, 32)
    
    If (!deviceId Or StrLen(deviceId) < 16) {
        MsgBox, 16, Erro Crítico, Não foi possível gerar Device ID.`n`nTente executar como administrador ou verifique as permissões da pasta.`n`nPasta do script: %A_ScriptDir%
        ExitApp
    }
}

; Verifica licença (tenta online primeiro, depois offline se necessário)
isValid := License_Verify()

; Se falhou e está offline, tenta validar com token salvo (fallback adicional)
If (!isValid And g_LicenseVerify_Offline) {
    ; Já tentou offline dentro de License_Verify, mas tenta novamente aqui como fallback
    tokenJson := License_LoadToken()
    If (tokenJson And StrLen(tokenJson) > 0) {
        FileAppend, Fallback: Tentando validar offline novamente (token encontrado)`n, %A_Temp%\license_offline_fallback.txt
        isValid := License_Verify_Offline(tokenJson)
        If (isValid) {
            ; Modo offline ativado - permite uso mas avisa
            FileAppend, Modo offline ativado (fallback) - Token validado localmente`n, %A_Temp%\license_offline_mode.txt
            g_LicenseVerify_Offline := true
        } Else {
            FileAppend, Fallback offline falhou: %g_LicenseVerify_Message%`n, %A_Temp%\license_offline_fallback_failed.txt
        }
    } Else {
        FileAppend, Fallback: Token não encontrado para validação offline`n, %A_Temp%\license_offline_fallback_no_token.txt
    }
}

; Debug: salva resultado da verificação
FileAppend, Verificacao de licenca - Device ID: %deviceId%`nResultado: %isValid%`nModo Offline: %g_LicenseVerify_Offline%`nMensagem: %g_LicenseVerify_Message%`n`n, %A_Temp%\license_verification_result.txt

If (isValid) {
    ; Licença válida - opcionalmente exibe mensagem de sucesso
    If (SHOW_SUCCESS_MSG) {
        MsgBox, 64, Licença Válida, Licença verificada com sucesso!`n`nDevice ID: %deviceId%`n`nO programa continuará normalmente.
    }
} Else {
    ; Obtém informações da verificação
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message
    
    ; Garante que temos o Device ID
    displayDeviceId := g_LicenseVerify_DeviceId
    If (!displayDeviceId) {
        ; Tenta ler do arquivo
        deviceIdFile := A_ScriptDir . "\device.id"
        IfExist, %deviceIdFile%
        {
            FileRead, deviceIdFromFile, %deviceIdFile%
            deviceIdFromFile := Trim(deviceIdFromFile, " `r`n`t")
            If (StrLen(deviceIdFromFile) > 0) {
                displayDeviceId := deviceIdFromFile
            }
        }
        ; Tenta ler de %APPDATA%
        If (!displayDeviceId) {
            deviceIdFileAlt := A_AppData . "\LicenseSystem\device.id"
            IfExist, %deviceIdFileAlt%
            {
                FileRead, deviceIdFromFile, %deviceIdFileAlt%
                deviceIdFromFile := Trim(deviceIdFromFile, " `r`n`t")
                If (StrLen(deviceIdFromFile) > 0) {
                    displayDeviceId := deviceIdFromFile
                }
            }
        }
        If (!displayDeviceId) {
            displayDeviceId := deviceId
        }
    }
    
    ; Copia Device ID para área de transferência ANTES de mostrar mensagem
    Clipboard := displayDeviceId
    
    ; Monta mensagem com codificação UTF-8 correta
    ; Usa método que garante exibição correta de acentos
    msgTitle := "Licença Inválida"
    
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
    
    ; Exibe mensagem (IMPORTANTE: arquivo .ahk deve estar salvo como UTF-8 com BOM)
    MsgBox, 16, %msgTitle%, %msgText%
    
    ExitApp
}

; ============================================================================
; SEU CÓDIGO ORIGINAL (sem modificações)
; ============================================================================

; Verifica se performace.ahk existe antes de incluir
IfExist, %A_ScriptDir%\performace.ahk
{
    #Include performace.ahk
}
Else
{
    ; Se não existir, continua sem ele (ou adicione seu código aqui)
    ; MsgBox, 48, Aviso, Arquivo performace.ahk não encontrado. Continuando sem ele...
}

#NoTrayIcon

	Loop, 7{

	WinGetTitle, Title, A

	;MsgBox, The active window is "%Title%".

	myTitle := Title

	myTube := SubStr(Title, 1,13)

	youtubeTv := "YouTube na TV"

	if(myTube = youtubeTv){

		Process, Exist, javaw.exe

		NewPID = %errorlevel%

			if (%errorlevel% <> 0){

		CoordMode, Mouse, Screen

		Loop, 2{

			x := A_ScreenWidth // 2

			y := A_ScreenHeight // 2

			MouseMove, %x%, %y%

			Click

			Sleep, 300

		}

		Sleep, 1000

	; ===== CONFIGURAÇÕES =====

		Send, {Left}

		Sleep, 300

		Loop, 2{

			Send, {Down}

			Sleep, 300

		}

		Send, {Right}

		Sleep, 300

		Loop, 6{

			Send, {Down}

			Sleep, 300

		}

		Sleep, 500

		Run, %A_WorkingDir%\Comandos.exe

			Sleep, 500

		Run, %A_WorkingDir%\blocked.exe

			Sleep, 500

		Run, %A_WorkingDir%\clicks.exe

		Sleep, 500

		ExitApp

			}else{

			Run, %A_WorkingDir%\notification.exe

		}

		Process, Exist, timetemporary.exe

		NewPID = %errorlevel%

			if (%errorlevel% <> 0){

				Send, {Volume_Mute}

			ExitApp

			}

	Run, %A_WorkingDir%\timetemporary.exe

	Process, close, images.exe

	Progress, off

	}else{

	Run, %A_WorkingDir%\images.exe

	Sleep, 3000

	process, close, psrockola4.exe

	;Run, chrome.exe --chrome-frame -kiosk /incognito https://www.youtube.com/tv

	Run, brave.exe --kiosk --start-fullscreen --kiosk --incognito --disable-infobars --disable-session-crashed-bubble --disable-restore-session-state --no-first-run --no-default-browser-check --disable-plugins-discovery --disable-popup-blocking --disable-blink-features=AutomationControlled --disable-features=TranslateUI --disable-ipc-flooding-protection --incognito --profile-directory="Default" "https://www.youtube.com/tv#/browse?c=FElibrary"

	;~Run, msedge.exe --kiosk "https://www.youtube.com/tv#/browse?c=FEmy_youtube" --inprivate --edge-kiosk-type=full

	;~ Run, msedge.exe --kiosk "https://www.youtube.com/tv#/browse?c=FEmy_youtube" --inprivate --edge-kiosk-type=fullscreen

	wdth := (A_ScreenWidth/2)-(Width/2), hght := 455

	Progress,  b fs30 fm12 zh0 CTRED CWFFFFFF X%wdth% Y%hght%  w1330, AGUARDE UM MOMENTO..., ,Youtube

	WinSet, TransColor, 000000 200, Youtube,

	Sleep, 850

	}

	Sleep, 5000

	}

	Send, {F5}

	Reload

	return

Shift::

ExitApp

