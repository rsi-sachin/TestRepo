/**
 * ORAN-specific UI functionality
 * Handles spec upload, catalog display, and test execution for O-RAN A1
 *
 * Upload-tab flow (selector-first):
 *  1. User picks Protocol/Interface (default A1).
 *  2. User checks which TS documents to include (multi-select checkboxes).
 *  3. Backend /resolve-specs is queried for each selected spec:
 *       - status "auto"    -> file found in repo docs folder, auto-bound silently.
 *       - status "missing" -> user must choose file via hidden <input type=file>.
 *  4. Generate / Preview buttons enable only when all selected specs are resolved.
 */

const SPEC_META = {
    TS_103_989: { tsNumber: 'TS 103 989', title: 'A1 Test Specification' },
    TS_103_987: { tsNumber: 'TS 103 987', title: 'A1 Application Protocol' },
    TS_103_988: { tsNumber: 'TS 103 988', title: 'A1 Type Definitions' },
    TS_103_983: { tsNumber: 'TS 103 983', title: 'A1 General Principles' }
};

const INPUT_ID = {
    TS_103_989: 'spec-ts-103-989',
    TS_103_987: 'spec-ts-103-987',
    TS_103_988: 'spec-ts-103-988',
    TS_103_983: 'spec-ts-103-983'
};

const specStates = {};
function resetSpecState(specType) {
    specStates[specType] = { status: 'pending', file: null, filename: null };
}

const oranState = {
    selectedSpecs: ['TS_103_989', 'TS_103_987', 'TS_103_988', 'TS_103_983'],
    selectedService: 'A1-P',
    serviceDefinitions: [],
    catalogs: [],
    currentCatalog: null,
    methodologyAnalysis: null,
    useRules: true,
    availableRulePacks: [],
    selectedRulePack: null,
    currentHierarchy: null,
    extractionResults: null
};

export function initOranUI() {
    console.log('Initializing ORAN UI...');

    Object.keys(SPEC_META).forEach(resetSpecState);

    document.getElementById('protocol-select')
        ?.addEventListener('change', handleProtocolChange);

    document.getElementById('service-select')
        ?.addEventListener('change', handleServiceChange);

    document.querySelectorAll('.spec-checkbox').forEach(cb => {
        cb.addEventListener('change', handleSpecCheckboxChange);
    });

    Object.entries(INPUT_ID).forEach(([specType, inputId]) => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('change', e => handleManualFileSelect(e, specType));
        }
    });

    document.getElementById('generate-catalog-btn')
        ?.addEventListener('click', handleGenerateCatalog);

    document.getElementById('analyze-methodology-btn')
        ?.addEventListener('click', handleAnalyzeMethodology);

    document.getElementById('methodology-spec-select')
        ?.addEventListener('change', handleMethodologySpecChange);

    document.getElementById('preview-sections-btn')
        ?.addEventListener('click', () => {
            document.dispatchEvent(new CustomEvent('oran:previewSections'));
        });

    document.getElementById('refresh-catalogs-btn')
        ?.addEventListener('click', loadCatalogs);

    document.querySelector('#script-modal .modal-close')
        ?.addEventListener('click', () => {
            document.getElementById('script-modal').style.display = 'none';
        });

    document.getElementById('download-script-btn')?.addEventListener('click', handleDownloadScript);
    document.getElementById('copy-script-btn')?.addEventListener('click', handleCopyScript);

    // Rule-based extraction listeners
    document.getElementById('use-rules-toggle')
        ?.addEventListener('change', handleUseRulesToggle);
    
    document.getElementById('view-hierarchy-btn')
        ?.addEventListener('click', handleViewHierarchy);
    
    document.getElementById('manage-rules-btn')
        ?.addEventListener('click', handleManageRules);
    
    document.getElementById('learn-from-doc-btn')
        ?.addEventListener('click', handleLearnFromDocument);
    
    document.getElementById('refresh-rule-packs-btn')
        ?.addEventListener('click', loadRulePacks);
    
    document.getElementById('export-hierarchy-btn')
        ?.addEventListener('click', handleExportHierarchy);
    
    document.getElementById('apply-rule-pack-btn')
        ?.addEventListener('click', handleApplyRulePack);
    
    document.getElementById('delete-rule-pack-btn')
        ?.addEventListener('click', handleDeleteRulePack);

    refreshResolution();
    loadServiceDefinitions();
    loadCatalogs();
    loadRulePacks();
}

function handleProtocolChange() {
    refreshResolution();
}

function handleServiceChange(e) {
    oranState.selectedService = e.target.value || 'A1-P';
    updateServiceSummary();
    syncCatalogNamePlaceholder();
}

function handleSpecCheckboxChange(e) {
    const specType = e.target.value;

    if (e.target.checked) {
        if (!oranState.selectedSpecs.includes(specType)) {
            oranState.selectedSpecs.push(specType);
        }
        resetSpecState(specType);
    } else {
        oranState.selectedSpecs = oranState.selectedSpecs.filter(s => s !== specType);
        delete specStates[specType];
    }

    refreshResolution();
}

function handleManualFileSelect(event, specType) {
    const file = event.target.files[0];
    if (!file) return;

    specStates[specType] = {
        status: 'manual',
        file,
        filename: file.name
    };

    renderResolutionList();
    updateActionButtons();
}

function triggerFilePicker(specType) {
    const input = document.getElementById(INPUT_ID[specType]);
    if (input) input.click();
}

async function refreshResolution() {
    const selected = oranState.selectedSpecs;

    if (selected.length === 0) {
        const listEl = document.getElementById('spec-resolution-list');
        if (listEl) listEl.style.display = 'none';
        updateActionButtons();
        return;
    }

    selected.forEach(s => {
        if (specStates[s]?.status !== 'manual') {
            specStates[s] = { status: 'pending', file: null, filename: null };
        }
    });

    renderResolutionList();

    try {
        const params = new URLSearchParams();
        selected.forEach(s => params.append('selected', s));

        const resp = await fetch(`/api/oran/resolve-specs?${params}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

        const data = await resp.json();

        data.specs.forEach(spec => {
            if (specStates[spec.spec_type]?.status !== 'manual') {
                specStates[spec.spec_type] = {
                    status: spec.status,
                    file: null,
                    filename: spec.filename
                };
            }
        });
    } catch (err) {
        console.warn('resolve-specs failed, marking selected specs as missing:', err);
        selected.forEach(s => {
            if (specStates[s]?.status !== 'manual') {
                specStates[s] = { status: 'missing', file: null, filename: null };
            }
        });
    }

    renderResolutionList();
    updateActionButtons();
}

function renderResolutionList() {
    const listEl = document.getElementById('spec-resolution-list');
    const itemsEl = document.getElementById('spec-resolution-items');
    if (!listEl || !itemsEl) return;

    const selected = oranState.selectedSpecs;

    if (selected.length === 0) {
        listEl.style.display = 'none';
        itemsEl.innerHTML = '';
        return;
    }

    listEl.style.display = 'block';

    itemsEl.innerHTML = selected.map(specType => {
        const meta = SPEC_META[specType] || {};
        const state = specStates[specType] || { status: 'pending' };

        let statusIcon = '...';
        let statusText = 'Checking...';
        let statusClass = 'status-pending';
        let actionHtml = '';

        if (state.status === 'auto') {
            statusIcon = '?';
            statusText = `Found in docs folder: ${state.filename}`;
            statusClass = 'status-auto';
        } else if (state.status === 'manual') {
            statusIcon = '?';
            statusText = `File selected: ${state.filename}`;
            statusClass = 'status-manual';
        } else if (state.status === 'missing') {
            statusIcon = '!';
            statusText = 'Not found in docs folder - please select file';
            statusClass = 'status-missing';
            actionHtml = `<button class="btn-choose-file btn-sm" data-spec="${specType}">Choose File</button>`;
        }

        return `
            <div class="spec-resolution-item ${statusClass}">
                <span class="spec-resolution-icon">${statusIcon}</span>
                <div class="spec-resolution-info">
                    <strong>${meta.tsNumber || specType}</strong>
                    <span class="spec-resolution-title-text">${meta.title || ''}</span>
                    <span class="spec-resolution-status">${statusText}</span>
                </div>
                <div class="spec-resolution-action">${actionHtml}</div>
            </div>
        `;
    }).join('');

    itemsEl.querySelectorAll('.btn-choose-file').forEach(btn => {
        btn.addEventListener('click', () => triggerFilePicker(btn.dataset.spec));
    });
}

function updateActionButtons() {
    const selected = oranState.selectedSpecs;
    const allResolved = selected.length > 0 && selected.every(s => ['auto', 'manual'].includes(specStates[s]?.status));

    const generateBtn = document.getElementById('generate-catalog-btn');
    const previewBtn = document.getElementById('preview-sections-btn');

    if (generateBtn) generateBtn.disabled = !allResolved;
    if (previewBtn) previewBtn.disabled = !allResolved;
}

function handleMethodologySpecChange() {
    const summary = document.getElementById('methodology-analysis-summary');
    if (summary) {
        summary.textContent = 'Specification selected. Click Preview Modules & Titles to analyze the document.';
    }
}

async function handleAnalyzeMethodology() {
    const specType = document.getElementById('methodology-spec-select')?.value || 'TS_103_989';
    const summary = document.getElementById('methodology-analysis-summary');
    const sectionsEl = document.getElementById('methodology-analysis-sections');
    const modulesEl = document.getElementById('methodology-analysis-modules');
    const titlesEl = document.getElementById('methodology-analysis-titles');

    if (summary) summary.textContent = `Analyzing ${specType}...`;
    if (sectionsEl) sectionsEl.innerHTML = '<div class="analysis-placeholder">Loading methodology sections...</div>';
    if (modulesEl) modulesEl.innerHTML = '<div class="analysis-placeholder">Loading module candidates...</div>';
    if (titlesEl) titlesEl.innerHTML = '<div class="analysis-placeholder">Loading test title candidates...</div>';

    try {
        const response = await fetch(`/api/oran/extract-methodology?spec_type=${encodeURIComponent(specType)}&service_type=${encodeURIComponent(oranState.selectedService)}`, {
            method: 'POST'
        });
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();
        oranState.methodologyAnalysis = data;
        renderMethodologyAnalysis(data);
    } catch (error) {
        console.error('Error analyzing methodology:', error);
        if (summary) summary.textContent = `Failed to analyze ${specType}: ${error.message}`;
        if (sectionsEl) sectionsEl.innerHTML = '<div class="analysis-placeholder error">Analysis failed.</div>';
        if (modulesEl) modulesEl.innerHTML = '<div class="analysis-placeholder error">Analysis failed.</div>';
        if (titlesEl) titlesEl.innerHTML = '<div class="analysis-placeholder error">Analysis failed.</div>';
    }
}

function renderMethodologyAnalysis(data) {
    const summary = document.getElementById('methodology-analysis-summary');
    const sectionsEl = document.getElementById('methodology-analysis-sections');
    const modulesEl = document.getElementById('methodology-analysis-modules');
    const titlesEl = document.getElementById('methodology-analysis-titles');

    if (summary) {
        summary.innerHTML = `
            <strong>${data.spec_file}</strong> | 
            ${data.summary?.methodology_sections_found || 0} methodology sections | 
            ${data.summary?.test_modules_found || 0} module candidates | 
            ${data.summary?.test_titles_found || 0} test title candidates
        `;
    }

    if (sectionsEl) {
        const sections = data.methodology_sections || [];
        sectionsEl.innerHTML = sections.length === 0
            ? '<div class="analysis-placeholder">No methodology sections detected.</div>'
            : sections.map(section => {
                const headingText = `${section.section_number} ${section.title}`.trim();
                const normalizedHeading = headingText.toLowerCase();
                const normalizedTitle = String(section.title || '').trim().toLowerCase();
                const filteredEvidence = (section.evidence || [])
                    .filter(item => {
                        const normalizedItem = String(item || '').trim().toLowerCase();
                        return normalizedItem && normalizedItem !== normalizedHeading && normalizedItem !== normalizedTitle;
                    })
                    .slice(0, 3);

                return `
                <div class="analysis-item">
                    <div class="analysis-item-title">${escapeHtml(headingText)}</div>
                    ${filteredEvidence.length > 0
                        ? `<div class="analysis-item-evidence">${filteredEvidence.map(e => `<span>${escapeHtml(e)}</span>`).join('')}</div>`
                        : ''}
                </div>
            `;
            }).join('');
    }

    if (modulesEl) {
        const modules = data.test_modules || [];
        modulesEl.innerHTML = modules.length === 0
            ? '<div class="analysis-placeholder">No module candidates detected.</div>'
            : modules.map(module => `
                <div class="analysis-item analysis-item--compact">
                    <div class="analysis-item-title">${escapeHtml(module.module_name)}</div>
                    <div class="analysis-item-meta">${escapeHtml(module.module_id)} • confidence ${Number(module.confidence || 0).toFixed(2)}</div>
                    <div class="analysis-item-subtext">Source: ${escapeHtml(module.source_section || 'n/a')} ${module.source_title ? `• ${escapeHtml(module.source_title)}` : ''}</div>
                </div>
            `).join('');
    }

    if (titlesEl) {
        const titles = data.test_titles || [];
        titlesEl.innerHTML = titles.length === 0
            ? '<div class="analysis-placeholder">No test title candidates detected.</div>'
            : titles.map(title => `
                <div class="analysis-item analysis-item--compact">
                    <div class="analysis-item-title">${escapeHtml(title.title)}</div>
                    <div class="analysis-item-meta">Module: ${escapeHtml(title.module_id)} • confidence ${Number(title.confidence || 0).toFixed(2)}</div>
                </div>
            `).join('');
    }
}

function escapeHtml(text) {
    return String(text)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

async function handleGenerateCatalog() {
    const catalogName = document.getElementById('catalog-name')?.value || getDefaultCatalogName();
    const catalogDesc = document.getElementById('catalog-description')?.value || '';

    const progressDiv = document.getElementById('upload-progress');
    const statusDiv = document.getElementById('generation-status');
    const statusLog = document.getElementById('generation-log');

    if (progressDiv) progressDiv.style.display = 'block';
    if (statusDiv) statusDiv.style.display = 'block';
    if (statusLog) statusLog.innerHTML = '<p>Preparing specifications...</p>';

    try {
        const formData = new FormData();

        for (const specType of oranState.selectedSpecs) {
            const state = specStates[specType];
            formData.append('selected_specs', specType);

            if (state?.status === 'manual' && state.file) {
                formData.append(specType.toLowerCase(), state.file);
            }
        }

        if (statusLog) statusLog.innerHTML += '<p>Uploading / resolving specifications...</p>';

        const uploadResponse = await fetch(`/api/oran/upload-specs?service_type=${encodeURIComponent(oranState.selectedService)}`, {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error('Failed to upload / resolve specifications');
        }

        const uploadResult = await uploadResponse.json();

        if (uploadResult.status !== 'ready') {
            const missing = (uploadResult.missing || []).join(', ');
            throw new Error(`Missing specification files: ${missing}`);
        }

        if (statusLog) statusLog.innerHTML += `<p>✓ ${uploadResult.message}</p>`;

        if (statusLog) {
            const extractionMethod = oranState.useRules ? 'rule-based' : 'heuristic';
            statusLog.innerHTML += `<p>Generating test catalog (${extractionMethod} extraction)...</p>`;
        }

        const generateResponse = await fetch(
            `/api/oran/generate?catalog_name=${encodeURIComponent(catalogName)}&description=${encodeURIComponent(catalogDesc)}&use_rules=${oranState.useRules}&service_type=${encodeURIComponent(oranState.selectedService)}`,
            { method: 'POST' }
        );

        if (!generateResponse.ok) {
            throw new Error('Failed to generate catalog');
        }

        const result = await generateResponse.json();

        if (statusLog) {
            statusLog.innerHTML += `<p>? Catalog generated: ${result.catalog_id}</p>`;
            statusLog.innerHTML += '<p class="success">Generation complete! Switch to Test Catalog tab to view.</p>';
        }

        setTimeout(() => {
            document.querySelector('[data-tab="oran-catalog"]')?.click();
            loadCatalogs();
        }, 1500);
    } catch (error) {
        console.error('Error generating catalog:', error);
        if (statusLog) {
            statusLog.innerHTML += `<p class="error">? Error: ${error.message}</p>`;
        }
    } finally {
        if (progressDiv) progressDiv.style.display = 'none';
    }
}

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

function displayCatalogs(catalogs) {
    const catalogsList = document.getElementById('catalogs-list');
    if (!catalogsList) return;

    if (catalogs.length === 0) {
        catalogsList.innerHTML = '<p class="placeholder">No test catalogs generated yet. Select specifications and generate your first catalog.</p>';
        return;
    }

    catalogsList.innerHTML = catalogs.map(catalog => `
        <div class="catalog-card" data-catalog-id="${catalog.catalog_id}">
            <div class="catalog-header">
                <div class="catalog-header-title-wrap">
                    <h3>${catalog.name}</h3>
                    <button class="btn-danger btn-sm delete-catalog-btn" data-catalog-id="${catalog.catalog_id}" data-catalog-name="${catalog.name}">Delete</button>
                </div>
                <span class="catalog-badge">${catalog.total_tests} tests</span>
            </div>
            <p class="catalog-description">${catalog.description || 'No description'}</p>
            <div class="catalog-meta">
                    <span>${catalog.service_name || catalog.service_type || 'A1 service not set'}</span>
                <span>Generated: ${new Date(catalog.generated_at).toLocaleString()}</span>
            </div>
            <div class="catalog-actions">
                <button class="btn-primary btn-sm view-catalog-btn" data-catalog-id="${catalog.catalog_id}">View Tests</button>
                <button class="btn-secondary btn-sm" onclick="window.open('/api/oran/catalogs/${catalog.catalog_id}', '_blank')">Export JSON</button>
            </div>
        </div>
    `).join('');

    document.querySelectorAll('.view-catalog-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const catalogId = e.target.dataset.catalogId;
            viewCatalogTests(catalogId);
        });
    });

    document.querySelectorAll('.delete-catalog-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const catalogId = e.target.dataset.catalogId;
            const catalogName = e.target.dataset.catalogName;
            deleteCatalog(catalogId, catalogName);
        });
    });
}

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

async function deleteCatalog(catalogId, catalogName) {
    const confirmed = window.confirm(`Delete catalog "${catalogName}"? This will remove the catalog file and its saved test cases.`);
    if (!confirmed) return;

    try {
        const response = await fetch(`/api/oran/catalogs/${catalogId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Failed to delete catalog');
        }

        if (oranState.currentCatalog?.catalog_id === catalogId) {
            oranState.currentCatalog = null;
            document.getElementById('catalog-details')?.style && (document.getElementById('catalog-details').style.display = 'none');
        }

        await loadCatalogs();
    } catch (error) {
        console.error('Error deleting catalog:', error);
        alert(`Failed to delete catalog: ${error.message}`);
    }
}

function displayCatalogDetails(catalog) {
    const detailsDiv = document.getElementById('catalog-details');
    if (!detailsDiv) return;

    document.getElementById('catalog-title').textContent = catalog.name;
    document.getElementById('catalog-generated').textContent = new Date(catalog.generated_at).toLocaleString();
    document.getElementById('catalog-total-tests').textContent = catalog.total_tests;
    document.getElementById('catalog-sources').textContent = Object.keys(catalog.spec_sources || {}).join(', ');

    const serviceSummary = [catalog.service_type, catalog.service_name].filter(Boolean).join(' • ');
    if (serviceSummary) {
        document.getElementById('catalog-title').textContent = `${catalog.name} (${serviceSummary})`;
    }

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

    document.getElementById('close-catalog-btn')?.addEventListener('click', () => {
        detailsDiv.style.display = 'none';
    });

    detailsDiv.style.display = 'block';
}

async function viewTestScript(testId) {
    try {
        const response = await fetch(`/api/oran/scripts/${testId}`);
        if (!response.ok) {
            throw new Error('Failed to load test script');
        }

        const scriptData = await response.json();

        const modal = document.getElementById('script-modal');
        document.getElementById('script-test-id').textContent = scriptData.test_id;
        const codeElement = document.getElementById('script-content');
        codeElement.textContent = scriptData.content;

        if (window.Prism) {
            Prism.highlightElement(codeElement);
        }

        modal.dataset.testId = testId;
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error loading test script:', error);
        alert('Failed to load test script. Script may not be generated yet.');
    }
}

async function handleDownloadScript() {
    const modal = document.getElementById('script-modal');
    const testId = modal.dataset.testId;
    if (!testId) return;

    window.open(`/api/oran/scripts/${testId}/download`, '_blank');
}

function handleCopyScript() {
    const codeElement = document.getElementById('script-content');
    const text = codeElement.textContent;

    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copy-script-btn');
        const originalText = btn.textContent;
        btn.textContent = '? Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

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

        document.querySelector('[data-tab="execution"]')?.click();

        alert(`Test execution started!\nExecution ID: ${result.execution_id}\n\nSwitch to Execution tab to view progress.`);
    } catch (error) {
        console.error('Error running test:', error);
        alert('Failed to start test execution.');
    }
}

async function loadServiceDefinitions() {
    try {
        const response = await fetch('/api/oran/services');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        oranState.serviceDefinitions = data.services || [];

        const serviceSelect = document.getElementById('service-select');
        if (serviceSelect) {
            const currentValue = serviceSelect.value || oranState.selectedService;
            serviceSelect.innerHTML = oranState.serviceDefinitions.map(service => `
                <option value="${service.service_type}">${service.service_type} - ${service.name}</option>
            `).join('');

            const availableValue = oranState.serviceDefinitions.some(service => service.service_type === currentValue)
                ? currentValue
                : (oranState.serviceDefinitions[0]?.service_type || 'A1-P');

            serviceSelect.value = availableValue;
            oranState.selectedService = availableValue;
        }

        updateServiceSummary();
        syncCatalogNamePlaceholder();
    } catch (error) {
        console.warn('Failed to load service definitions, using fallback options:', error);
        updateServiceSummary();
        syncCatalogNamePlaceholder();
    }
}

function updateServiceSummary() {
    const summary = document.getElementById('service-summary');
    const selected = oranState.serviceDefinitions.find(service => service.service_type === oranState.selectedService);

    if (!summary) return;

    if (selected) {
        summary.textContent = `${selected.consumer_role.label} / ${selected.producer_role.label}`;
    } else if (oranState.selectedService === 'A1-EI') {
        summary.textContent = 'A1-EI Consumer / A1-EI Producer';
    } else {
        summary.textContent = 'A1-P Consumer / A1-P Producer';
    }
}

function getDefaultCatalogName() {
    const selected = oranState.serviceDefinitions.find(service => service.service_type === oranState.selectedService);
    return selected?.default_catalog_name || 'A1 Test Catalog';
}

function syncCatalogNamePlaceholder() {
    const catalogNameInput = document.getElementById('catalog-name');
    if (!catalogNameInput) return;

    catalogNameInput.placeholder = getDefaultCatalogName();
}

// ============================================================================
// Rule-Based Extraction Functions
// ============================================================================

function handleUseRulesToggle(e) {
    oranState.useRules = e.target.checked;
    const infoPanel = document.getElementById('rule-extraction-info');
    
    if (infoPanel) {
        infoPanel.style.display = oranState.useRules ? 'block' : 'none';
    }
    
    console.log('Rule-based extraction:', oranState.useRules ? 'enabled' : 'disabled');
}

async function loadRulePacks() {
    try {
        const response = await fetch('/api/oran/rules');
        if (!response.ok) {
            throw new Error('Failed to load rule packs');
        }
        
        const rulePacks = await response.json();
        oranState.availableRulePacks = rulePacks;
        
        updateRulePackDisplay(rulePacks);
        
        console.log(`Loaded ${rulePacks.length} rule packs`);
    } catch (error) {
        console.error('Error loading rule packs:', error);
        updateRulePackDisplay([]);
    }
}

function updateRulePackDisplay(rulePacks) {
    const nameEl = document.getElementById('rule-pack-name');
    const descEl = document.getElementById('rule-pack-description');
    const viewBtn = document.getElementById('view-hierarchy-btn');
    
    if (rulePacks.length === 0) {
        if (nameEl) nameEl.textContent = 'No rule packs available';
        if (descEl) descEl.textContent = 'Create a rule pack by learning from a document.';
        if (viewBtn) viewBtn.disabled = true;
    } else {
        // Find best matching rule pack for TEST_SPECIFICATION
        const testSpecPack = rulePacks.find(p => p.document_type === 'TEST_SPECIFICATION');
        
        if (testSpecPack) {
            if (nameEl) nameEl.textContent = testSpecPack.name;
            if (descEl) {
                const quality = (testSpecPack.avg_quality_score * 100).toFixed(0);
                descEl.textContent = `${testSpecPack.success_count} successful extractions, ${quality}% avg quality`;
            }
            if (viewBtn) viewBtn.disabled = false;
            oranState.selectedRulePack = testSpecPack;
        } else {
            if (nameEl) nameEl.textContent = `${rulePacks.length} rule packs available`;
            if (descEl) descEl.textContent = 'Click "Manage Rules" to view and apply rule packs.';
            if (viewBtn) viewBtn.disabled = true;
        }
    }
}

async function handleViewHierarchy() {
    // First, extract hierarchy if not already extracted
    if (!oranState.currentHierarchy) {
        await extractHierarchy();
    }
    
    if (oranState.currentHierarchy) {
        displayHierarchyModal(oranState.currentHierarchy);
    }
}

async function extractHierarchy() {
    try {
        const response = await fetch('/api/oran/hierarchy/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                spec_type: 'TS_103_989',
                use_rules: oranState.useRules
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to extract hierarchy');
        }
        
        const result = await response.json();
        oranState.currentHierarchy = result;
        
        // Check if fallback was used
        if (result.fallback_used) {
            showFallbackNotice();
        }
        
        // Check for hybrid mode (quality comparison)
        if (result.quality_score < 0.7 && oranState.useRules && !result.fallback_used) {
            // Low quality from rules, also try heuristic for comparison
            await extractHierarchyHeuristic();
        }
        
        console.log('Hierarchy extracted:', result);
    } catch (error) {
        console.error('Error extracting hierarchy:', error);
        alert('Failed to extract document hierarchy.');
    }
}

async function extractHierarchyHeuristic() {
    try {
        const response = await fetch('/api/oran/hierarchy/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                spec_type: 'TS_103_989',
                use_rules: false
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to extract hierarchy with heuristic');
        }
        
        const heuristicResult = await response.json();
        
        // Show hybrid mode comparison
        showHybridModeNotice(oranState.currentHierarchy, heuristicResult);
        
        // Store both results
        oranState.extractionResults = {
            rules: oranState.currentHierarchy,
            heuristic: heuristicResult
        };
        
        console.log('Heuristic extraction completed for comparison');
    } catch (error) {
        console.error('Error extracting with heuristic:', error);
        // Don't show error to user, just log it
    }
    } catch (error) {
        console.error('Error extracting hierarchy:', error);
        alert('Failed to extract document hierarchy.');
    }
}

function displayHierarchyModal(hierarchyResult) {
    const modal = document.getElementById('hierarchy-modal');
    if (!modal) return;
    
    // Update info
    document.getElementById('hierarchy-doc-name').textContent = 
        hierarchyResult.hierarchy_tree?.document_name || 'Unknown';
    document.getElementById('hierarchy-total-nodes').textContent = 
        hierarchyResult.total_nodes || 0;
    document.getElementById('hierarchy-max-depth').textContent = 
        hierarchyResult.max_depth || 0;
    
    const qualityScore = document.getElementById('hierarchy-quality-score');
    const quality = Math.round((hierarchyResult.quality_score || 0) * 100);
    qualityScore.textContent = `${quality}%`;
    qualityScore.style.background = quality >= 70 ? '#86efac' : quality >= 50 ? '#fcd34d' : '#fca5a5';
    
    // Render tree
    const treeContainer = document.getElementById('hierarchy-tree');
    if (treeContainer && hierarchyResult.hierarchy_tree) {
        treeContainer.innerHTML = renderHierarchyTree(hierarchyResult.hierarchy_tree.root_nodes);
    }
    
    modal.style.display = 'block';
}

function renderHierarchyTree(nodes, level = 0) {
    if (!nodes || nodes.length === 0) return '';
    
    let html = '<div class="tree-node-children">';
    
    for (const node of nodes) {
        const indent = '  '.repeat(level);
        html += `
            <div class="tree-node" data-node-id="${node.id}">
                <div class="tree-node-label">
                    <svg class="tree-node-icon" viewBox="0 0 16 16" fill="none">
                        <circle cx="8" cy="8" r="2" fill="currentColor"/>
                    </svg>
                    <span class="tree-node-section">${node.section_number}</span>
                    <span class="tree-node-title">${node.title}</span>
                </div>
                ${node.children && node.children.length > 0 ? renderHierarchyTree(node.children, level + 1) : ''}
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

function handleManageRules() {
    const modal = document.getElementById('rule-management-modal');
    if (modal) {
        displayRuleManagementModal();
        modal.style.display = 'block';
    }
}

function displayRuleManagementModal() {
    const listContainer = document.getElementById('rule-packs-list');
    if (!listContainer) return;
    
    if (oranState.availableRulePacks.length === 0) {
        listContainer.innerHTML = '<p style="text-align:center;color:#7f8c8d;">No rule packs available. Learn from a document to create one.</p>';
        return;
    }
    
    listContainer.innerHTML = '';
    
    for (const pack of oranState.availableRulePacks) {
        const packEl = document.createElement('div');
        packEl.className = 'rule-pack-item';
        packEl.dataset.packId = pack.id;
        
        const quality = Math.round(pack.avg_quality_score * 100);
        
        packEl.innerHTML = `
            <div class="rule-pack-item-header">
                <span class="rule-pack-item-name">${pack.name}</span>
                <span class="rule-pack-item-type">${pack.document_type}</span>
            </div>
            <div class="rule-pack-item-stats">
                <span>✓ ${pack.success_count} successful</span>
                <span>✗ ${pack.failure_count} failed</span>
                <span>Quality: ${quality}%</span>
            </div>
        `;
        
        packEl.addEventListener('click', () => selectRulePack(pack));
        
        listContainer.appendChild(packEl);
    }
}

async function selectRulePack(pack) {
    // Highlight selected
    document.querySelectorAll('.rule-pack-item').forEach(el => {
        el.classList.remove('selected');
        if (el.dataset.packId === pack.id) {
            el.classList.add('selected');
        }
    });
    
    // Load full details
    try {
        const response = await fetch(`/api/oran/rules/${pack.id}`);
        if (!response.ok) {
            throw new Error('Failed to load rule pack details');
        }
        
        const fullPack = await response.json();
        displayRulePackDetails(fullPack);
    } catch (error) {
        console.error('Error loading rule pack details:', error);
        alert('Failed to load rule pack details.');
    }
}

function displayRulePackDetails(pack) {
    const detailsContainer = document.getElementById('rule-pack-details');
    if (!detailsContainer) return;
    
    detailsContainer.style.display = 'block';
    
    document.getElementById('rule-pack-detail-name').textContent = pack.name;
    document.getElementById('rule-pack-doc-type').textContent = pack.document_type;
    document.getElementById('rule-pack-max-depth').textContent = pack.hierarchy_config.max_depth;
    document.getElementById('rule-pack-success-count').textContent = pack.match_statistics.success_count;
    document.getElementById('rule-pack-failure-count').textContent = pack.match_statistics.failure_count;
    
    const avgQuality = document.getElementById('rule-pack-avg-quality');
    const quality = Math.round(pack.match_statistics.avg_quality_score * 100);
    avgQuality.textContent = `${quality}%`;
    avgQuality.style.background = quality >= 70 ? '#86efac' : quality >= 50 ? '#fcd34d' : '#fca5a5';
    
    // Display extraction rules
    const rulesBody = document.getElementById('extraction-rules-tbody');
    if (rulesBody) {
        rulesBody.innerHTML = '';
        
        for (const rule of pack.extraction_rules) {
            const row = document.createElement('tr');
            
            const patterns = rule.heading_patterns?.slice(0, 2).join(', ') || 
                           rule.required_keywords?.slice(0, 3).join(', ') || '-';
            
            row.innerHTML = `
                <td>${rule.level}</td>
                <td>${rule.level_name}</td>
                <td>${rule.extraction_method}</td>
                <td style="font-size:0.8rem;">${patterns}</td>
            `;
            
            rulesBody.appendChild(row);
        }
    }
    
    // Store selected pack
    oranState.selectedRulePack = pack;
}

async function handleApplyRulePack() {
    if (!oranState.selectedRulePack) {
        alert('No rule pack selected.');
        return;
    }
    
    try {
        const response = await fetch(`/api/oran/rules/${oranState.selectedRulePack.id}/apply`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                spec_type: 'TS_103_989'
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to apply rule pack');
        }
        
        const result = await response.json();
        alert(`Rule pack applied successfully!\n\nExtracted ${result.total_nodes} nodes with ${Math.round(result.avg_confidence * 100)}% confidence.`);
        
        oranState.currentHierarchy = result;
        closeRuleManagementModal();
    } catch (error) {
        console.error('Error applying rule pack:', error);
        alert('Failed to apply rule pack.');
    }
}

async function handleDeleteRulePack() {
    if (!oranState.selectedRulePack) {
        alert('No rule pack selected.');
        return;
    }
    
    const confirmed = confirm(`Delete rule pack "${oranState.selectedRulePack.name}"?\n\nThis action cannot be undone.`);
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/api/oran/rules/${oranState.selectedRulePack.id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete rule pack');
        }
        
        alert('Rule pack deleted successfully.');
        await loadRulePacks();
        displayRuleManagementModal();
        
        document.getElementById('rule-pack-details').style.display = 'none';
        oranState.selectedRulePack = null;
    } catch (error) {
        console.error('Error deleting rule pack:', error);
        alert('Failed to delete rule pack.');
    }
}

async function handleLearnFromDocument() {
    const confirmed = confirm('Learn extraction rules from the current document?\n\nThis will analyze the document structure and create a new rule pack.');
    if (!confirmed) return;
    
    try {
        const response = await fetch('/api/oran/rules/learn', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                spec_type: 'TS_103_989',
                rule_pack_name: 'Learned from TS 103 989'
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to learn from document');
        }
        
        const result = await response.json();
        alert(`Rule pack created successfully!\n\nName: ${result.name}\nExtracted: ${result.extraction_rules.length} rules`);
        
        await loadRulePacks();
        hideFallbackNotice();
    } catch (error) {
        console.error('Error learning from document:', error);
        alert('Failed to learn from document.');
    }
}

function showFallbackNotice() {
    const notice = document.getElementById('heuristic-fallback-notice');
    if (notice) {
        notice.style.display = 'flex';
    }
}

function hideFallbackNotice() {
    const notice = document.getElementById('heuristic-fallback-notice');
    if (notice) {
        notice.style.display = 'none';
    }
}

function showHybridModeNotice(rulesResult, heuristicResult) {
    const notice = document.getElementById('hybrid-mode-notice');
    if (!notice) return;
    
    // Update stats
    const rulesTestCount = document.getElementById('rules-test-count');
    const rulesQuality = document.getElementById('rules-quality');
    const heuristicTestCount = document.getElementById('heuristic-test-count');
    const heuristicQuality = document.getElementById('heuristic-quality');
    
    if (rulesTestCount) rulesTestCount.textContent = `${rulesResult.total_nodes} tests`;
    if (rulesQuality) {
        const quality = Math.round(rulesResult.quality_score * 100);
        rulesQuality.textContent = `Quality: ${quality}%`;
        rulesQuality.style.background = quality >= 70 ? '#86efac' : quality >= 50 ? '#fcd34d' : '#fca5a5';
    }
    
    if (heuristicTestCount) heuristicTestCount.textContent = `${heuristicResult.total_nodes} tests`;
    if (heuristicQuality) {
        const quality = Math.round(heuristicResult.quality_score * 100);
        heuristicQuality.textContent = `Quality: ${quality}%`;
        heuristicQuality.style.background = quality >= 70 ? '#86efac' : quality >= 50 ? '#fcd34d' : '#fca5a5';
    }
    
    // Add event listeners for choice
    document.getElementById('choice-rules')?.addEventListener('change', () => {
        if (oranState.extractionResults) {
            oranState.currentHierarchy = oranState.extractionResults.rules;
            console.log('User selected rule-based extraction');
        }
    });
    
    document.getElementById('choice-heuristic')?.addEventListener('change', () => {
        if (oranState.extractionResults) {
            oranState.currentHierarchy = oranState.extractionResults.heuristic;
            console.log('User selected heuristic extraction');
        }
    });
    
    notice.style.display = 'block';
}

function hideHybridModeNotice() {
    const notice = document.getElementById('hybrid-mode-notice');
    if (notice) {
        notice.style.display = 'none';
    }
}

function handleExportHierarchy() {
    if (!oranState.currentHierarchy) {
        alert('No hierarchy to export.');
        return;
    }
    
    const dataStr = JSON.stringify(oranState.currentHierarchy, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `hierarchy_${Date.now()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
}

// Modal close functions
window.closeHierarchyModal = function() {
    const modal = document.getElementById('hierarchy-modal');
    if (modal) modal.style.display = 'none';
};

window.closeRuleManagementModal = function() {
    const modal = document.getElementById('rule-management-modal');
    if (modal) modal.style.display = 'none';
    
    // Reset selection
    document.getElementById('rule-pack-details').style.display = 'none';
    oranState.selectedRulePack = null;
};

// ============================================================================
// End Rule-Based Extraction Functions
// ============================================================================

export const oran = {
    init: initOranUI,
    loadCatalogs,
    viewTestScript,
    runTest: runOranTest
};
