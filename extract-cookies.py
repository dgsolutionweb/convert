#!/usr/bin/env python
# Este script extrai cookies do YouTube de um navegador

import json
import os
import sys
import browser_cookie3

def extract_cookies_to_file(browser_name, output_file):
    """
    Extrai cookies do navegador especificado e salva em um arquivo.
    Navegadores suportados: chrome, firefox, opera, edge, chromium
    """
    try:
        if browser_name.lower() == 'chrome':
            cookies = browser_cookie3.chrome(domain_name='.youtube.com')
        elif browser_name.lower() == 'firefox':
            cookies = browser_cookie3.firefox(domain_name='.youtube.com')
        elif browser_name.lower() == 'opera':
            cookies = browser_cookie3.opera(domain_name='.youtube.com')
        elif browser_name.lower() == 'edge':
            cookies = browser_cookie3.edge(domain_name='.youtube.com')
        elif browser_name.lower() == 'chromium':
            cookies = browser_cookie3.chromium(domain_name='.youtube.com')
        else:
            print(f"Navegador não suportado: {browser_name}")
            print("Navegadores suportados: chrome, firefox, opera, edge, chromium")
            return False
            
        # Converter para o formato Netscape (usado pelo yt-dlp)
        with open(output_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
            f.write("# This is a generated file! Do not edit.\n\n")
            
            for cookie in cookies:
                secure = "TRUE" if cookie.secure else "FALSE"
                http_only = "TRUE" if cookie.has_nonstandard_attr('HttpOnly') else "FALSE"
                expiry = str(cookie.expires) if cookie.expires else "0"
                
                f.write(f".youtube.com\tTRUE\t/\t{secure}\t{expiry}\t{cookie.name}\t{cookie.value}\n")
                
        print(f"Cookies extraídos com sucesso para {output_file}")
        return True
        
    except Exception as e:
        print(f"Erro ao extrair cookies: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python extract-cookies.py [chrome|firefox|opera|edge|chromium]")
        sys.exit(1)
    
    browser = sys.argv[1]
    output_file = "youtube.cookies.txt"
    
    if extract_cookies_to_file(browser, output_file):
        print("Execute o seguinte comando para transferir o arquivo para o seu VPS:")
        print(f"scp {output_file} usuario@seu_vps_ip:/caminho/para/youtube-converter/")
    else:
        print("Falha ao extrair cookies.") 