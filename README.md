# YouTube para MP3 Converter

Um aplicativo web simples para converter vídeos do YouTube para arquivos MP3.

## Executando com Docker

### Pré-requisitos
- Docker
- Docker Compose

### Instalação e Execução

1. Clone este repositório:
   ```
   git clone [URL_DO_REPOSITÓRIO]
   cd youtube-to-mp3
   ```

2. Inicie o contêiner Docker:
   ```
   docker-compose up -d
   ```

3. Acesse o aplicativo no navegador:
   ```
   http://localhost:5000
   ```

### Como usar

1. Cole a URL de um vídeo do YouTube no campo de entrada.
2. Clique no botão "Converter para MP3".
3. Aguarde o download e a conversão serem concluídos.
4. Os arquivos convertidos estão disponíveis na pasta "downloads".

## Configuração

Você pode personalizar as configurações no arquivo `.env`:

- `PORT` - A porta em que o aplicativo será executado (padrão: 5000)
- `FLASK_ENV` - O ambiente (production ou development)

## Manutenção

Para parar o serviço:
```
docker-compose down
```

Para ver os logs:
```
docker-compose logs -f
``` 