#!/usr/bin/env python3
"""
Script para otimizar vídeos reduzindo tamanho mantendo qualidade
Requisitos: pip install ffmpeg-python (ou instalar ffmpeg separadamente)
"""

import os
import sys
import subprocess

def verificar_ffmpeg():
    """Verifica se ffmpeg está instalado"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                               capture_output=True, 
                               text=True, 
                               timeout=5)
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False

def obter_info_video(caminho):
    """Obtém informações do vídeo usando ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,duration,bit_rate,codec_name',
            '-of', 'json',
            caminho
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                return {
                    'width': int(stream.get('width', 0)),
                    'height': int(stream.get('height', 0)),
                    'duration': float(stream.get('duration', 0)),
                    'bit_rate': int(stream.get('bit_rate', 0)),
                    'codec': stream.get('codec_name', 'unknown')
                }
    except Exception as e:
        print(f'   ⚠️  Erro ao obter info: {e}')
    return None

def otimizar_video(caminho_entrada, caminho_saida=None, qualidade='medium', max_resolution='1080p'):
    """
    Otimiza um vídeo reduzindo tamanho mantendo qualidade
    
    Args:
        caminho_entrada: Caminho do vídeo original
        caminho_saida: Caminho de saída (se None, cria _optimized)
        qualidade: 'low', 'medium', 'high' (padrão: medium)
        max_resolution: '720p', '1080p', '1440p', '4k' ou None
    """
    
    if not os.path.exists(caminho_entrada):
        print(f'❌ Arquivo não encontrado: {caminho_entrada}')
        return False
    
    if not verificar_ffmpeg():
        print('❌ FFmpeg não está instalado!')
        print('   Instale FFmpeg:')
        print('   - Windows: choco install ffmpeg')
        print('   - Ou baixe de: https://ffmpeg.org/download.html')
        return False
    
    try:
        tamanho_original = os.path.getsize(caminho_entrada)
        print(f'📹 Processando: {os.path.basename(caminho_entrada)}')
        print(f'   Tamanho original: {tamanho_original:,} bytes ({tamanho_original/1024/1024:.2f} MB)')
        
        # Obter informações do vídeo
        info = obter_info_video(caminho_entrada)
        if info:
            print(f'   Resolução: {info["width"]}x{info["height"]}')
            print(f'   Duração: {info["duration"]:.1f}s')
            print(f'   Codec: {info["codec"]}')
            print(f'   Bitrate: {info["bit_rate"]/1000:.0f} kbps')
        
        # Determinar caminho de saída
        if caminho_saida is None:
            nome_base = os.path.splitext(caminho_entrada)[0]
            extensao = os.path.splitext(caminho_entrada)[1]
            caminho_saida = f'{nome_base}_optimized{extensao}'
        
        # Configurar resolução máxima
        resolucoes = {
            '720p': '1280:720',
            '1080p': '1920:1080',
            '1440p': '2560:1440',
            '4k': '3840:2160'
        }
        
        scale_filter = ''
        if max_resolution and max_resolution in resolucoes:
            max_w, max_h = resolucoes[max_resolution].split(':')
            if info and (info['width'] > int(max_w) or info['height'] > int(max_h)):
                # Calcular escala mantendo proporção
                ratio_w = int(max_w) / info['width']
                ratio_h = int(max_h) / info['height']
                ratio = min(ratio_w, ratio_h)
                new_w = int(info['width'] * ratio)
                new_h = int(info['height'] * ratio)
                # Garantir números pares (requisito do codec)
                new_w = new_w - (new_w % 2)
                new_h = new_h - (new_h % 2)
                scale_filter = f'scale={new_w}:{new_h}'
                print(f'   Redimensionando para: {new_w}x{new_h}')
        
        # Configurar qualidade (CRF - Constant Rate Factor)
        # Menor CRF = melhor qualidade, maior arquivo
        # 18-23 = alta qualidade, 23-28 = média, 28+ = baixa
        crf_values = {
            'low': 28,      # Menor tamanho, qualidade menor
            'medium': 23,  # Balanceado
            'high': 20     # Maior qualidade, arquivo maior
        }
        crf = crf_values.get(qualidade, 23)
        
        # Construir comando ffmpeg
        cmd = [
            'ffmpeg',
            '-i', caminho_entrada,
            '-c:v', 'libx264',           # Codec H.264
            '-crf', str(crf),            # Qualidade
            '-preset', 'medium',         # Velocidade de encoding (medium = balanceado)
            '-c:a', 'aac',               # Codec de áudio
            '-b:a', '128k',              # Bitrate de áudio
            '-movflags', '+faststart',   # Otimização para web
        ]
        
        if scale_filter:
            cmd.extend(['-vf', scale_filter])
        
        cmd.append(caminho_saida)
        
        print(f'   🔄 Otimizando (isso pode demorar)...')
        print(f'   💡 Qualidade: {qualidade} (CRF {crf})')
        
        # Executar ffmpeg
        result = subprocess.run(cmd, 
                               capture_output=True, 
                               text=True,
                               timeout=3600)  # 1 hora máximo
        
        if result.returncode != 0:
            print(f'   ❌ Erro no ffmpeg:')
            print(result.stderr[:500])  # Primeiros 500 chars do erro
            return False
        
        if not os.path.exists(caminho_saida):
            print(f'   ❌ Arquivo de saída não foi criado!')
            return False
        
        tamanho_final = os.path.getsize(caminho_saida)
        reducao = ((tamanho_original - tamanho_final) / tamanho_original) * 100
        
        print(f'   ✅ Tamanho final: {tamanho_final:,} bytes ({tamanho_final/1024/1024:.2f} MB)')
        print(f'   📉 Redução: {reducao:.1f}%')
        print()
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f'   ❌ Timeout: Processamento demorou mais de 1 hora')
        return False
    except Exception as e:
        print(f'   ❌ Erro ao processar: {e}')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('🎬 Otimizador de Vídeos - Redução de Tamanho')
    print('=' * 60)
    print()
    
    # Verificar ffmpeg
    if not verificar_ffmpeg():
        print('❌ FFmpeg não está instalado!')
        print()
        print('📥 Como instalar FFmpeg:')
        print('   Windows (Chocolatey): choco install ffmpeg')
        print('   Windows (Manual): https://ffmpeg.org/download.html')
        print('   Linux: sudo apt install ffmpeg')
        print('   Mac: brew install ffmpeg')
        print()
        sys.exit(1)
    
    print('✅ FFmpeg encontrado!')
    print()
    
    # Encontrar vídeos na raiz
    extensoes_video = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
    videos = []
    
    for ext in extensoes_video:
        videos.extend([f for f in os.listdir('.') if f.lower().endswith(ext)])
    
    if not videos:
        print('⚠️  Nenhum vídeo encontrado na raiz do projeto')
        sys.exit(0)
    
    print(f'📹 Encontrados {len(videos)} vídeo(s):')
    for video in videos:
        tamanho = os.path.getsize(video) / 1024 / 1024
        print(f'   - {video} ({tamanho:.2f} MB)')
    print()
    
    # Otimizar cada vídeo
    sucesso_total = 0
    falhas = 0
    
    for video in videos:
        if otimizar_video(video, qualidade='medium', max_resolution='1080p'):
            sucesso_total += 1
        else:
            falhas += 1
    
    print('=' * 60)
    if sucesso_total > 0:
        print(f'✅ {sucesso_total} vídeo(s) otimizado(s) com sucesso!')
    if falhas > 0:
        print(f'❌ {falhas} falha(s)')
    print('=' * 60)

