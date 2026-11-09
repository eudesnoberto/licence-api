#SingleInstance,Force

; ============================================================================
; SOLUÇÃO COMPLETA COM REDUNDÂNCIA DE SERVIDORES
; ============================================================================
; Este arquivo suporta múltiplos servidores para alta disponibilidade
; Se um servidor cair, tenta automaticamente o próximo
; ============================================================================

; ============================================================================
; CONFIGURAÇÕES - SERVIDORES COM REDUNDÂNCIA E ATUALIZAÇÃO DINÂMICA
; ============================================================================
; Sistema profissional de gerenciamento de servidores para 30k+ clientes
; Atualiza automaticamente sem necessidade de recompilar o executável
; ============================================================================

; ============================================================================
; CONFIGURAÇÃO DO SISTEMA DE ATUALIZAÇÃO DINÂMICA
; ============================================================================
; Endpoint centralizado para obter lista de servidores atualizada
; Pode ser um dos seus próprios servidores ou um CDN (ex: GitHub Raw, Cloudflare)
; ============================================================================
g_ConfigEndpoint := "https://api.epr.app.br/servers"  ; Endpoint para lista de servidores
g_ConfigCacheFile := A_AppData . "\LicenseSystem\servers_cache.json"
g_ConfigCacheMaxAge := 3600  ; Cache válido por 1 hora (3600 segundos)
g_ConfigUpdateInterval := 86400  ; Verifica atualizações a cada 24 horas

; ============================================================================
; SERVIDORES FALLBACK (HARDCODED)
; ============================================================================
; Usados apenas se não conseguir baixar lista atualizada
; Estes servidores NUNCA devem ser removidos - são o último recurso
; ============================================================================
g_LicenseAPI_Servers_Fallback := []
g_LicenseAPI_Servers_Fallback[1] := "https://api.epr.app.br"
g_LicenseAPI_Servers_Fallback[2] := "https://licence-api-6evg.onrender.com"
g_LicenseAPI_Servers_Fallback[3] := "https://api-epr.rj.r.appspot.com"

; ============================================================================
; ARRAY DINÂMICO DE SERVIDORES (SERÁ PREENCHIDO AUTOMATICAMENTE)
; ============================================================================
g_LicenseAPI_Servers := []

; Configurações de API
g_LicenseAPI_Key := "CFEC44D0118C85FBA54A4B96C89140C6"
g_LicenseAPI_Secret := "" ; removido: assinatura de requisição compartilhada desativada na migração
g_LicenseAPI_Version := "1.0.0"

global g_LicenseVerify_DeviceId := ""
global g_LicenseVerify_Message := ""
global g_LicenseVerify_Offline := false
; Política offline: sem prazo de carência; tokens perpétuos continuam válidos sem limite de tempo.

; ============================================================================
; FUNÇÃO: License_LoadServersFromConfig() - Carrega servidores do cache ou baixa atualização
; ============================================================================
License_LoadServersFromConfig() {
    global g_ConfigCacheFile, g_ConfigCacheMaxAge, g_ConfigEndpoint
    global g_LicenseAPI_Servers, g_LicenseAPI_Servers_Fallback

    ; Tenta carregar do cache primeiro
    cacheValid := false
    IfExist, %g_ConfigCacheFile%
    {
        FileRead, cacheContent, %g_ConfigCacheFile%
        If (cacheContent And StrLen(cacheContent) > 0) {
            ; Verifica se cache ainda é válido
            RegExMatch(cacheContent, """timestamp"":(\d+)", match)
            If (match1) {
                cacheTime := match1
                currentTime := A_NowUTC
                EnvSub, currentTime, %cacheTime%, Seconds
                timeDiff := currentTime
                
                ; Timestamp da API e relógio do cliente são comparados em UTC.
                If (timeDiff >= 0 And timeDiff < g_ConfigCacheMaxAge) {
                    servers := License_ParseServerConfig(cacheContent)
                    If (servers.Length() > 0) {
                        g_LicenseAPI_Servers := servers
                        cacheValid := true
                        FileAppend, [%A_Now%] Servidores carregados do cache (válido)`n, %A_Temp%\license_config_log.txt
                    }
                }
            }
        }
    }

    ; Se cache inválido ou não existe, tenta baixar atualização
    If (!cacheValid) {
        FileAppend, [%A_Now%] Cache inválido ou não existe, tentando atualizar...`n, %A_Temp%\license_config_log.txt
        
        ; Tenta baixar de cada servidor fallback até conseguir
        maxFallback := g_LicenseAPI_Servers_Fallback.Length()
        downloadSuccess := false
        
        Loop, %maxFallback%
        {
            configServer := g_LicenseAPI_Servers_Fallback[A_Index]
            configUrl := configServer . "/servers"
            
            ; Se o endpoint configurado já é um servidor completo, usa ele
            If (InStr(g_ConfigEndpoint, "http") = 1) {
                configUrl := g_ConfigEndpoint
            }
            
            servers := License_DownloadServerConfig(configUrl)
            If (servers.Length() > 0) {
                g_LicenseAPI_Servers := servers
                License_SaveServerConfig(servers)
                downloadSuccess := true
                FileAppend, [%A_Now%] Lista de servidores atualizada com sucesso de: %configUrl%`n, %A_Temp%\license_config_log.txt
                Break
            }
        }
        
        ; Se falhou ao baixar, usa fallback hardcoded
        If (!downloadSuccess) {
            FileAppend, [%A_Now%] Falha ao baixar lista, usando servidores fallback hardcoded`n, %A_Temp%\license_config_log.txt
            g_LicenseAPI_Servers := g_LicenseAPI_Servers_Fallback.Clone()
        }
    }
    
    ; Garante que sempre há pelo menos os servidores fallback
    If (g_LicenseAPI_Servers.Length() = 0) {
        g_LicenseAPI_Servers := g_LicenseAPI_Servers_Fallback.Clone()
    }
}

; ============================================================================
; FUNÇÃO: License_DownloadServerConfig() - Baixa lista de servidores do endpoint
; ============================================================================
License_DownloadServerConfig(configUrl) {
    tempFile := A_Temp . "\servers_config_" . A_TickCount . ".tmp"
    tempPsFile := A_Temp . "\servers_ps_" . A_TickCount . ".ps1"
    
    servers := []
    
    ; Script PowerShell para baixar configuração
    psScript := "$ErrorActionPreference = 'Stop'`n"
    psScript .= "try {`n"
    psScript .= "  $response = Invoke-WebRequest -Uri '" . configUrl . "' -TimeoutSec 10 -UseBasicParsing`n"
    psScript .= "  $response.Content | Out-File -FilePath '" . tempFile . "' -Encoding UTF8 -NoNewline`n"
    psScript .= "  exit 0`n"
    psScript .= "} catch {`n"
    psScript .= "  ('ERROR: ' + $_.Exception.Message) | Out-File -FilePath '" . tempFile . "' -Encoding UTF8 -NoNewline`n"
    psScript .= "  exit 1`n"
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
    
    ; Se não é erro, tenta parsear
    If (response And StrLen(response) > 0 And InStr(response, "ERROR:") != 1) {
        servers := License_ParseServerConfig(response)
    }
    
    return servers
}

; ============================================================================
; FUNÇÃO: License_ParseServerConfig() - Parseia JSON com lista de servidores
; ============================================================================
License_ParseServerConfig(jsonContent) {
    servers := []
    
    ; Extrai array de servidores do JSON
    ; Formato esperado: {"version": 1, "timestamp": 20250101120000, "servers": ["url1", "url2", ...]}
    
    ; Procura pelo array de servidores
    If (InStr(jsonContent, """servers""") > 0) {
        ; Encontra início do array
        startPos := InStr(jsonContent, """servers"":")
        If (startPos > 0) {
            ; Procura por [
            pos := startPos + 10
            While (pos <= StrLen(jsonContent) And SubStr(jsonContent, pos, 1) != "[") {
                pos++
            }
            
            If (pos <= StrLen(jsonContent)) {
                ; Agora extrai cada URL do array
                pos++  ; Pula o [
                bracketCount := 1
                currentUrl := ""
                inString := false
                escapeNext := false
                
                Loop, % StrLen(jsonContent)
                {
                    If (pos > StrLen(jsonContent)) {
                        Break
                    }
                    
                    char := SubStr(jsonContent, pos, 1)
                    
                    If (escapeNext) {
                        currentUrl .= char
                        escapeNext := false
                        pos++
                        Continue
                    }
                    
                    If (char = "\") {
                        escapeNext := true
                        pos++
                        Continue
                    }
                    
                    If (char = """") {
                        If (inString) {
                            ; Fim da string
                            If (StrLen(currentUrl) > 0) {
                                ; Valida URL básica
                                If (InStr(currentUrl, "http://") = 1 Or InStr(currentUrl, "https://") = 1) {
                                    servers.Push(currentUrl)
                                }
                            }
                            currentUrl := ""
                        }
                        inString := !inString
                        pos++
                        Continue
                    }
                    
                    If (inString) {
                        currentUrl .= char
                    } Else If (char = "]") {
                        bracketCount--
                        If (bracketCount = 0) {
                            Break
                        }
                    } Else If (char = "[") {
                        bracketCount++
                    }
                    
                    pos++
                }
            }
        }
    }
    
    return servers
}

; ============================================================================
; FUNÇÃO: License_SaveServerConfig() - Salva lista de servidores no cache
; ============================================================================
License_SaveServerConfig(servers) {
    global g_ConfigCacheFile
    
    If (servers.Length() = 0) {
        return false
    }
    
    ; Cria diretório se não existir
    IfNotExist, %A_AppData%\LicenseSystem
    {
        FileCreateDir, %A_AppData%\LicenseSystem
    }
    
    ; Monta JSON com timestamp
    timestamp := A_NowUTC
    
    ; Constrói JSON de forma segura usando Chr(34) para aspas duplas
    quote := Chr(34)
    jsonContent := "{" . quote . "version" . quote . ":1,"
    jsonContent .= quote . "timestamp" . quote . ":"
    jsonContent .= timestamp . ","
    jsonContent .= quote . "servers" . quote . ":["
    
    Loop, % servers.Length()
    {
        If (A_Index > 1) {
            jsonContent .= ","
        }
        jsonContent .= quote . servers[A_Index] . quote
    }
    
    jsonContent .= "]}"
    
    ; Salva arquivo
    FileDelete, %g_ConfigCacheFile%
    FileAppend, %jsonContent%, %g_ConfigCacheFile%
    
    return !ErrorLevel
}

; ============================================================================
; FUNÇÃO: License_GetCurrentServer() - Obtém servidor atual (com suporte a redundância)
; ============================================================================
License_GetCurrentServer(serverIndex := 1) {
    global g_LicenseAPI_Servers, g_LicenseAPI_Servers_Fallback

    ; Se usar array de servidores dinâmico
    If (IsObject(g_LicenseAPI_Servers) And g_LicenseAPI_Servers.Length() > 0) {
        If (serverIndex <= g_LicenseAPI_Servers.Length()) {
            return g_LicenseAPI_Servers[serverIndex]
        }
    }

    ; Fallback para servidores hardcoded
    If (IsObject(g_LicenseAPI_Servers_Fallback) And g_LicenseAPI_Servers_Fallback.Length() > 0) {
        If (serverIndex <= g_LicenseAPI_Servers_Fallback.Length()) {
            return g_LicenseAPI_Servers_Fallback[serverIndex]
        }
    }

    ; Último fallback
    return "https://api.epr.app.br"
}

; ============================================================================
; FUNÇÃO 0: License_CheckInternet() - Verifica conectividade com internet
; ============================================================================
License_CheckInternet() {
    ; Tenta ler IP do config.ini, se não existir usa padrão (Google DNS)
    configFile := A_ScriptDir . "\config.ini"
    testIP := "8.8.8.8"  ; Google DNS como padrão

    IfExist, %configFile%
    {
        IniRead, conection, %configFile%, IPS, IP
        If (conection And StrLen(conection) > 0) {
            testIP := conection
        }
    }

    ; Faz ping no IP configurado
    RunWait, ping.exe %testIP% -n 1 -w 3000,, Hide UseErrorlevel

    ; Se ErrorLevel > 0, significa que o ping falhou (sem internet)
    If (ErrorLevel) {
        return false
    }

    ; Ping bem-sucedido = tem internet
    return true
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
    global g_LicenseAPI_Key, g_LicenseAPI_Version
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

    timestamp := A_NowUTC
    ; Assinatura compartilhada desativada: a validação online usa TLS + API key de compatibilidade.
    signature := ""

    ; O servidor está configurado para aceitar a verificação online por TLS e chave de API.

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
        url .= "&hostname=" . hostname
        url .= "&username=" . username

        ; Faz requisição
        tempFile := A_Temp . "\license_resp_" . A_TickCount . "_" . A_Index . ".tmp"
        tempPsFile := A_Temp . "\license_ps_" . A_TickCount . "_" . A_Index . ".ps1"

        psScript := "$ErrorActionPreference = 'Continue'`n"
        psScript .= "$headers = @{ 'X-API-Key' = '" . g_LicenseAPI_Key . "' }`n"
        psScript .= "try {`n"
        psScript .= "  $response = Invoke-WebRequest -Uri '" . url . "' -Headers $headers -TimeoutSec 30 -UseBasicParsing`n"
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

        ; ========================================================================
        ; DETECTA TIPO DE RESPOSTA
        ; ========================================================================
        ; 1. Erro de conexão (deve tentar próximo servidor)
        ; 2. Resposta JSON válida com allow:true (sucesso)
        ; 3. Resposta JSON válida com allow:false (erro de licença - não tenta próximo)
        ; 4. Resposta inválida/HTML (erro de conexão - tenta próximo)
        ; ========================================================================

        isConnectionError := false
        isJsonResponse := false

        ; Verifica se é erro de conexão
        If (InStr(response, "ERROR:") = 1) {
            isConnectionError := true
            FileAppend, [%A_Index%/%maxServers%] Servidor %currentServer% - Erro de conexão: %response%`n, %A_Temp%\license_server_failover.txt
        } Else If (!response Or StrLen(response) = 0) {
            isConnectionError := true
            FileAppend, [%A_Index%/%maxServers%] Servidor %currentServer% - Resposta vazia`n, %A_Temp%\license_server_failover.txt
        } Else If (InStr(response, "<!doctype") = 1 Or InStr(response, "<html") = 1 Or InStr(response, "Cloudflare") > 0) {
            ; Resposta HTML (servidor offline ou erro)
            isConnectionError := true
            FileAppend, [%A_Index%/%maxServers%] Servidor %currentServer% - Resposta HTML (servidor offline?)`n, %A_Temp%\license_server_failover.txt
        } Else If (InStr(response, "{") > 0 And InStr(response, "}") > 0 And (InStr(response, """allow"":") > 0)) {
            ; Parece ser JSON válido com campo "allow" (resposta da API)
            isJsonResponse := true
        } Else {
            ; Resposta inválida (não é JSON nem erro conhecido)
            isConnectionError := true
            FileAppend, [%A_Index%/%maxServers%] Servidor %currentServer% - Resposta inválida: %response%`n, %A_Temp%\license_server_failover.txt
        }

        ; Se é erro de conexão, tenta próximo servidor
        If (isConnectionError) {
            If (A_Index < maxServers) {
                FileAppend, Tentando próximo servidor...`n, %A_Temp%\license_server_failover.txt
                Continue
            } Else {
                ; Último servidor também falhou - vai para modo offline
                Break
            }
        }

        ; Se obteve resposta JSON válida, processa
        If (isJsonResponse And response And StrLen(response) > 0) {
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
                ; Resposta JSON válida mas licença negada - NÃO tenta próximo servidor
                ; (pois é erro de licença, não de conexão)
                msg := "Licença inválida ou expirada"
                If (InStr(response, """msg"":""") > 0) {
                    RegExMatch(response, """msg"":""([^""]+)""", match)
                    If (match1) {
                        msg := match1
                    }
                }
                g_LicenseVerify_Message := msg
                FileAppend, [%A_Index%/%maxServers%] Servidor %currentServer% - Licença negada: %msg%`n, %A_Temp%\license_server_failover.txt
                return false
            }
        } Else {
            ; Se chegou aqui e não é JSON válido nem erro de conexão, algo estranho
            ; Tenta próximo servidor se houver
            If (A_Index < maxServers) {
                FileAppend, [%A_Index%/%maxServers%] Servidor %currentServer% - Resposta inválida, tentando próximo...`n, %A_Temp%\license_server_failover.txt
                Continue
            }
        }
    }

    ; Se todos os servidores falharam (erro de conexão), tenta modo offline
    FileAppend, Todos os servidores falharam - Tentando modo offline...`n, %A_Temp%\license_server_failover.txt
    g_LicenseVerify_Message := "Todos os servidores indisponíveis"
    g_LicenseVerify_Offline := true

    tokenJson := License_LoadToken()
    If (tokenJson And StrLen(tokenJson) > 0) {
        offlineValid := License_Verify_Offline(tokenJson)
        If (offlineValid) {
            FileAppend, Modo offline ativado com sucesso!`n, %A_Temp%\license_offline_success.txt
            g_LicenseVerify_Message := "Licença válida (modo offline - todos os servidores indisponíveis)"
            g_LicenseVerify_Offline := true
            return true
        } Else {
            FileAppend, Modo offline falhou - token inválido ou expirado`n, %A_Temp%\license_offline_failed.txt
        }
    } Else {
        FileAppend, Modo offline não disponível - nenhum token salvo`n, %A_Temp%\license_offline_no_token.txt
    }

    g_LicenseVerify_Message := "Todos os servidores indisponíveis e modo offline não disponível"
    return false
}

; ============================================================================
; FUNÇÃO 4: License_Verify_Offline()
; ============================================================================
License_Verify_Offline(licenseTokenJson) {
    global g_LicenseVerify_DeviceId, g_LicenseVerify_Message

    g_LicenseVerify_DeviceId := ""
    g_LicenseVerify_Message := ""

    ; O token novo deve conter payload_b64 e assinatura RSA-SHA256.
    payloadB64 := ""
    signatureB64 := ""
    If (RegExMatch(licenseTokenJson, """payload_b64""\s*:\s*""([A-Za-z0-9+/=]+)""", match))
        payloadB64 := match1
    If (RegExMatch(licenseTokenJson, """signature""\s*:\s*""([A-Za-z0-9+/=]+)""", match))
        signatureB64 := match1

    If (!payloadB64 Or !signatureB64) {
        g_LicenseVerify_Message := "Token offline antigo ou inválido. Conecte-se à internet para renovar."
        return false
    }

    ; Verifica a assinatura com a chave PÚBLICA. Nenhum segredo privado fica no cliente.
    publicKeyXml := "<RSAKeyValue><Modulus>yQZto8JpopRuzz0l+5sXIbixta2IrpBkJQdEGPpS2PyEZGR1PwcqbGW565c50fkxNgiPL1UMYaD+rc98UVuVAMyV0oyKB7TA+XQP4NjG9zWGv5d8hgmqYJnr/ppfTGPiQp7SIipJcxK4KlMAD6kjDiFkbvUqn3Wcqvg+cv4rMzjBFTU8b9Hw8i2+CjfeFmdOKV8By7IW2GAb+Kg64I7Wi0xW6BuYNsBWkBJ1Y5Y0SlmlEvpMZK+XgqDR0xZRkqTfD2UOXPESlqufcsl/KM1hSCN20dOuDA1SpW6cxsazF3Uj9sNKVWECrJH93lE3WeGUuLLptZBkiIYWy3kNm6H2hC+7tihWIt/K3ebcVla0D10+EolnkLcrsBhwqVgmIV4RdBY/41ZF2fZZtmJp0w8jiohSsrldrnIm2BU2NehtlFIAGOimhRBR0KjIZZRuE7SDmwoONhkOd6OVLuDtePdAqv//F4gtyD1ekCRxPStLU0R50NMzG/xagnPDZmDdo/Kv</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"

    tempPsFile := A_Temp . "\license_verify_" . A_TickCount . ".ps1"
    payloadFile := A_Temp . "\license_payload_" . A_TickCount . ".json"
    psScript := "$ErrorActionPreference = 'Stop'`n"
    psScript .= "$payload = [Convert]::FromBase64String('" . payloadB64 . "')`n"
    psScript .= "$signature = [Convert]::FromBase64String('" . signatureB64 . "')`n"
    psScript .= "$rsa = New-Object System.Security.Cryptography.RSACryptoServiceProvider`n"
    psScript .= "$rsa.FromXmlString('" . publicKeyXml . "')`n"
    psScript .= "$sha = [System.Security.Cryptography.SHA256]::Create()`n"
    psScript .= "if (-not $rsa.VerifyData($payload, $sha, $signature)) { exit 2 }`n"
    psScript .= "[System.IO.File]::WriteAllBytes('" . payloadFile . "', $payload)`n"
    psScript .= "exit 0`n"

    FileDelete, %tempPsFile%
    FileDelete, %payloadFile%
    FileAppend, %psScript%, %tempPsFile%
    RunWait, %ComSpec% /c powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%tempPsFile%" >nul 2>&1, , Hide
    verifyExitCode := ErrorLevel
    FileDelete, %tempPsFile%

    If (verifyExitCode != 0) {
        FileDelete, %payloadFile%
        g_LicenseVerify_Message := "Assinatura RSA do token offline inválida"
        return false
    }

    FileRead, payloadRaw, %payloadFile%
    FileDelete, %payloadFile%
    If (!payloadRaw) {
        g_LicenseVerify_Message := "Payload offline vazio"
        return false
    }

    deviceId := ""
    expiresAt := ""
    status := ""
    If (RegExMatch(payloadRaw, """device_id""\s*:\s*""([^""]+)""", match))
        deviceId := match1
    If (RegExMatch(payloadRaw, """expires_at""\s*:\s*""([^""]+)""", match))
        expiresAt := match1
    If (RegExMatch(payloadRaw, """status""\s*:\s*""([^""]+)""", match))
        status := match1

    If (!deviceId Or status != "active") {
        g_LicenseVerify_Message := "Licença offline inativa ou token inválido"
        return false
    }

    currentDeviceId := License_GetDeviceId()
    If (currentDeviceId != deviceId) {
        g_LicenseVerify_Message := "Token não corresponde a este dispositivo"
        return false
    }

    ; Sem limite de carência offline: licenças perpétuas (expires_at null) não expiram.
    ; Licenças com data final continuam respeitando a expiração registrada no servidor.
    If (expiresAt != "") {
        expiresDate := expiresAt
        StringReplace, expiresDate, expiresDate, -, , All
        expiresDate := SubStr(expiresDate, 1, 8)
        currentDate := SubStr(A_NowUTC, 1, 8)
        if (expiresDate < currentDate) {
            g_LicenseVerify_Message := "Licença offline expirada"
            return false
        }
    }

    g_LicenseVerify_DeviceId := deviceId
    g_LicenseVerify_Message := "Licença válida (assinatura RSA offline)"
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
; INICIALIZAÇÃO DO SISTEMA DE SERVIDORES DINÂMICOS
; ============================================================================
; Carrega lista de servidores do cache ou baixa atualização
; Executa ANTES de qualquer verificação de licença
; ============================================================================

; Garante que o diretório existe desde o início
configDirPath := A_AppData . "\LicenseSystem"
IfNotExist, %configDirPath%
{
    FileCreateDir, %configDirPath%
    ; Aguarda um pouco para garantir que foi criado
    Sleep, 100
    ; Verifica novamente se existe
    IfNotExist, %configDirPath%
    {
        ; Tenta método alternativo
        RunWait, %ComSpec% /c mkdir "%configDirPath%" 2>nul, , Hide
        FileAppend, [%A_Now%] Tentativa de criar diretório: %configDirPath%`n, %A_Temp%\license_config_log.txt
    } Else {
        FileAppend, [%A_Now%] Diretório criado com sucesso: %configDirPath%`n, %A_Temp%\license_config_log.txt
    }
}

License_LoadServersFromConfig()

; ============================================================================
; ATUALIZAÇÃO PERIÓDICA EM BACKGROUND (OPCIONAL)
; ============================================================================
; Verifica atualizações de servidores periodicamente sem bloquear execução
; ============================================================================
SetTimer, License_UpdateServersBackground, % (g_ConfigUpdateInterval * 1000)

; ============================================================================
; VERIFICAÇÃO DE INTERNET E LICENÇA - EXECUTA AUTOMATICAMENTE
; ============================================================================

; ============================================================================
; PASSO 1: Verifica se há internet
; ============================================================================
hasInternet := License_CheckInternet()

If (!hasInternet) {
    ; Sem internet: somente permite continuar com token RSA válido já salvo.
    deviceId := License_GetDeviceId()
    tokenJson := License_LoadToken()
    If (tokenJson And License_Verify_Offline(tokenJson)) {
        g_LicenseVerify_Offline := true
        g_LicenseVerify_Message := "Licença válida offline (sem prazo de carência)"
        Goto, SkipLicenseCheck
    }

    SoundSet, 10
    Progress, CTRED b fs15 fm12 zh0 w1360, SEM INTERNET E SEM TOKEN OFFLINE VALIDO`nCONECTE-SE PARA VALIDAR A LICENCA.`n`n.,,Countdowner
    WinSet, TransColor, 000000 240, Countdowner
    Sleep 7000
    Progress, Off
    SoundSet, 10
    MsgBox, 16, Licença não validada, Sem conexão e sem um token offline RSA válido. Conecte-se à internet para validar a licença.
    ExitApp
}

; ============================================================================
; PASSO 2: Tem internet - Verifica Device ID
; ============================================================================
deviceId := License_GetDeviceId()

If (!deviceId Or StrLen(deviceId) < 16) {
    MsgBox, 16, Erro Crítico, Não foi possível gerar Device ID.`n`nTente executar como administrador ou verifique as permissões da pasta.`n`nPasta do script: %A_ScriptDir%
    ExitApp
}

; ============================================================================
; PASSO 3: Tem internet - Verifica licença
; ============================================================================
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

SkipLicenseCheck:
; ============================================================================
; SEU CÓDIGO ORIGINAL AQUI
; ============================================================================
; A partir daqui, seu script pode executar normalmente
; Se passou pela verificação de licença, está válida
; Se pulou (sem internet), o programa continua mas sem verificação

; ============================================================================
; ROTINA DE ATUALIZAÇÃO PERIÓDICA EM BACKGROUND
; ============================================================================
License_UpdateServersBackground:
    ; Verifica se há internet antes de tentar atualizar
    If (License_CheckInternet()) {
        ; Atualiza servidores em background (não bloqueia execução)
        ; Usa um timer curto para não interferir com o programa principal
        SetTimer, License_UpdateServersBackground, Off  ; Desliga temporariamente
        
        ; Tenta atualizar
        global g_ConfigEndpoint, g_LicenseAPI_Servers_Fallback
        maxFallback := g_LicenseAPI_Servers_Fallback.Length()
        
        Loop, %maxFallback%
        {
            configServer := g_LicenseAPI_Servers_Fallback[A_Index]
            configUrl := configServer . "/servers"
            
            If (InStr(g_ConfigEndpoint, "http") = 1) {
                configUrl := g_ConfigEndpoint
            }
            
            servers := License_DownloadServerConfig(configUrl)
            If (servers.Length() > 0) {
                global g_LicenseAPI_Servers
                g_LicenseAPI_Servers := servers
                License_SaveServerConfig(servers)
                FileAppend, [%A_Now%] Servidores atualizados em background`n, %A_Temp%\license_config_log.txt
                Break
            }
        }
        
        ; Reativa timer para próxima atualização
        global g_ConfigUpdateInterval
        SetTimer, License_UpdateServersBackground, % (g_ConfigUpdateInterval * 1000)
    }
Return
