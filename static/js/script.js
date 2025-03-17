document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('url-input');
    const convertBtn = document.getElementById('convert-btn');
    const downloadList = document.getElementById('download-list');
    const errorMessage = document.getElementById('error-message');
    
    // Map para armazenar os intervalos de verificação de status
    const statusCheckers = new Map();
    
    // Função para mostrar erro
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
    
    // Lidar com erros de conexão
    function handleConnectionError() {
        showError('Erro de conexão com o servidor. Verifique se o servidor está em execução.');
    }
    
    // Adicionar um manipulador de eventos para capturar erros de conexão
    window.addEventListener('error', (e) => {
        if (
            e.target instanceof HTMLScriptElement ||
            e.target instanceof HTMLLinkElement ||
            e.target instanceof HTMLImageElement
        ) {
            handleConnectionError();
        }
    });
    
    // Função para atualizar o status do download
    function updateDownloadStatus(downloadId, status) {
        const downloadItem = document.getElementById(`download-${downloadId}`);
        if (!downloadItem) {
            const newItem = document.createElement('div');
            newItem.id = `download-${downloadId}`;
            newItem.className = 'download-item';
            downloadList.appendChild(newItem);
        }
    
        const item = document.getElementById(`download-${downloadId}`);
        
        if (status.status === 'downloading') {
            const progress = status.progress.toFixed(1);
            const speed = (status.speed / 1024 / 1024).toFixed(2);
            const eta = status.eta;
            
            item.innerHTML = `
                <div class="download-info">
                    <div class="filename">${downloadId}</div>
                    <div class="progress-bar">
                        <div class="progress" style="width: ${progress}%"></div>
                    </div>
                    <div class="status-info">
                        <span>${progress}%</span>
                        <span>${speed} MB/s</span>
                        <span>ETA: ${eta}s</span>
                    </div>
                </div>
            `;
        } else if (status.status === 'converting') {
            item.innerHTML = `
                <div class="download-info">
                    <div class="filename">${downloadId}</div>
                    <div class="progress-bar">
                        <div class="progress" style="width: 100%"></div>
                    </div>
                    <div class="status-info">
                        <span>Convertendo para MP3...</span>
                    </div>
                </div>
            `;
        } else if (status.status === 'finished') {
            item.innerHTML = `
                <div class="download-info">
                    <div class="filename">${downloadId}</div>
                    <div class="status-info success">
                        <span>Conversão concluída!</span>
                    </div>
                    <div class="download-actions">
                        <a href="${status.download_url}" class="download-btn">
                            <i class="fas fa-download"></i> Salvar MP3
                        </a>
                    </div>
                </div>
            `;
            clearInterval(statusCheckers.get(downloadId));
            statusCheckers.delete(downloadId);
        } else if (status.status === 'error') {
            item.innerHTML = `
                <div class="download-info">
                    <div class="filename">${downloadId}</div>
                    <div class="status-info error">
                        <span>Erro: ${status.error}</span>
                    </div>
                </div>
            `;
            clearInterval(statusCheckers.get(downloadId));
            statusCheckers.delete(downloadId);
        }
    }
    
    // Função para iniciar o monitoramento de status
    function startStatusChecker(downloadId) {
        if (statusCheckers.has(downloadId)) {
            clearInterval(statusCheckers.get(downloadId));
        }
    
        let retries = 0;
        const maxRetries = 180; // 3 minutos
    
        statusCheckers.set(downloadId, setInterval(() => {
            fetch(`/status/${encodeURIComponent(downloadId)}`)
                .then(response => response.json())
                .then(status => {
                    if (status && status.status !== 'not_found') {
                        updateDownloadStatus(downloadId, status);
                        if (status.status === 'finished' || status.status === 'error') {
                            clearInterval(statusCheckers.get(downloadId));
                            statusCheckers.delete(downloadId);
                        }
                    }
                    retries++;
                    if (retries >= maxRetries) {
                        clearInterval(statusCheckers.get(downloadId));
                        statusCheckers.delete(downloadId);
                        updateDownloadStatus(downloadId, {
                            status: 'error',
                            error: 'Tempo limite excedido'
                        });
                    }
                })
                .catch(error => {
                    console.error('Erro ao verificar status:', error);
                    retries++;
                    if (retries >= maxRetries) {
                        clearInterval(statusCheckers.get(downloadId));
                        statusCheckers.delete(downloadId);
                        updateDownloadStatus(downloadId, {
                            status: 'error',
                            error: 'Erro ao verificar status'
                        });
                    }
                });
        }, 1000));
    }
    
    // Event handler para o botão de download
    convertBtn.addEventListener('click', function() {
        const url = urlInput.value.trim();
        if (!url) {
            showError('Por favor, insira uma URL do YouTube');
            return;
        }
        
        // Verificar se é uma URL do YouTube válida
        if (!url.match(/^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/)) {
            showError('Por favor, insira uma URL válida do YouTube');
            return;
        }
        
        // Enviar a solicitação de download
        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                startStatusChecker(data.download_id);
                urlInput.value = '';
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showError('Erro ao se comunicar com o servidor');
        });
    });
    
    // Permitir pressionar Enter para iniciar o download
    urlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            convertBtn.click();
        }
    });
}); 