// AcademicPlot Pro - Main JavaScript
// Fixes file upload bug and provides modern interactive functionality

class AcademicPlotApp {
    constructor() {
        this.currentFile = null;
        this.isProcessing = false;
        this.sidebarExpanded = false;
        this.currentLanguage = 'zh'; // 'zh' for Chinese, 'en' for English
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
            this.resetUI();
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

        document.getElementById('userGuideLinkFooter').addEventListener('click', (e) => {
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

        // Sidebar toggle
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Language toggle
        document.getElementById('langToggle').addEventListener('click', () => {
            this.toggleLanguage();
        });

        // Sidebar toggle
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            this.toggleSidebar();
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

    resetUI() {
        // Reset processing state
        this.isProcessing = false;
        
        // Reset file input and UI
        this.removeFile();
        
        // Reset loading state
        this.hideLoading();
        
        // Reset process button
        this.updateProcessButton();
        
        // Reset any form toggles to default state
        document.getElementById('academicToggle').checked = false;
        this.toggleAcademicOptions(false);
        document.getElementById('customToggle').checked = false;
        this.toggleCustomOptions(false);
        
        // Reset status to initial state
        this.updateStatus('等待文件上传', 'success');
    }

    updateProcessButton() {
        const processBtn = document.getElementById('processBtn');
        processBtn.disabled = !this.currentFile || this.isProcessing;
    }

    async processFile() {
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

        try {
            // Use fetch with ReadableStream for Server-Sent Events
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`服务器错误: ${response.status} ${response.statusText}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.substring(6)); // Remove 'data: ' prefix
                        
                        if (data.error) {
                            throw new Error(data.error);
                        }
                        
                        if (data.status) {
                            this.updateStatus(data.status, 'warning');
                        }
                        
                        if (data.success) {
                            this.showSuccess(data.download_url);
                            this.updateStatus('处理完成！', 'success');
                            // Don't reset UI completely here - keep results visible
                            this.isProcessing = false;
                            this.hideLoading();
                            this.updateProcessButton();
                            return;
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Processing error:', error);
            this.showError('处理错误: ' + error.message);
            this.updateStatus('处理失败', 'error');
            this.isProcessing = false;
            this.hideLoading();
            this.updateProcessButton();
        }
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

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const main = document.querySelector('.app-main');
        
        // Toggle expanded state
        this.sidebarExpanded = !sidebar.classList.contains('sidebar-expanded');
        
        if (this.sidebarExpanded) {
            sidebar.classList.add('sidebar-expanded');
            main.classList.add('sidebar-expanded');
        } else {
            sidebar.classList.remove('sidebar-expanded');
            main.classList.remove('sidebar-expanded');
        }
    }

    toggleLanguage() {
        this.currentLanguage = this.currentLanguage === 'zh' ? 'en' : 'zh';
        this.updateLanguageUI();
        
        // Update the language toggle button text
        const langToggle = document.getElementById('langToggle');
        const langText = langToggle.querySelector('span');
        langText.textContent = this.currentLanguage === 'zh' ? 'EN' : '中文';
    }

    updateLanguageUI() {
        // Define translations for all UI elements
        const translations = {
            zh: {
                // Header
                'appTitle': 'AcademicPlot Pro',
                'appSubtitle': 'AI驱动的学术图表翻译与美化专家',
                'langToggle': 'EN',
                
                // Upload card
                'uploadTitle': '上传Python图表文件',
                'uploadDragDrop': '拖放文件到此处',
                'uploadClick': '或点击选择Python文件 (.py)',
                'uploadFileTypes': '支持 .py 格式文件',
                
                // Action card
                'actionTitle': '开始处理',
                'processButton': '开始AI处理',
                'processingText': '处理中...',
                'waitingStatus': '等待文件上传',
                
                // Results card
                'resultsTitle': '处理结果',
                'resultsPlaceholder': '处理完成后将显示结果',
                'resultsSuccess': '处理成功！',
                'resultsDownload': '文件已处理完成，可以下载结果',
                'downloadButton': '下载处理结果',
                
                // Sidebar
                'sidebarTitle': '设置',
                'basicSettings': '基本设置',
                'beautifyLabel': 'AI布局美化',
                'beautifyDesc': '智能优化图表布局和排列',
                
                'academicSettings': '学术风格设置',
                'academicLabel': '启用学术论文风格',
                'academicDesc': '应用学术期刊出版标准样式',
                
                'customSettings': '自定义设置',
                'customLabel': '启用自定义参数',
                'customDesc': '手动调整详细参数设置',
                
                // Academic options
                'paperFormat': '论文格式',
                'layout': '图表布局',
                'vectorFormat': '导出格式',
                'dpi': '分辨率 (DPI)',
                'noSave': '不保存',
                'singleColumn': '单栏',
                'doubleColumn': '双栏',
                
                // Custom options
                'fontSize': '字体大小',
                'titleSize': '标题大小',
                'figWidth': '图表宽度',
                'figHeight': '图表高度',
                'customDpi': '自定义DPI',
                
                // Footer
                'copyright': '© 2024 AcademicPlot Pro. 由 DeepSeek AI 提供技术支持',
                'userGuide': '使用指南',
                'feedback': '反馈问题',
                'about': '关于我们',
                
                // User Guide Modal
                'modalTitle': '使用指南',
                'step1Title': '步骤 1: 上传文件',
                'step1Desc': '将您的Python绘图脚本文件 (.py) 拖放到上传区域，或点击选择文件。',
                'step2Title': '步骤 2: 配置设置',
                'step2Desc': '打开左侧的设置面板（基本设置、学术风格、自定义）来定制美化选项。',
                'step3Title': '步骤 3: 开始处理',
                'step3Desc': '点击"开始AI处理"按钮开始处理您的文件。',
                'step4Title': '步骤 4: 下载结果',
                'step4Desc': '处理完成后，处理结果区域将显示下载链接。'
            },
            en: {
                // Header
                'appTitle': 'AcademicPlot Pro',
                'appSubtitle': 'AI-powered Academic Chart Translation & Beautification Expert',
                'langToggle': '中文',
                
                // Upload card
                'uploadTitle': 'Upload Python Chart File',
                'uploadDragDrop': 'Drag and drop file here',
                'uploadClick': 'or click to select Python file (.py)',
                'uploadFileTypes': 'Supports .py format files',
                
                // Action card
                'actionTitle': 'Start Processing',
                'processButton': 'Start AI Processing',
                'processingText': 'Processing...',
                'waitingStatus': 'Waiting for file upload',
                
                // Results card
                'resultsTitle': 'Processing Results',
                'resultsPlaceholder': 'Results will be displayed after processing',
                'resultsSuccess': 'Processing Successful!',
                'resultsDownload': 'File processed successfully, ready for download',
                'downloadButton': 'Download Result',
                
                // Sidebar
                'sidebarTitle': 'Settings',
                'basicSettings': 'Basic Settings',
                'beautifyLabel': 'AI Layout Beautification',
                'beautifyDesc': 'Intelligent chart layout optimization',
                
                'academicSettings': 'Academic Style Settings',
                'academicLabel': 'Enable Academic Paper Style',
                'academicDesc': 'Apply academic journal publishing standards',
                
                'customSettings': 'Custom Settings',
                'customLabel': 'Enable Custom Parameters',
                'customDesc': 'Manual detailed parameter adjustment',
                
                // Academic options
                'paperFormat': 'Paper Format',
                'layout': 'Chart Layout',
                'vectorFormat': 'Export Format',
                'dpi': 'Resolution (DPI)',
                'noSave': 'Don\'t save',
                'singleColumn': 'Single Column',
                'doubleColumn': 'Double Column',
                
                // Custom options
                'fontSize': 'Font Size',
                'titleSize': 'Title Size',
                'figWidth': 'Chart Width',
                'figHeight': 'Chart Height',
                'customDpi': 'Custom DPI',
                
                // Footer
                'copyright': '© 2024 AcademicPlot Pro. Powered by DeepSeek AI',
                'userGuide': 'User Guide',
                'feedback': 'Feedback',
                'about': 'About Us',
                
                // User Guide Modal
                'modalTitle': 'User Guide',
                'step1Title': 'Step 1: Upload File',
                'step1Desc': 'Drag and drop your Python plotting script file (.py) to the upload area, or click to select a file.',
                'step2Title': 'Step 2: Configure Settings',
                'step2Desc': 'Open the settings panel on the left (Basic, Academic Style, Custom) to customize beautification options.',
                'step3Title': 'Step 3: Start Processing',
                'step3Desc': 'Click the "Start AI Processing" button to begin processing your file.',
                'step4Title': 'Step 4: Download Results',
                'step4Desc': 'After processing is complete, the results area will display download links.'
            }
        };

        const lang = translations[this.currentLanguage];
        
        // Update all text elements
        document.querySelector('.logo-text h1').textContent = lang.appTitle;
        document.querySelector('.subtitle').textContent = lang.appSubtitle;
        
        // Upload card
        document.querySelector('.upload-card h2').textContent = lang.uploadTitle;
        document.querySelector('.drop-content h3').textContent = lang.uploadDragDrop;
        document.querySelector('.drop-content p').textContent = lang.uploadClick;
        document.querySelector('.file-types').textContent = lang.uploadFileTypes;
        
        // Action card
        document.querySelector('.action-card h2').textContent = lang.actionTitle;
        document.querySelector('.btn-text').textContent = lang.processButton;
        document.querySelector('.btn-loading').textContent = lang.processingText;
        document.querySelector('.status-item span').textContent = lang.waitingStatus;
        
        // Results card
        document.querySelector('.results-card h2').textContent = lang.resultsTitle;
        document.querySelector('.results-placeholder p').textContent = lang.resultsPlaceholder;
        document.querySelector('.results-success h3').textContent = lang.resultsSuccess;
        document.querySelector('.results-success p').textContent = lang.resultsDownload;
        document.querySelector('.btn-download-result').textContent = lang.downloadButton;
        
        // Sidebar
        document.querySelector('.sidebar-header h3').textContent = lang.sidebarTitle;
        
        // Basic settings
        document.querySelector('[data-target="basicSettings"] h3').textContent = lang.basicSettings;
        document.querySelector('#basicSettings .label-text').textContent = lang.beautifyLabel;
        document.querySelector('#basicSettings .setting-description').textContent = lang.beautifyDesc;
        
        // Academic settings
        document.querySelector('[data-target="academicSettings"] h3').textContent = lang.academicSettings;
        document.querySelector('#academicSettings .label-text').textContent = lang.academicLabel;
        document.querySelector('#academicSettings .setting-description').textContent = lang.academicDesc;
        
        // Custom settings
        document.querySelector('[data-target="customSettings"] h3').textContent = lang.customSettings;
        document.querySelector('#customSettings .label-text').textContent = lang.customLabel;
        document.querySelector('#customSettings .setting-description').textContent = lang.customDesc;
        
        // Academic options labels
        document.querySelector('#academicOptions label[for="paperFormat"]').textContent = lang.paperFormat;
        document.querySelector('#academicOptions label[for="layout"]').textContent = lang.layout;
        document.querySelector('#academicOptions label[for="vectorFormat"]').textContent = lang.vectorFormat;
        document.querySelector('#academicOptions label[for="dpi"]').textContent = lang.dpi;
        
        // Update select options
        document.querySelector('#vectorFormat option[value=""]').textContent = lang.noSave;
        document.querySelector('#layout option[value="single"]').textContent = lang.singleColumn;
        document.querySelector('#layout option[value="double"]').textContent = lang.doubleColumn;
        
        // Custom options labels
        document.querySelector('#customOptions label[for="fontSize"]').textContent = lang.fontSize;
        document.querySelector('#customOptions label[for="titleSize"]').textContent = lang.titleSize;
        document.querySelector('#customOptions label[for="figWidth"]').textContent = lang.figWidth;
        document.querySelector('#customOptions label[for="figHeight"]').textContent = lang.figHeight;
        document.querySelector('#customOptions label[for="customDpi"]').textContent = lang.customDpi;
        
        // Footer
        document.querySelector('.footer-content p').textContent = lang.copyright;
        document.querySelectorAll('.footer-link')[0].textContent = lang.userGuide;
        document.querySelectorAll('.footer-link')[1].textContent = lang.feedback;
        document.querySelectorAll('.footer-link')[2].textContent = lang.about;

        // User Guide Modal
        document.querySelector('#userGuideModal .modal-header h2').textContent = lang.modalTitle;
        document.querySelector('#userGuideModal .guide-step:nth-child(1) h3').textContent = lang.step1Title;
        document.querySelector('#userGuideModal .guide-step:nth-child(1) p').textContent = lang.step1Desc;
        document.querySelector('#userGuideModal .guide-step:nth-child(2) h3').textContent = lang.step2Title;
        document.querySelector('#userGuideModal .guide-step:nth-child(2) p').textContent = lang.step2Desc;
        document.querySelector('#userGuideModal .guide-step:nth-child(3) h3').textContent = lang.step3Title;
        document.querySelector('#userGuideModal .guide-step:nth-child(3) p').textContent = lang.step3Desc;
        document.querySelector('#userGuideModal .guide-step:nth-child(4) h3').textContent = lang.step4Title;
        document.querySelector('#userGuideModal .guide-step:nth-child(4) p').textContent = lang.step4Desc;
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