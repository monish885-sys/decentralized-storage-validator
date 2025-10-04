// Decentralized Storage Validator - Frontend JavaScript

// Global state
const state = {
    files: [],
    stats: null,
    currentSection: 'dashboard'
};

// DOM Elements
const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('.nav-link');
const fileInput = document.getElementById('file-input');
const uploadDropzone = document.getElementById('upload-dropzone');
const loadingOverlay = document.getElementById('loading-overlay');
const notificationContainer = document.getElementById('notification-container');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    showLoading();
    Promise.all([
        loadStats(),
        loadFiles()
    ]).finally(() => {
        hideLoading();
    });
}

function setupEventListeners() {
    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            showSection(sectionId);
        });
    });

    // File upload
    if (uploadDropzone) {
        uploadDropzone.addEventListener('click', () => fileInput.click());
        
        uploadDropzone.addEventListener('dragover', handleDragOver);
        uploadDropzone.addEventListener('dragleave', handleDragLeave);
        uploadDropzone.addEventListener('drop', handleDrop);
        
        fileInput.addEventListener('change', handleFileSelect);
    }

    // Search
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchFiles();
            }
        });
    }
}

// Section management
function showSection(sectionId) {
    // Hide all sections
    sections.forEach(section => section.classList.remove('active'));
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update navigation
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        }
    });

    state.currentSection = sectionId;

    // Load section-specific data
    switch(sectionId) {
        case 'dashboard':
            refreshFiles();
            break;
        case 'verify':
            refreshVerification();
            break;
    }
}

// API Functions
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Stats management
async function loadStats() {
    try {
        const response = await apiRequest('/api/stats');
        state.stats = response.data;
        updateStatsDisplay();
    } catch (error) {
        showNotification('Failed to load statistics: ' + error.message, 'error');
    }
}

function updateStatsDisplay() {
    if (!state.stats) return;

    document.getElementById('total-files').textContent = state.stats.active_files || 0;
    document.getElementById('verified-files').textContent = state.stats.active_files || 0;
    document.getElementById('tampered-files').textContent = state.stats.deleted_files || 0;
    
    const storageSize = state.stats.total_storage_bytes || 0;
    document.getElementById('total-storage').textContent = formatBytes(storageSize);
}

// Files management
async function loadFiles() {
    try {
        const response = await apiRequest('/api/files');
        state.files = response.files || [];
        updateFilesTable();
    } catch (error) {
        showNotification('Failed to load files: ' + error.message, 'error');
    }
}

function updateFilesTable() {
    const tableBody = document.getElementById('files-table-body');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    if (state.files.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center" style="padding: 2rem; color: var(--gray-color);">
                    <i class="fas fa-folder-open"></i><br>
                    No files uploaded yet
                </td>
            </tr>
        `;
        return;
    }

    state.files.slice(0, 5).forEach(file => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas fa-file"></i>
                    <span>${escapeHtml(file.file_name)}</span>
                </div>
            </td>
            <td>${formatBytes(file.file_size)}</td>
            <td>
                <code style="background: var(--light-color); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem;">
                    ${escapeHtml(file.hash.substring(0, 16))}...
                </code>
            </td>
            <td>
                <span class="status-badge verified">
                    <i class="fas fa-check-circle"></i> Verified
                </span>
            </td>
            <td>${formatDate(file.upload_date)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="verifyFile('${file.file_name}')">
                    <i class="fas fa-shield-check"></i>
                </button>
                <button class="btn btn-sm btn-error" onclick="deleteFile('${file.file_name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// File upload functionality
function handleDragOver(e) {
    e.preventDefault();
    uploadDropzone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadDropzone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadDropzone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

async function uploadFile(file) {
    if (file.size > 16 * 1024 * 1024) { // 16MB limit
        showNotification('File size exceeds 16MB limit', 'error');
        return;
    }

    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        showUploadProgress(0, 'Uploading file...');
        
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                showUploadProgress(percentComplete, 'Uploading to Google Drive...');
            }
        });

        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                showUploadResult(true, response.data);
                refreshFiles();
                loadStats();
                
                // Reset file input
                if (fileInput) fileInput.value = '';
            } else {
                const error = JSON.parse(xhr.responseText);
                throw new Error(error.error || 'Upload failed');
            }
        });

        xhr.addEventListener('error', function() {
            throw new Error('Upload failed');
        });

        xhr.open('POST', '/api/upload');
        xhr.send(formData);

    } catch (error) {
        hideLoading();
        showNotification('Upload failed: ' + error.message, 'error');
        hideUploadProgress();
    }
}

function showUploadProgress(percentage, text) {
    const progressDiv = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (progressDiv && progressFill && progressText) {
        progressDiv.style.display = 'block';
        progressFill.style.width = percentage + '%';
        progressText.textContent = text;
    }
}

function hideUploadProgress() {
    const progressDiv = document.getElementById('upload-progress');
    if (progressDiv) {
        progressDiv.style.display = 'none';
    }
}

function showUploadResult(success, data) {
    hideLoading();
    hideUploadProgress();
    
    const resultDiv = document.getElementById('upload-result');
    const detailsP = document.getElementById('upload-details');
    
    if (resultDiv && detailsP && success) {
        detailsP.innerHTML = `
            <strong>${escapeHtml(data.filename)}</strong><br>
            Size: ${formatBytes(data.size)}<br>
            Hash: <code>${escapeHtml(data.hash.substring(0, 32))}...</code>
        `;
        resultDiv.style.display = 'block';
        
        // Reset after 3 seconds
        setTimeout(() => {
            resultDiv.style.display = 'none';
        }, 3000);
    }
}

// Verification functionality
async function verifyFile(filename) {
    showLoading();
    try {
        const response = await apiRequest(`/api/verify/${filename}`);
        const data = response.data;
        
        const message = data.is_intact 
            ? `✅ ${filename} is intact (Trust Score: ${data.trust_score}%)`
            : `❌ ${filename} has been tampered with! Security Alert!`;
        
        const type = data.is_intact ? 'success' : 'error';
        showNotification(message, type);
        
        refreshFiles();
        refreshVerification();
    } catch (error) {
        showNotification('Verification failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function verifyAllFiles() {
    showLoading();
    try {
        const response = await apiRequest('/api/verify-all', {
            method: 'POST'
        });
        
        const data = response.data;
        
        // Update summary
        document.getElementById('verified-count').textContent = data.verified_count;
        document.getElementById('tampered-count').textContent = data.tampered_count;
        document.getElementById('security-percentage').textContent = data.security_percentage + '%';
        
        // Show summary
        document.getElementById('verification-summary').style.display = 'block';
        
        // Update details
        updateVerificationDetails(data.results);
        
        // Show notification
        const message = data.tampered_count > 0 
            ? `⚠️ Verification complete: ${data.tampered_count} tampered files found!`
            : `✅ All ${data.verified_count} files verified successfully!`;
        
        const type = data.tampered_count > 0 ? 'warning' : 'success';
        showNotification(message, type);
        
        refreshFiles();
        
    } catch (error) {
        showNotification('Batch verification failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function updateVerificationDetails(results) {
    const detailsDiv = document.getElementById('verification-details');
    if (!detailsDiv) return;

    detailsDiv.innerHTML = '<h3>Detailed Results:</h3>';

    results.forEach(result => {
        const resultDiv = document.createElement('div');
        resultDiv.className = `verification-item ${result.is_intact ? 'success' : 'error'}`;
        
        resultDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; background: ${result.is_intact ? 'rgba(81, 207, 102, 0.1)' : 'rgba(255, 107, 107, 0.1)'};">
                <span><i class="fas ${result.is_intact ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i> ${escapeHtml(result.filename)}</span>
                <span class="status-badge ${result.is_intact ? 'verified' : 'tampered'}">
                    ${result.trust_score}%
                </span>
            </div>
        `;
        
        detailsDiv.appendChild(resultDiv);
    });
}

function refreshVerification() {
    if (state.currentSection === 'verify') {
        // Show latest verification data if available
        document.getElementById('verification-summary').style.display = 'block';
    }
}

// Delete functionality
async function deleteFile(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"? This action cannot be undone.`)) {
        return;
    }

    showLoading();
    try {
        await apiRequest(`/api/delete/${filename}`, {
            method: 'DELETE'
        });
        
        showNotification(`✅ ${filename} deleted successfully`, 'success');
        refreshFiles();
        loadStats();
    } catch (error) {
        showNotification('Delete failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Search functionality
async function searchFiles() {
    const query = document.getElementById('search-input').value.trim();
    
    if (!query) {
        showNotification('Please enter a search term', 'warning');
        return;
    }

    showLoading();
    try {
        const response = await apiRequest(`/api/search?q=${encodeURIComponent(query)}`);
        displaySearchResults(response.data);
    } catch (error) {
        showNotification('Search failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displaySearchResults(data) {
    const resultsDiv = document.getElementById('search-results');
    if (!resultsDiv) return;

    if (data.count === 0) {
        resultsDiv.innerHTML = `
            <div class="text-center" style="padding: 2rem; color: var(--gray-color);">
                <i class="fas fa-search"></i><br><br>
                No files found matching "${escapeHtml(data.query)}"
            </div>
        `;
        return;
    }

    resultsDiv.innerHTML = `
        <h3>Search Results for "${escapeHtml(data.query)}" (${data.count} found)</h3>
        <div class="search-results-list">
            ${data.results.map(file => `
                <div class="search-result-item" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; background: white; box-shadow: var(--shadow);">
                    <div>
                        <strong><i class="fas fa-file"></i> ${escapeHtml(file.file_name)}</strong><br>
                        <small style="color: var(--gray-color);">
                            Hash: <code>${escapeHtml(file.hash.substring(0, 16))}...</code> | 
                            Size: ${formatBytes(file.file_size)} | 
                            Uploaded: ${formatDate(file.upload_date)}
                        </small>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-sm btn-primary" onclick="verifyFile('${file.file_name}')">
                            <i class="fas fa-shield-check"></i>
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Utility functions
function refreshFiles() {
    if (state.currentSection === 'dashboard' || state.currentSection === 'verify') {
        loadFiles();
    }
}

function showLoading() {
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="fas ${getIconForType(type)}"></i>
            <span>${message}</span>
        </div>
    `;

    if (notificationContainer) {
        notificationContainer.appendChild(notification);

        // Auto remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);
    }
}

function getIconForType(type) {
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-times-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions for global access
window.showSection = showSection;
window.verifyFile = verifyFile;
window.verifyAllFiles = verifyAllFiles;
window.deleteFile = deleteFile;
window.searchFiles = searchFiles;
window.refreshFiles = refreshFiles;
window.refreshVerification = refreshVerification;
