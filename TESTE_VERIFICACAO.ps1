# Script de teste para verificar se a API está respondendo corretamente

$deviceId = "2049365993desktop-j65uer12025112"
$apiKey = "CFEC44D0118C85FBA54A4B96C89140C6"
$baseUrl = "https://api.fartgreen.fun"
$version = "1.0.0"

# Gera timestamp
$timestamp = Get-Date -Format "yyyyMMddHHmmss"

# Gera assinatura (simplificado para teste)
$sharedSecret = "BF70ED46DC0E1A2A2D9B9488DE569D96A50E8EF4A23B8F79F45413371D8CAC2D"
$stringToSign = "$deviceId|$version|$timestamp|$sharedSecret"
$signature = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($stringToSign))) -replace '-',''

# Monta URL
$url = "$baseUrl/verify?id=$deviceId&version=$version&ts=$timestamp&sig=$signature&api_key=$apiKey&hostname=$env:COMPUTERNAME&username=$env:USERNAME"

Write-Host "Testando URL: $url" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri $url -TimeoutSec 15 -UseBasicParsing
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response Content:" -ForegroundColor Yellow
    Write-Host $response.Content
} catch {
    Write-Host "ERRO:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorContent = $reader.ReadToEnd()
        Write-Host "Error Response: $errorContent" -ForegroundColor Red
    }
}





