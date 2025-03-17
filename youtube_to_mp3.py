import yt_dlp
import os
import sys

def configurar_ffmpeg():
    # Adiciona o diretório ffmpeg ao PATH
    ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg')
    if os.path.exists(ffmpeg_path):
        os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]
        return True
    return False

def baixar_e_converter_para_mp3(url, pasta_destino='downloads'):
    try:
        # Cria a pasta de downloads se não existir
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
        
        # Verifica se o FFmpeg está configurado
        if not configurar_ffmpeg():
            print("\nAVISO: FFmpeg não encontrado na pasta 'ffmpeg'!")
            print("Por favor, baixe o FFmpeg de https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
            print("Extraia o conteúdo da pasta 'bin' para uma pasta chamada 'ffmpeg' neste diretório")
            return
        
        # Configurações do yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
            'verbose': True,
            'progress_hooks': [lambda d: print(f"Baixando: {d['_percent_str']} concluído") if d['status'] == 'downloading' else None],
        }
        
        print("\nIniciando download e conversão...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info['title']
            print(f"\nDownload e conversão concluídos!")
            print(f"Arquivo salvo em: {pasta_destino}/{titulo}.mp3")
            
    except Exception as e:
        print(f"\nOcorreu um erro: {str(e)}")
        print("\nDicas de solução:")
        print("1. Verifique se a URL do vídeo está correta")
        print("2. Verifique sua conexão com a internet")
        print("3. Certifique-se que o vídeo está disponível no seu país")
        print("4. O vídeo pode ter restrições de idade ou privacidade")
        print("5. Certifique-se que o FFmpeg está instalado corretamente")

if __name__ == "__main__":
    print("=== Conversor de YouTube para MP3 ===")
    print("Desenvolvido com yt-dlp para máxima compatibilidade")
    
    # Verifica FFmpeg no início
    if not configurar_ffmpeg():
        print("\nAVISO: FFmpeg não encontrado!")
        print("Por favor, siga estas instruções:")
        print("1. Baixe o FFmpeg de: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
        print("2. Extraia o arquivo zip")
        print("3. Copie os arquivos da pasta 'bin' para uma pasta chamada 'ffmpeg' neste diretório")
        print("4. Execute este script novamente")
        sys.exit(1)
    
    while True:
        try:
            url = input("\nCole a URL do vídeo do YouTube (ou 'sair' para encerrar): ")
            if url.lower() == 'sair':
                break
            
            if not url.strip():
                print("Por favor, insira uma URL válida")
                continue
                
            if not url.startswith(('http://', 'https://', 'www.', 'youtube.com', 'youtu.be')):
                print("Por favor, insira uma URL válida do YouTube")
                continue
            
            baixar_e_converter_para_mp3(url)
            print("\nPronto para converter outro vídeo!")
            
        except KeyboardInterrupt:
            print("\nPrograma encerrado pelo usuário")
            sys.exit(0)
        except Exception as e:
            print(f"\nErro inesperado: {str(e)}")
            print("Tente novamente com outro vídeo ou digite 'sair' para encerrar") 