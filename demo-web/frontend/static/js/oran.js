/**
 * ORAN-specific UI functionality
 * Handles spec upload, catalog display, and test execution for O-RAN A1
 */

// ORAN State
const oranState = {
    uploadedSpecs: {
        'TS_103_989': null,
        'TS_103_987': null,
        'TS_103_988': null,
        'TS_103_983': null
    },
    catalogs: [],
    currentCatalog: null
};

// Initialize ORAN UI
export function initOranUI() {
    console.log('Initializing ORAN UI...');
    
    // Setup file input handlers
    setupFileUploads();
    
    // Setup generation button
    document.getElementById('generate-catalog-btn')?.addEventListener('click', handleGenerateCatalog);
    
    // Setup refresh catalogs button
    document.getElementById('refresh-catalogs-btn')?.addEventListener('click', loadCatalogs);
    
    // Setup script modal close
    document.querySelector('#script-modal .modal-close')?.addEventListener('click', () => {
        document.getElementById('script-modal').style.display = 'none';
    });
    
    // Setup download and copy buttons
    document.getElementById('download-script-btn')?.addEventListener('click', handleDownloadScript);
    document.getElementById('copy-script-btn')?.addEventListener('click', handleCopyScript);
    
    // Load existing catalogs
    loadCatalogs();
}

// Setup file upload handlers
function setupFileUploads() {
    const specIds = ['spec-ts-103-989', 'spec-ts-103-987', 'spec-ts-103-988', 'spec-ts-103-983'];
    const specTypes = ['TS_103_989', 'TS_103_987', 'TS_103_988', 'TS_103_983'];
    
    specIds.forEach((specId, index) => {
        const input = document.getElementById(specId);
        const label = input?.nextElementSibling;
        const fileName = label?.querySelector('.file-name');
        const status = input?.parentElement.querySelector('.file-status');
        
        if (input) {
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    fileName.textContent = file.name;
                    status.textContent = `✓ ${(file.size / 1024 / 1024).toFixed(2)} MB`;
                    status.className = 'file-status success';
                    
                    oranState.uploadedSpecs[specTypes[index]] = file;
                    checkUploadComplete();
                } else {
                    fileName.textContent = 'No file selected';
                    status.textContent = '';
                    oranState.uploadedSpecs[specTypes[index]] = null;
                }
            });
        }
    });
}

// Check if all specs are uploaded
function checkUploadComplete() {
    const allUploaded = Object.values(oranState.uploadedSpecs).every(spec => spec !== null);
    const generateBtn = document.getElementById('generate-catalog-btn');
    
    if (generateBtn) {
        generateBtn.disabled = !allUploaded;
        if (allUploaded) {
            generateBtn.textContent = 'Generate Test Catalog (4 specs ready)';
        }
    }
}

// Handle catalog generation
async function handleGenerateCatalog() {
    const catalogName = document.getElementById('catalog-name')?.value || 'Untitled Catalog';
    const catalogDesc = document.getElementById('catalog-description')?.value || '';
    
    // Show progress
    const progressDiv = document.getElementById('upload-progress');
    const statusDiv = document.getElementById('generation-status');
    const statusLog = document.getElementById('generation-log');
    
    if (progressDiv) progressDiv.style.display = 'block';
    if (statusDiv) statusDiv.style.display = 'block';
    if (statusLog) statusLog.innerHTML = '<p>Uploading specifications...</p>';
    
    try {
        // Upload specs first
        const formData = new FormData();
        Object.entries(oranState.uploadedSpecs).forEach(([key, file]) => {
            if (file) {
                formData.append(key.toLowerCase(), file);
            }
        });
        
        const uploadResponse = await fetch('/api/oran/upload-specs', {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            throw new Error('Failed to upload specifications');
        }
        
        if (statusLog) statusLog.innerHTML += '<p>✓ Specifications uploaded</p>';
        
        // Generate catalog
        if (statusLog) statusLog.innerHTML += '<p>Generating test catalog...</p>';
        
        const generateResponse = await fetch(`/api/oran/generate?catalog_name=${encodeURIComponent(catalogName)}&description=${encodeURIComponent(catalogDesc)}`, {
            method: 'POST'
        });
        
        if (!generateResponse.ok) {
            throw new Error('Failed to generate catalog');
        }
        
        const result = await generateResponse.json();
        
        if (statusLog) {
            statusLog.innerHTML += `<p>✓ Test catalog generated: ${result.catalog_id}</p>`;
            statusLog.innerHTML += '<p class="success">Generation complete! Switch to Test Catalog tab to view.</p>';
        }
        
        // Switch to catalog tab after delay
        setTimeout(() => {
            document.querySelector('[data-tab="oran-catalog"]')?.click();
            loadCatalogs();
        }, 2000);
        
    } catch (error) {
        console.error('Error generating catalog:', error);
        if (statusLog) {
            statusLog.innerHTML += `<p class="error">✗ Error: ${error.message}</p>`;
        }
        alert('Failed to generate test catalog. See console for details.');
    } finally {
        if (progressDiv) progressDiv.style.display = 'none';
    }
}

// Load catalogs from backend
async function loadCatalogs() {
    try {
        const response = await fetch('/api/oran/catalogs');
        if (!response.ok) {
            throw new Error('Failed to load catalogs');
        }
        
        const catalogs = await response.json();
        oranState.catalogs = catalogs;
        
        displayCatalogs(catalogs);
    } catch (error) {
        console.error('Error loading catalogs:', error);
        const catalogsList = document.getElementById('catalogs-list');
        if (catalogsList) {
            catalogsList.innerHTML = '<p class="error">Failed to load catalogs. Make sure the backend is running.</p>';
        }
    }
}

// Display catalogs in UI
function displayCatalogs(catalogs) {
    const catalogsList = document.getElementById('catalogs-list');
    if (!catalogsList) return;
    
    if (catalogs.length === 0) {
        catalogsList.innerHTML = '<p class="placeholder">No test catalogs generated yet. Upload specifications to generate your first catalog.</p>';
        return;
    }
    
    catalogsList.innerHTML = catalogs.map(catalog => `
        <div class="catalog-card" data-catalog-id="${catalog.catalog_id}">
            <div class="catalog-header">
                <h3>${catalog.name}</h3>
                <span class="catalog-badge">${catalog.total_tests} tests</span>
            </div>
            <p class="catalog-description">${catalog.description || 'No description'}</p>
            <div class="catalog-meta">
                <span>Generated: ${new Date(catalog.generated_at).toLocaleString()}</span>
            </div>
            <div class="catalog-actions">
                <button class="btn-primary btn-sm view-catalog-btn" data-catalog-id="${catalog.catalog_id}">View Tests</button>
                <button class="btn-secondary btn-sm" onclick="window.open('/api/oran/catalogs/${catalog.catalog_id}', '_blank')">Export JSON</button>
            </div>
        </div>
    `).join('');
    
    // Add event listeners to view buttons
    document.querySelectorAll('.view-catalog-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const catalogId = e.target.dataset.catalogId;
            viewCatalogTests(catalogId);
        });
    });
}

// View catalog tests
async function viewCatalogTests(catalogId) {
    try {
        const response = await fetch(`/api/oran/catalogs/${catalogId}`);
        if (!response.ok) {
            throw new Error('Failed to load catalog details');
        }
        
        const catalog = await response.json();
        oranState.currentCatalog = catalog;
        
        displayCatalogDetails(catalog);
    } catch (error) {
        console.error('Error loading catalog details:', error);
        alert('Failed to load catalog details.');
    }
}

// Display catalog details with test cases
function displayCatalogDetails(catalog) {
    const detailsDiv = document.getElementById('catalog-details');
    if (!detailsDiv) return;
    
    document.getElementById('catalog-title').textContent = catalog.name;
    document.getElementById('catalog-generated').textContent = new Date(catalog.generated_at).toLocaleString();
    document.getElementById('catalog-total-tests').textContent = catalog.total_tests;
    document.getElementById('catalog-sources').textContent = Object.keys(catalog.spec_sources || {}).join(', ');
    
    // Display test cases table
    const tbody = document.getElementById('test-cases-tbody');
    if (tbody) {
        tbody.innerHTML = (catalog.test_cases || []).map(testCase => `
            <tr>
                <td><code>${testCase.test_id}</code></td>
                <td>${testCase.scenario}</td>
                <td><span class="method-badge method-${testCase.method.toLowerCase()}">${testCase.method}</span></td>
                <td><code>${testCase.endpoint}</code></td>
                <td><span class="status-badge status-${testCase.expected_status}">${testCase.expected_status}</span></td>
                <td><span class="complexity-badge complexity-${testCase.complexity.toLowerCase()}">${testCase.complexity}</span></td>
                <td>
                    <button class="btn-sm btn-secondary view-script-btn" data-test-id="${testCase.test_id}">View Script</button>
                    <button class="btn-sm btn-primary run-test-btn" data-test-id="${testCase.test_id}" data-catalog-id="${catalog.catalog_id}">Run</button>
                </td>
            </tr>
        `).join('');
        
        // Add event listeners
        tbody.querySelectorAll('.view-script-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const testId = e.target.dataset.testId;
                viewTestScript(testId);
            });
        });
        
        tbody.querySelectorAll('.run-test-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const testId = e.target.dataset.testId;
                const catalogId = e.target.dataset.catalogId;
                runOranTest(testId, catalogId);
            });
        });
    }
    
    // Setup close button
    document.getElementById('close-catalog-btn')?.addEventListener('click', () => {
        detailsDiv.style.display = 'none';
    });
    
    detailsDiv.style.display = 'block';
}

// View test script with syntax highlighting
async function viewTestScript(testId) {
    try {
        const response = await fetch(`/api/oran/scripts/${testId}`);
        if (!response.ok) {
            throw new Error('Failed to load test script');
        }
        
        const scriptData = await response.json();
        
        // Display in modal
        const modal = document.getElementById('script-modal');
        document.getElementById('script-test-id').textContent = scriptData.test_id;
        const codeElement = document.getElementById('script-content');
        codeElement.textContent = scriptData.content;
        
        // Apply syntax highlighting
        if (window.Prism) {
            Prism.highlightElement(codeElement);
        }
        
        // Store current test ID for download
        modal.dataset.testId = testId;
        modal.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading test script:', error);
        alert('Failed to load test script. Script may not be generated yet.');
    }
}

// Handle script download
async function handleDownloadScript() {
    const modal = document.getElementById('script-modal');
    const testId = modal.dataset.testId;
    if (!testId) return;
    
    window.open(`/api/oran/scripts/${testId}/download`, '_blank');
}

// Handle copy to clipboard
function handleCopyScript() {
    const codeElement = document.getElementById('script-content');
    const text = codeElement.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copy-script-btn');
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

// Run ORAN test
async function runOranTest(testId, catalogId) {
    try {
        const response = await fetch(`/api/oran/execute?test_id=${testId}&catalog_id=${catalogId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to start test execution');
        }
        
        const result = await response.json();
        console.log('Test execution started:', result);
        
        // Switch to execution tab
        document.querySelector('[data-tab="execution"]')?.click();
        
        alert(`Test execution started!\nExecution ID: ${result.execution_id}\n\nSwitch to Execution tab to view progress.`);
        
    } catch (error) {
        console.error('Error running test:', error);
        alert('Failed to start test execution.');
    }
}

// Export functions for use in main app
export const oran = {
    init: initOranUI,
    loadCatalogs,
    viewTestScript,
    runTest: runOranTest
};
