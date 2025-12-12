#!/usr/bin/env python3
"""
Script para gerar favicons e ícones do site a partir de uma imagem PNG
Requisitos: pip install Pillow
"""

from PIL import Image
import os
import sys

def gerar_favicons(imagem_origem='../favico.png', pasta_destino='public'):
    """Gera todos os tamanhos de favicon e ícones necessários"""
    
    # Verificar se a imagem existe
    if not os.path.exists(imagem_origem):
        print(f'❌ Erro: Arquivo {imagem_origem} não encontrado!')
        print(f'   Certifique-se de que o arquivo favico.png está na raiz do projeto.')
        return False
    
    # Criar pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    try:
        # Carregar imagem original
        print(f'📷 Carregando imagem: {imagem_origem}')
        img = Image.open(imagem_origem)
        
        # Converter para RGBA se necessário (para suportar transparência)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Tamanhos necessários
        tamanhos = {
            'favicon-16x16.png': 16,
            'favicon-32x32.png': 32,
            'apple-touch-icon.png': 180,
            'icon-192.png': 192,
            'icon-512.png': 512,
        }
        
        print(f'\n🔄 Gerando {len(tamanhos)} ícones...\n')
        
        # Gerar cada tamanho
        for filename, size in tamanhos.items():
            caminho = os.path.join(pasta_destino, filename)
            
            # Redimensionar com alta qualidade
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Salvar
            resized.save(caminho, 'PNG', optimize=True)
            
            print(f'✅ {filename:25} ({size:3}x{size:3}) - {os.path.getsize(caminho):6,} bytes')
        
        # Gerar favicon.ico (formato ICO com múltiplos tamanhos)
        print(f'\n🔄 Gerando favicon.ico...')
        favicon_path = os.path.join(pasta_destino, 'favicon.ico')
        
        # Criar lista de imagens em diferentes tamanhos para o ICO
        ico_sizes = [16, 32, 48]
        ico_images = []
        for ico_size in ico_sizes:
            ico_img = img.resize((ico_size, ico_size), Image.Resampling.LANCZOS)
            ico_images.append(ico_img)
        
        # Salvar como ICO
        ico_images[0].save(
            favicon_path,
            format='ICO',
            sizes=[(s, s) for s in ico_sizes],
            append_images=ico_images[1:] if len(ico_images) > 1 else []
        )
        
        print(f'✅ favicon.ico              (múltiplos) - {os.path.getsize(favicon_path):6,} bytes')
        
        print(f'\n✨ Todos os ícones foram gerados com sucesso!')
        print(f'📁 Arquivos salvos em: {os.path.abspath(pasta_destino)}')
        print(f'\n💡 Próximo passo: Recarregue o site para ver os novos ícones!')
        
        return True
        
    except Exception as e:
        print(f'❌ Erro ao processar imagem: {e}')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('🎨 Gerador de Favicons - Easy Play Rockola')
    print('=' * 60)
    print()
    
    # Verificar se Pillow está instalado
    try:
        import PIL
    except ImportError:
        print('❌ Erro: Pillow não está instalado!')
        print('   Instale com: pip install Pillow')
        sys.exit(1)
    
    # Executar
    sucesso = gerar_favicons()
    
    if not sucesso:
        sys.exit(1)

