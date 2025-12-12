# Script para instalar FFmpeg no Windows
# Requer Chocolatey ou pode ser instalado manualmente

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🎬 Instalador de FFmpeg para Otimização de Vídeos" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se já está instalado
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    if ($ffmpegVersion -match "ffmpeg version") {
        Write-Host "✅ FFmpeg já está instalado!" -ForegroundColor Green
        Write-Host $ffmpegVersion
        exit 0
    }
} catch {
    # Não está instalado, continuar
}

Write-Host "📥 FFmpeg não encontrado. Instalando..." -ForegroundColor Yellow
Write-Host ""

# Tentar instalar via Chocolatey
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if ($chocoInstalled) {
    Write-Host "✅ Chocolatey encontrado. Instalando FFmpeg..." -ForegroundColor Green
    try {
        choco install ffmpeg -y
        Write-Host ""
        Write-Host "✅ FFmpeg instalado com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "💡 Reinicie o terminal e execute: python otimizar_videos.py" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ Erro ao instalar via Chocolatey" -ForegroundColor Red
        Write-Host ""
        Write-Host "📥 Instalação Manual:" -ForegroundColor Yellow
        Write-Host "   1. Acesse: https://ffmpeg.org/download.html" -ForegroundColor White
        Write-Host "   2. Baixe a versão Windows" -ForegroundColor White
        Write-Host "   3. Extraia e adicione ao PATH" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  Chocolatey não encontrado." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📥 Opções de Instalação:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Opção 1 - Chocolatey (Recomendado):" -ForegroundColor Green
    Write-Host "   1. Instale Chocolatey: https://chocolatey.org/install" -ForegroundColor White
    Write-Host "   2. Execute: choco install ffmpeg" -ForegroundColor White
    Write-Host ""
    Write-Host "Opção 2 - Download Manual:" -ForegroundColor Green
    Write-Host "   1. Acesse: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor White
    Write-Host "   2. Baixe 'ffmpeg-release-essentials.zip'" -ForegroundColor White
    Write-Host "   3. Extraia em C:\ffmpeg" -ForegroundColor White
    Write-Host "   4. Adicione C:\ffmpeg\bin ao PATH do sistema" -ForegroundColor White
    Write-Host ""
    Write-Host "Opção 3 - Winget (Windows 10/11):" -ForegroundColor Green
    Write-Host "   winget install ffmpeg" -ForegroundColor White
    Write-Host ""
}

Write-Host "============================================================" -ForegroundColor Cyan

