from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import sys
from threading import Thread
import time
import json
import threading

app = Flask(__name__)

# Dicionário global para armazenar o progresso dos downloads
download_progress = {}

# Configuração de downloads e status
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Dicionário para armazenar o status dos downloads
downloads_status = {}

def configurar_ffmpeg():
    # Verifica se estamos em um ambiente Docker (onde FFmpeg já está instalado)
    if os.environ.get('FLASK_ENV') == 'production':
        return True
    
    # Para ambiente de desenvolvimento local
    ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg')
    if os.path.exists(ffmpeg_path):
        os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]
        return True
    return False

def download_callback(d):
    if d['status'] == 'downloading':
        download_progress[d['info_dict']['title']] = {
            'status': 'downloading',
            'progress': d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100,
            'speed': d.get('speed', 0),
            'eta': d.get('eta', 0)
        }
    elif d['status'] == 'finished':
        download_progress[d['info_dict']['title']] = {
            'status': 'converting',
            'progress': 100
        }
    elif d['status'] == 'error':
        download_progress[d['info_dict']['title']] = {
            'status': 'error',
            'error': str(d.get('error', 'Erro desconhecido'))
        }

def download_thread(url, download_id):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
            'progress_hooks': [download_callback],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', '')
            if not video_title:
                raise Exception('Não foi possível obter o título do vídeo')
                
            download_progress[video_title] = {
                'status': 'starting',
                'progress': 0
            }
            
            # Agora fazemos o download
            ydl.download([url])
            
            # Verificamos se o arquivo MP3 foi criado
            mp3_filename = f"{video_title}.mp3"
            expected_mp3 = os.path.join('downloads', mp3_filename)
            if os.path.exists(expected_mp3):
                download_progress[video_title] = {
                    'status': 'finished',
                    'progress': 100,
                    'download_url': f'/download_file/{mp3_filename}'
                }
            else:
                raise Exception('Arquivo MP3 não foi criado')
                
    except Exception as e:
        print(f"Erro no download: {str(e)}")
        if 'video_title' in locals():
            download_progress[video_title] = {
                'status': 'error',
                'error': str(e)
            }

def baixar_video(url):
    try:
        if not configurar_ffmpeg():
            return {'error': 'FFmpeg não encontrado. Por favor, configure o FFmpeg primeiro.'}

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'progress_hooks': [download_callback],
            'postprocessor_hooks': [download_callback],
            'keepvideo': False,
        }

        def download_thread(url, ydl_opts):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_title = info['title']
                    download_id = f"{video_title}.mp3"
                    
                    # Verifica se o arquivo foi convertido com sucesso
                    mp3_path = os.path.join(DOWNLOAD_FOLDER, f"{video_title}.mp3")
                    if os.path.exists(mp3_path):
                        downloads_status[download_id] = {
                            'status': 'finished',
                            'percent': '100%'
                        }
                    else:
                        downloads_status[download_id] = {
                            'status': 'error',
                            'error': 'Falha na conversão'
                        }
            except Exception as e:
                print(f"Erro no download: {str(e)}")
                if video_title and download_id:
                    downloads_status[download_id] = {
                        'status': 'error',
                        'error': str(e)
                    }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info['title']
            download_id = f"{video_title}.mp3"
            downloads_status[download_id] = {
                'status': 'starting',
                'percent': '0%'
            }
            
            thread = Thread(target=download_thread, args=(url, ydl_opts))
            thread.start()
            
            return {
                'success': True,
                'title': video_title,
                'download_id': download_id
            }

    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'URL não fornecida'}), 400

        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', '')
            if not video_title:
                return jsonify({'error': 'Não foi possível obter o título do vídeo'}), 400

            thread = threading.Thread(target=download_thread, args=(url, video_title))
            thread.start()

            return jsonify({
                'title': video_title,
                'download_id': video_title
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<download_id>')
def get_status(download_id):
    try:
        if download_id in download_progress:
            return jsonify(download_progress[download_id])
        else:
            return jsonify({'status': 'not_found'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        return send_from_directory('downloads', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not configurar_ffmpeg():
        print("\nAVISO: FFmpeg não encontrado!")
        print("Por favor, siga estas instruções:")
        print("1. Baixe o FFmpeg de: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
        print("2. Extraia o arquivo zip")
        print("3. Copie os arquivos da pasta 'bin' para uma pasta chamada 'ffmpeg' neste diretório")
        print("4. Execute este script novamente")
        sys.exit(1)
    
    # Configuração para ambiente de produção ou desenvolvimento
    import os
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))
    
    # Em produção, permitimos conexões de qualquer origem
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 