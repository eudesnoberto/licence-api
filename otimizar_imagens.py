#!/usr/bin/env python3
"""
Script para otimizar imagens PNG reduzindo tamanho mantendo qualidade
Requisitos: pip install Pillow
"""

from PIL import Image
import os
import sys

def otimizar_imagem(caminho_entrada, caminho_saida=None, qualidade=85, max_width=None, max_height=None):
    """
    Otimiza uma imagem PNG reduzindo tamanho mantendo qualidade
    
    Args:
        caminho_entrada: Caminho da imagem original
        caminho_saida: Caminho de saída (se None, sobrescreve a original)
        qualidade: Qualidade de compressão (0-100)
        max_width: Largura máxima (None = manter original)
        max_height: Altura máxima (None = manter original)
    """
    
    if not os.path.exists(caminho_entrada):
        print(f'❌ Arquivo não encontrado: {caminho_entrada}')
        return False
    
    try:
        # Carregar imagem
        print(f'📷 Processando: {os.path.basename(caminho_entrada)}')
        img = Image.open(caminho_entrada)
        
        tamanho_original = os.path.getsize(caminho_entrada)
        print(f'   Tamanho original: {tamanho_original:,} bytes ({tamanho_original/1024/1024:.2f} MB)')
        
        # Converter para RGB se necessário (PNG pode ter RGBA)
        if img.mode == 'RGBA':
            # Criar fundo branco para imagens com transparência
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Usar canal alpha como máscara
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar se necessário (mantendo proporção)
        largura_original, altura_original = img.size
        if max_width or max_height:
            if max_width and largura_original > max_width:
                ratio = max_width / largura_original
                nova_altura = int(altura_original * ratio)
                if max_height and nova_altura > max_height:
                    ratio = max_height / altura_original
                    max_width = int(largura_original * ratio)
                    nova_altura = max_height
                else:
                    max_height = nova_altura
                
                if max_width and max_height:
                    img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
                    print(f'   Redimensionado: {largura_original}x{altura_original} → {max_width}x{max_height}')
        
        # Determinar caminho de saída
        if caminho_saida is None:
            caminho_saida = caminho_entrada
        
        # Salvar otimizado
        # Para PNG, vamos tentar salvar como PNG otimizado primeiro
        # Se ainda for muito grande, converter para JPEG com alta qualidade
        
        # Tentativa 1: PNG otimizado (tentar manter formato original)
        temp_png = caminho_saida.replace('.png', '_temp.png')
        img.save(temp_png, 'PNG', optimize=True, compress_level=9)
        tamanho_png = os.path.getsize(temp_png)
        
        # Tentativa 2: JPEG com alta qualidade
        temp_jpeg = caminho_saida.replace('.png', '_temp.jpg')
        img.save(temp_jpeg, 'JPEG', quality=qualidade, optimize=True)
        tamanho_jpeg = os.path.getsize(temp_jpeg)
        
        # Escolher melhor formato (menor tamanho, mas priorizar PNG se diferença for pequena)
        diferenca_percentual = ((tamanho_png - tamanho_jpeg) / tamanho_png) * 100
        
        # Se PNG for < 1MB, manter PNG
        if tamanho_png < 1024 * 1024:
            formato_escolhido = 'PNG'
            tamanho_final = tamanho_png
            arquivo_final = temp_png
            os.remove(temp_jpeg)
        # Se JPEG for significativamente menor (>30%), usar JPEG
        elif diferenca_percentual > 30:
            formato_escolhido = 'JPEG'
            tamanho_final = tamanho_jpeg
            arquivo_final = temp_jpeg
            os.remove(temp_png)
        # Caso contrário, manter PNG (diferença pequena)
        else:
            formato_escolhido = 'PNG'
            tamanho_final = tamanho_png
            arquivo_final = temp_png
            os.remove(temp_jpeg)
        
        # Mover arquivo final para destino
        if caminho_saida == caminho_entrada:
            # Backup do original
            backup_path = caminho_entrada.replace('.png', '_original.png')
            if not os.path.exists(backup_path):
                os.rename(caminho_entrada, backup_path)
                print(f'   ✅ Backup criado: {os.path.basename(backup_path)}')
        
        # Renomear arquivo final
        if formato_escolhido == 'JPEG':
            caminho_final = caminho_saida.replace('.png', '.jpg')
        else:
            caminho_final = caminho_saida
        
        os.rename(arquivo_final, caminho_final)
        formato_final = formato_escolhido
        
        reducao = ((tamanho_original - tamanho_final) / tamanho_original) * 100
        
        print(f'   ✅ Tamanho final: {tamanho_final:,} bytes ({tamanho_final/1024/1024:.2f} MB)')
        print(f'   📉 Redução: {reducao:.1f}%')
        print(f'   🎨 Formato: {formato_final}')
        print()
        
        return True
        
    except Exception as e:
        print(f'❌ Erro ao processar {caminho_entrada}: {e}')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('🎨 Otimizador de Imagens - Redução de Tamanho')
    print('=' * 60)
    print()
    
    # Verificar se Pillow está instalado
    try:
        import PIL
    except ImportError:
        print('❌ Erro: Pillow não está instalado!')
        print('   Instale com: pip install Pillow')
        sys.exit(1)
    
    # Arquivos para otimizar
    arquivos = [
        'Whisk_0d73634550c05cb8f124c6f8de751b5fdr.png',
        'ab46f331-e688-4337-82ac-a0e3abc05bc6.png',
        'c0df15ce-1629-42ab-b144-b21310629772.png'
    ]
    
    sucesso_total = 0
    falhas = 0
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            if otimizar_imagem(arquivo, max_width=1920, max_height=1080, qualidade=90):
                sucesso_total += 1
            else:
                falhas += 1
        else:
            print(f'⚠️  Arquivo não encontrado: {arquivo}')
            falhas += 1
    
    print('=' * 60)
    if sucesso_total > 0:
        print(f'✅ {sucesso_total} imagem(ns) otimizada(s) com sucesso!')
    if falhas > 0:
        print(f'❌ {falhas} falha(s)')
    print('=' * 60)

