# Script para gerar credenciais seguras (API_KEY e SHARED_SECRET)
# Execute: .\gerar_credenciais.ps1

Write-Host "Gerando credenciais seguras..." -ForegroundColor Cyan
Write-Host ""

# Gera API_KEY (32 caracteres hexadecimais)
$chars = '0123456789ABCDEF'
$apiKey = -join (1..32 | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })

# Gera SHARED_SECRET (64 caracteres hexadecimais - mais longo para segurança)
$sharedSecret = -join (1..64 | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })

Write-Host "========================================" -ForegroundColor Green
Write-Host "CREDENCIAIS GERADAS:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API_KEY:" -ForegroundColor Cyan
Write-Host $apiKey -ForegroundColor White
Write-Host ""
Write-Host "SHARED_SECRET:" -ForegroundColor Cyan
Write-Host $sharedSecret -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Pergunta se quer salvar no .env do backend
$salvar = Read-Host "Deseja salvar no arquivo api/.env? (S/N)"

if ($salvar -eq "S" -or $salvar -eq "s") {
    $envFile = "api\.env"
    
    # Cria ou atualiza o arquivo .env
    $envContent = @"
API_KEY=$apiKey
SHARED_SECRET=$sharedSecret
REQUIRE_API_KEY=true
REQUIRE_SIGNATURE=true
ALLOW_AUTO_PROVISION=false
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123
"@
    
    $envContent | Out-File -Encoding utf8 $envFile
    Write-Host "[OK] Credenciais salvas em api/.env" -ForegroundColor Green
    Write-Host ""
}

# Mostra instruções para o cliente AHK
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "INSTRUCOES PARA O CLIENTE AHK:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Edite o arquivo youtube_tv_standalone.ahk:" -ForegroundColor White
Write-Host ""
Write-Host "Linha 11: g_LicenseAPI_BaseURL := `"https://api.fartgreen.fun`"" -ForegroundColor Gray
Write-Host "Linha 12: g_LicenseAPI_Key := `"$apiKey`"" -ForegroundColor Gray
Write-Host "Linha 13: g_LicenseAPI_Secret := `"$sharedSecret`"" -ForegroundColor Gray
Write-Host ""
Write-Host "OU copie estas linhas:" -ForegroundColor White
Write-Host ""
Write-Host "g_LicenseAPI_Key := `"$apiKey`"" -ForegroundColor Cyan
Write-Host "g_LicenseAPI_Secret := `"$sharedSecret`"" -ForegroundColor Cyan
Write-Host ""

# Copia para área de transferência
$clipboardText = "g_LicenseAPI_Key := `"$apiKey`"`r`ng_LicenseAPI_Secret := `"$sharedSecret`""
Set-Clipboard -Value $clipboardText
Write-Host "[OK] Credenciais copiadas para area de transferencia!" -ForegroundColor Green
Write-Host ""

