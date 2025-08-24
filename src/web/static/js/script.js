// AcademicPlot Pro - Main JavaScript
// Fixes file upload bug and provides modern interactive functionality

class AcademicPlotApp {
    constructor() {
        this.currentFile = null;
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.initAccordions();
        this.initSliders();
        this.updateProcessButton();
    }

    bindEvents() {
        // File input change
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Drag and drop
        const dropZone = document.getElementById('dropZone');
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.name.endsWith('.py')) {
                    this.handleFileSelect(file);
                } else {
                    this.showError('请选择Python文件 (.py)');
                }
            }
        });

        // Click to select file
        dropZone.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        // Remove file button
        document.getElementById('removeFile').addEventListener('click', () => {
            this.removeFile();
        });

        // Process button
        document.getElementById('processBtn').addEventListener('click', () => {
            this.processFile();
        });

        // Toggle events
        document.getElementById('academicToggle').addEventListener('change', (e) => {
            this.toggleAcademicOptions(e.target.checked);
        });

        document.getElementById('customToggle').addEventListener('change', (e) => {
            this.toggleCustomOptions(e.target.checked);
        });

        // Accordion headers
        document.querySelectorAll('.accordion-header').forEach(header => {
            header.addEventListener('click', () => {
                this.toggleAccordion(header);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'u' && !this.isProcessing) {
                e.preventDefault();
                document.getElementById('fileInput').click();
            }
            
            if (e.ctrlKey && e.key === 'Enter' && this.currentFile && !this.isProcessing) {
                e.preventDefault();
                this.processFile();
            }
        });

        // User guide modal
        document.getElementById('userGuideLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.showUserGuide();
        });

        // Modal close button
        document.querySelector('.modal-close').addEventListener('click', () => {
            this.hideUserGuide();
        });

        // Close modal when clicking outside
        document.getElementById('userGuideModal').addEventListener('click', (e) => {
            if (e.target === document.getElementById('userGuideModal')) {
                this.hideUserGuide();
            }
        });
    }

    initAccordions() {
        // Open first accordion by default
        const firstAccordion = document.querySelector('.accordion-header');
        if (firstAccordion) {
            this.toggleAccordion(firstAccordion, true);
        }
    }

    initSliders() {
        // Initialize all sliders with value display
        const sliders = [
            { id: 'dpi', valueId: 'dpiValue', suffix: ' DPI' },
            { id: 'fontSize', valueId: 'fontSizeValue', suffix: ' pt' },
            { id: 'titleSize', valueId: 'titleSizeValue', suffix: ' pt' },
            { id: 'figWidth', valueId: 'figWidthValue', suffix: ' 英寸' },
            { id: 'figHeight', valueId: 'figHeightValue', suffix: ' 英寸' },
            { id: 'customDpi', valueId: 'customDpiValue', suffix: ' DPI' }
        ];

        sliders.forEach(({ id, valueId, suffix }) => {
            const slider = document.getElementById(id);
            const valueDisplay = document.getElementById(valueId);
            
            if (slider && valueDisplay) {
                // Set initial value
                valueDisplay.textContent = slider.value + suffix;
                
                // Update on change
                slider.addEventListener('input', () => {
                    valueDisplay.textContent = slider.value + suffix;
                });
            }
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        this.currentFile = file;
        
        // Update file info display
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = this.formatFileSize(file.size);
        
        // Show file preview
        document.getElementById('filePreview').classList.add('visible');
        
        // Update process button state
        this.updateProcessButton();
        
        // Update status
        this.updateStatus('文件已选择，准备处理', 'success');
        
        // Hide results if previously shown
        this.hideResults();
    }

    removeFile() {
        this.currentFile = null;
        
        // Reset file input
        document.getElementById('fileInput').value = '';
        
        // Hide file preview
        document.getElementById('filePreview').classList.remove('visible');
        
        // Update process button state
        this.updateProcessButton();
        
        // Update status
        this.updateStatus('等待文件上传', 'success');
        
        // Hide results
        this.hideResults();
    }

    updateProcessButton() {
        const processBtn = document.getElementById('processBtn');
        processBtn.disabled = !this.currentFile || this.isProcessing;
    }

    processFile() {
        if (!this.currentFile || this.isProcessing) return;

        this.isProcessing = true;
        this.updateProcessButton();
        this.showLoading();
        this.updateStatus('正在处理文件...', 'warning');

        const formData = new FormData();
        formData.append('file', this.currentFile);
        
        // Get all settings
        formData.append('beautify', document.getElementById('beautifyToggle').checked);
        formData.append('academic_mode', document.getElementById('academicToggle').checked);
        
        if (document.getElementById('academicToggle').checked) {
            formData.append('paper_format', document.getElementById('paperFormat').value);
            formData.append('layout', document.getElementById('layout').value);
            formData.append('vector_format', document.getElementById('vectorFormat').value);
            formData.append('dpi', document.getElementById('dpi').value);
            formData.append('custom_mode', document.getElementById('customToggle').checked);
            
            if (document.getElementById('customToggle').checked) {
                formData.append('font_size', document.getElementById('fontSize').value);
                formData.append('title_size', document.getElementById('titleSize').value);
                formData.append('fig_width', document.getElementById('figWidth').value);
                formData.append('fig_height', document.getElementById('figHeight').value);
                formData.append('custom_dpi', document.getElementById('customDpi').value);
            }
        }

        // Use fetch with streaming response
        fetch('/process', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            // Create a reader to read the stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            function readStream() {
                return reader.read().then(({ done, value }) => {
                    if (done) {
                        return;
                    }
                    
                    // Decode the chunk and process SSE messages
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                
                                if (data.error) {
                                    this.showError('处理错误: ' + data.error);
                                    this.updateStatus('处理失败', 'error');
                                    this.isProcessing = false;
                                    this.hideLoading();
                                    this.updateProcessButton();
                                    return;
                                }
                                
                                if (data.status) {
                                    this.updateStatus(data.status, 'warning');
                                }
                                
                                if (data.success) {
                                    this.showSuccess(data.download_url);
                                    this.updateStatus('处理完成！', 'success');
                                    this.isProcessing = false;
                                    this.hideLoading();
                                    this.updateProcessButton();
                                    return;
                                }
                                
                            } catch (error) {
                                console.error('Error parsing SSE message:', error, line);
                            }
                        }
                    }
                    
                    // Continue reading the stream
                    return readStream();
                });
            }
            
            return readStream();
        })
        .catch(error => {
            console.error('Fetch error:', error);
            this.showError('请求发送失败: ' + error.message);
            this.updateStatus('处理失败', 'error');
            this.isProcessing = false;
            this.hideLoading();
            this.updateProcessButton();
        });
    }

    toggleAcademicOptions(enabled) {
        const academicOptions = document.getElementById('academicOptions');
        academicOptions.style.display = enabled ? 'block' : 'none';
        
        // If academic mode is disabled, also disable custom mode
        if (!enabled) {
            document.getElementById('customToggle').checked = false;
            this.toggleCustomOptions(false);
        }
    }

    toggleCustomOptions(enabled) {
        const customOptions = document.getElementById('customOptions');
        customOptions.style.display = enabled ? 'block' : 'none';
    }

    toggleAccordion(header, forceOpen = false) {
        const targetId = header.getAttribute('data-target');
        const content = document.getElementById(targetId);
        const isCurrentlyOpen = header.classList.contains('active');
        
        // Close all other accordions
        document.querySelectorAll('.accordion-header').forEach(h => {
            if (h !== header) {
                h.classList.remove('active');
                document.getElementById(h.getAttribute('data-target')).classList.remove('active');
            }
        });
        
        // Toggle this accordion
        if (forceOpen || !isCurrentlyOpen) {
            header.classList.add('active');
            content.classList.add('active');
        } else {
            header.classList.remove('active');
            content.classList.remove('active');
        }
    }

    showLoading() {
        const processBtn = document.getElementById('processBtn');
        processBtn.classList.add('loading');
    }

    hideLoading() {
        const processBtn = document.getElementById('processBtn');
        processBtn.classList.remove('loading');
    }

    showSuccess(downloadUrl) {
        const downloadLink = document.getElementById('downloadLink');
        downloadLink.href = downloadUrl;
        
        document.querySelector('.results-success').style.display = 'block';
        document.querySelector('.results-placeholder').style.display = 'none';
        
        // Scroll to results
        document.getElementById('resultsCard').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest' 
        });
    }

    hideResults() {
        document.querySelector('.results-success').style.display = 'none';
        document.querySelector('.results-placeholder').style.display = 'block';
    }

    updateStatus(message, type = 'success') {
        const statusElement = document.querySelector('.status-item');
        
        // Clear existing classes
        statusElement.className = 'status-item';
        
        // Set new class and content
        const iconClass = {
            success: 'fas fa-check-circle status-success',
            warning: 'fas fa-exclamation-circle status-warning',
            error: 'fas fa-times-circle status-error'
        }[type];
        
        statusElement.innerHTML = `
            <i class="${iconClass}"></i>
            <span>${message}</span>
        `;
    }

    showError(message) {
        // Create error toast
        const toast = document.createElement('div');
        toast.className = 'error-toast';
        toast.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add styles
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fef2f2;
            color: #dc2626;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #fecaca;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            max-width: 400px;
            animation: slideInRight 0.3s ease;
        `;
        
        // Add close button event
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showUserGuide() {
        const modal = document.getElementById('userGuideModal');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    hideUserGuide() {
        const modal = document.getElementById('userGuideModal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AcademicPlotApp();
});

// Add CSS for error toast
const toastStyles = `
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.error-toast {
    font-family: 'Inter', sans-serif;
}

.error-toast .toast-close {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    margin-left: 8px;
}

.error-toast .toast-close:hover {
    background: rgba(220, 38, 38, 0.1);
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = toastStyles;
document.head.appendChild(styleSheet);