document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('url');
    const downloadBtn = document.getElementById('download-btn');
    const errorMessage = document.getElementById('error-message');
    const downloadsContainer = document.getElementById('downloads-container');
    const downloadTemplate = document.getElementById('download-item-template');

    // Mapa para armazenar os intervalos de atualização de status
    const statusCheckers = new Map();

    // Função para mostrar erro
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
        setTimeout(() => {
            errorMessage.classList.add('d-none');
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

    // Função para criar um novo item de download
    function createDownloadItem(title, downloadId) {
        const clone = downloadTemplate.content.cloneNode(true);
        const downloadItem = clone.querySelector('.download-item');
        
        downloadItem.id = `download-${downloadId}`;
        downloadItem.querySelector('.video-title').textContent = title;
        
        downloadsContainer.insertBefore(downloadItem, downloadsContainer.firstChild);
        return downloadItem;
    }

    // Função para atualizar o status do download
    function updateDownloadStatus(downloadId, status) {
        const downloadItem = document.getElementById(`download-${downloadId}`);
        if (!downloadItem) {
            const downloadList = document.getElementById('download-list');
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
                        <a href="${status.download_url}" class="btn btn-success download-btn">
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
                    if (status) {
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

    // Handler do botão de download
    downloadBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        
        if (!url) {
            showError('Por favor, insira uma URL do YouTube');
            return;
        }

        if (!url.match(/^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/)) {
            showError('Por favor, insira uma URL válida do YouTube');
            return;
        }

        // Desabilita o botão durante o processo
        downloadBtn.disabled = true;
        
        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
            });

            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
            } else {
                const downloadItem = createDownloadItem(data.title, data.download_id);
                startStatusChecker(data.download_id);
                urlInput.value = '';
            }
        } catch (error) {
            showError('Erro ao iniciar o download. Por favor, tente novamente.');
        } finally {
            downloadBtn.disabled = false;
        }
    });

    // Permite pressionar Enter para iniciar o download
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            downloadBtn.click();
        }
    });
}); 