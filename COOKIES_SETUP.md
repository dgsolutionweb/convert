# Configuração de Cookies para o YouTube Converter

## Erro do YouTube: "Sign in to confirm you're not a bot"

Se você está recebendo o erro:
```
ERROR: [youtube] Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies for the authentication.
```

Isso ocorre porque o YouTube detecta que o download está sendo feito a partir de um servidor e está aplicando proteções anti-bot. Para resolver este problema, você precisa fornecer cookies de uma sessão autenticada do YouTube.

## Como configurar os cookies

### Passo 1: No seu computador pessoal

1. Instale a biblioteca `browser-cookie3`:
   ```
   pip install browser-cookie3
   ```

2. Faça login no YouTube no seu navegador habitual (Chrome, Firefox, etc.)

3. Baixe o script `extract-cookies.py` do projeto

4. Execute o script, especificando seu navegador:
   ```
   python extract-cookies.py chrome  # ou firefox, edge, opera, chromium
   ```

5. O script criará um arquivo `youtube.cookies.txt` no diretório atual

### Passo 2: Transferir para o servidor

1. Transfira o arquivo de cookies para o servidor usando SCP ou SFTP:
   ```
   scp youtube.cookies.txt usuario@seu_vps_ip:/caminho/para/youtube-converter/
   ```
   
2. Se estiver usando Docker, você precisa colocar o arquivo dentro do container. Execute:
   ```
   docker cp youtube.cookies.txt convert-youtube-converter-1:/app/
   ```

### Passo 3: Verificar a configuração

1. Acesse a URL do seu servidor seguida de `/cookies_status` para verificar se os cookies foram configurados corretamente:
   ```
   http://seu_vps_ip:5000/cookies_status
   ```

2. Você deverá ver uma resposta JSON indicando que o arquivo existe.

### Observações importantes

- Os cookies do YouTube expiram periodicamente, então você pode precisar repetir este processo regularmente
- Por segurança, não compartilhe o arquivo de cookies, pois ele contém dados de autenticação da sua conta do YouTube
- O arquivo de cookies deve ser colocado na raiz do aplicativo (mesmo diretório do arquivo app.py)

## Solução alternativa: Adicionar proxy

Se a configuração de cookies não funcionar ou expirar com frequência, você pode considerar a configuração de um proxy residencial, que tem menos chances de ser bloqueado pelo YouTube. 