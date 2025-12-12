# Script PowerShell para gerar favicons (requer ImageMagick)
# Instale ImageMagick: choco install imagemagick

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🎨 Gerador de Favicons - Easy Play Rockola" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$imagemOrigem = "..\favico.png"
$pastaDestino = "public"

# Verificar se ImageMagick está instalado
try {
    $magickVersion = magick -version 2>&1
    Write-Host "✅ ImageMagick encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ ImageMagick não encontrado!" -ForegroundColor Red
    Write-Host "   Instale com: choco install imagemagick" -ForegroundColor Yellow
    Write-Host "   Ou baixe de: https://imagemagick.org/script/download.php" -ForegroundColor Yellow
    exit 1
}

# Verificar se a imagem existe
if (-not (Test-Path $imagemOrigem)) {
    Write-Host "❌ Erro: Arquivo $imagemOrigem não encontrado!" -ForegroundColor Red
    Write-Host "   Certifique-se de que o arquivo favico.png está na raiz do projeto." -ForegroundColor Yellow
    exit 1
}

# Criar pasta de destino
if (-not (Test-Path $pastaDestino)) {
    New-Item -ItemType Directory -Path $pastaDestino | Out-Null
    Write-Host "📁 Pasta criada: $pastaDestino" -ForegroundColor Green
}

Write-Host "📷 Processando imagem: $imagemOrigem" -ForegroundColor Cyan
Write-Host ""

# Tamanhos necessários
$tamanhos = @{
    "favicon-16x16.png" = 16
    "favicon-32x32.png" = 32
    "apple-touch-icon.png" = 180
    "icon-192.png" = 192
    "icon-512.png" = 512
}

Write-Host "🔄 Gerando ícones PNG..." -ForegroundColor Cyan
Write-Host ""

foreach ($item in $tamanhos.GetEnumerator()) {
    $filename = $item.Key
    $size = $item.Value
    $caminho = Join-Path $pastaDestino $filename
    
    magick $imagemOrigem -resize "${size}x${size}" -quality 95 $caminho
    
    $fileSize = (Get-Item $caminho).Length
    Write-Host "✅ $($filename.PadRight(25)) ($($size.ToString().PadLeft(3))x$($size.ToString().PadLeft(3))) - $($fileSize.ToString('N0').PadLeft(8)) bytes" -ForegroundColor Green
}

# Gerar favicon.ico
Write-Host ""
Write-Host "🔄 Gerando favicon.ico..." -ForegroundColor Cyan
$faviconPath = Join-Path $pastaDestino "favicon.ico"

# Criar ICO com múltiplos tamanhos
magick $imagemOrigem `
    \( -clone 0 -resize 16x16 \) `
    \( -clone 0 -resize 32x32 \) `
    \( -clone 0 -resize 48x48 \) `
    -delete 0 `
    -alpha off `
    -colors 256 `
    $faviconPath

$icoSize = (Get-Item $faviconPath).Length
Write-Host "✅ favicon.ico              (múltiplos) - $($icoSize.ToString('N0').PadLeft(8)) bytes" -ForegroundColor Green

Write-Host ""
Write-Host "✨ Todos os ícones foram gerados com sucesso!" -ForegroundColor Green
Write-Host "📁 Arquivos salvos em: $(Resolve-Path $pastaDestino)" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Próximo passo: Recarregue o site para ver os novos ícones!" -ForegroundColor Yellow

