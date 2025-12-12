; ============================================================================
; EXEMPLO: Configuração de URLs dos Servidores
; ============================================================================
; Copie e cole no seu arquivo SOLUCAO_COM_REDUNDANCIA.ahk
; ============================================================================

; ============================================================================
; OPÇÃO 1: URLs Padrão dos Serviços (Mais Fácil)
; ============================================================================
g_LicenseAPI_Servers := []
g_LicenseAPI_Servers[1] := "https://licence-api-production.up.railway.app"  ; Railway (Principal)
g_LicenseAPI_Servers[2] := "https://licence-api-backup1.onrender.com"     ; Render (Backup 1)
g_LicenseAPI_Servers[3] := "https://licence-api-backup2.fly.dev"            ; Fly.io (Backup 2)

; ============================================================================
; OPÇÃO 2: URLs com Domínios Customizados (Mais Profissional)
; ============================================================================
; Se você configurou domínios customizados:
; g_LicenseAPI_Servers := []
; g_LicenseAPI_Servers[1] := "https://api.fartgreen.fun"           ; Principal
; g_LicenseAPI_Servers[2] := "https://api-backup1.fartgreen.fun"   ; Backup 1
; g_LicenseAPI_Servers[3] := "https://api-backup2.fartgreen.fun"   ; Backup 2

; ============================================================================
; OPÇÃO 3: Apenas 2 Servidores (Mais Simples)
; ============================================================================
; Se quiser apenas 2 servidores:
; g_LicenseAPI_Servers := []
; g_LicenseAPI_Servers[1] := "https://licence-api-production.up.railway.app"  ; Principal
; g_LicenseAPI_Servers[2] := "https://licence-api-backup1.onrender.com"        ; Backup

; ============================================================================
; IMPORTANTE:
; ============================================================================
; 1. Substitua as URLs acima pelas URLs REAIS dos seus servidores
; 2. Você obterá as URLs após fazer deploy em cada serviço
; 3. Railway: URL aparece após deploy (ex: xxx.railway.app)
; 4. Render: URL aparece após deploy (ex: xxx.onrender.com)
; 5. Fly.io: URL aparece após deploy (ex: xxx.fly.dev)
; ============================================================================



