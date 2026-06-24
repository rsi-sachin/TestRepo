/**
 * Section Selector Module (Phase 3C)
 * Handles section preview and selection for test catalog generation
 */

// State management
const sectionSelectorState = {
    allSections: {},
    selectedSections: new Set(),
    filteredSections: [],
    catalogName: '',
    catalogDescription: ''
};

/**
 * Initialize section selector
 */
export function initSectionSelector() {
    const previewBtn = document.getElementById('preview-sections-btn');
    if (previewBtn) {
        previewBtn.addEventListener('click', handlePreviewSections);
    }

    // Modal controls
    document.getElementById('cancel-selection-btn')?.addEventListener('click', closeSectionSelectionModal);
    document.getElementById('generate-from-selection-btn')?.addEventListener('click', handleGenerateFromSelection);

    // Selection actions
    document.getElementById('select-all-btn')?.addEventListener('click', selectAll);
    document.getElementById('deselect-all-btn')?.addEventListener('click', deselectAll);
    document.getElementById('select-mvp-btn')?.addEventListener('click', selectMVP);
    document.getElementById('select-all-checkbox')?.addEventListener('change', handleSelectAllCheckbox);

    // Filters
    document.getElementById('section-search')?.addEventListener('input', applyFilters);
    document.getElementById('spec-filter')?.addEventListener('change', applyFilters);
}

/**
 * Handle preview sections button click
 */
async function handlePreviewSections() {
    try {
        showLoader('Extracting test sections from specifications...');

        const response = await fetch('/api/oran/preview-sections', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        hideLoader();

        if (!response.ok) {
            const error = await response.json();
            showNotification(error.detail || 'Failed to preview sections', 'error');
            return;
        }

        const data = await response.json();
        
        // Store sections data
        sectionSelectorState.allSections = data.sections_by_spec;
        
        // Get catalog info from form
        sectionSelectorState.catalogName = document.getElementById('catalog-name').value || 'Custom Test Catalog';
        sectionSelectorState.catalogDescription = document.getElementById('catalog-description').value || '';

        // Clear selection
        sectionSelectorState.selectedSections.clear();

        // Display modal
        displaySectionSelectionModal(data);
        
        showNotification(`Found ${data.total_sections} test sections across ${Object.keys(data.sections_by_spec).length} specifications`, 'success');
    } catch (error) {
        hideLoader();
        console.error('Error previewing sections:', error);
        showNotification('Failed to preview sections: ' + error.message, 'error');
    }
}

/**
 * Display section selection modal
 */
function displaySectionSelectionModal(data) {
    const modal = document.getElementById('section-selection-modal');
    const tbody = document.getElementById('sections-table-body');
    
    // Update counts
    document.getElementById('total-count').textContent = data.total_sections;
    document.getElementById('selected-count').textContent = '0';
    document.getElementById('generate-count').textContent = '0';

    // Clear table
    tbody.innerHTML = '';

    // Build flat list of sections for rendering
    const allSections = [];
    for (const [specType, sections] of Object.entries(data.sections_by_spec)) {
        sections.forEach(section => {
            allSections.push({
                spec: specType,
                ...section
            });
        });
    }

    sectionSelectorState.filteredSections = allSections;
    renderSectionsTable();

    // Show modal
    modal.style.display = 'flex';
}

/**
 * Render sections table
 */
function renderSectionsTable() {
    const tbody = document.getElementById('sections-table-body');
    tbody.innerHTML = '';

    if (sectionSelectorState.filteredSections.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">No sections match your filters</td>
            </tr>
        `;
        return;
    }

    sectionSelectorState.filteredSections.forEach(section => {
        const sectionId = `${section.spec}-${section.section_number}`;
        const isSelected = sectionSelectorState.selectedSections.has(sectionId);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="col-checkbox">
                <input type="checkbox" 
                       data-section-id="${sectionId}" 
                       data-spec="${section.spec}"
                       data-section-number="${section.section_number}"
                       ${isSelected ? 'checked' : ''}
                       class="section-checkbox">
            </td>
            <td class="col-spec">
                <span class="badge-spec">${section.spec.replace('TS_', 'TS ')}</span>
            </td>
            <td class="col-section">${section.section_number}</td>
            <td class="col-title" title="${section.description_preview}">
                ${section.title}
            </td>
            <td class="col-page">${section.page}</td>
            <td class="col-complexity">
                <span class="badge-complexity-${section.complexity.toLowerCase()}">${section.complexity}</span>
            </td>
        `;

        // Add click handler for checkbox
        const checkbox = row.querySelector('.section-checkbox');
        checkbox.addEventListener('change', handleSectionToggle);

        tbody.appendChild(row);
    });

    updateSelectionCounts();
}

/**
 * Handle individual section checkbox toggle
 */
function handleSectionToggle(event) {
    const checkbox = event.target;
    const sectionId = checkbox.dataset.sectionId;

    if (checkbox.checked) {
        sectionSelectorState.selectedSections.add(sectionId);
    } else {
        sectionSelectorState.selectedSections.delete(sectionId);
    }

    updateSelectionCounts();
}

/**
 * Handle select all checkbox in header
 */
function handleSelectAllCheckbox(event) {
    if (event.target.checked) {
        selectAll();
    } else {
        deselectAll();
    }
}

/**
 * Select all visible sections
 */
function selectAll() {
    sectionSelectorState.filteredSections.forEach(section => {
        const sectionId = `${section.spec}-${section.section_number}`;
        sectionSelectorState.selectedSections.add(sectionId);
    });

    // Update checkboxes
    document.querySelectorAll('.section-checkbox').forEach(cb => {
        cb.checked = true;
    });

    updateSelectionCounts();
}

/**
 * Deselect all sections
 */
function deselectAll() {
    sectionSelectorState.selectedSections.clear();

    // Update checkboxes
    document.querySelectorAll('.section-checkbox').forEach(cb => {
        cb.checked = false;
    });

    updateSelectionCounts();
}

/**
 * Select MVP default (2 per spec)
 */
function selectMVP() {
    deselectAll();

    // Select first 2 sections from each spec
    const sectionsBySpec = {};
    sectionSelectorState.filteredSections.forEach(section => {
        if (!sectionsBySpec[section.spec]) {
            sectionsBySpec[section.spec] = [];
        }
        if (sectionsBySpec[section.spec].length < 2) {
            sectionsBySpec[section.spec].push(section);
            const sectionId = `${section.spec}-${section.section_number}`;
            sectionSelectorState.selectedSections.add(sectionId);
        }
    });

    // Update checkboxes
    document.querySelectorAll('.section-checkbox').forEach(cb => {
        cb.checked = sectionSelectorState.selectedSections.has(cb.dataset.sectionId);
    });

    updateSelectionCounts();
    showNotification('Selected 2 sections per specification (MVP mode)', 'info');
}

/**
 * Apply filters to sections
 */
function applyFilters() {
    const searchTerm = document.getElementById('section-search').value.toLowerCase();
    const specFilter = document.getElementById('spec-filter').value;

    // Build flat list and apply filters
    const allSections = [];
    for (const [specType, sections] of Object.entries(sectionSelectorState.allSections)) {
        sections.forEach(section => {
            allSections.push({
                spec: specType,
                ...section
            });
        });
    }

    sectionSelectorState.filteredSections = allSections.filter(section => {
        // Spec filter
        if (specFilter && section.spec !== specFilter) {
            return false;
        }

        // Search filter
        if (searchTerm) {
            const searchableText = `${section.title} ${section.section_number}`.toLowerCase();
            if (!searchableText.includes(searchTerm)) {
                return false;
            }
        }

        return true;
    });

    renderSectionsTable();
}

/**
 * Update selection counts and button states
 */
function updateSelectionCounts() {
    const count = sectionSelectorState.selectedSections.size;
    
    document.getElementById('selected-count').textContent = count;
    document.getElementById('generate-count').textContent = count;

    const generateBtn = document.getElementById('generate-from-selection-btn');
    if (generateBtn) {
        generateBtn.disabled = count === 0;
    }

    // Update select all checkbox state
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    if (selectAllCheckbox) {
        const allVisible = sectionSelectorState.filteredSections.length;
        const selectedVisible = sectionSelectorState.filteredSections.filter(s => 
            sectionSelectorState.selectedSections.has(`${s.spec}-${s.section_number}`)
        ).length;

        selectAllCheckbox.checked = allVisible > 0 && selectedVisible === allVisible;
        selectAllCheckbox.indeterminate = selectedVisible > 0 && selectedVisible < allVisible;
    }
}

/**
 * Handle generate from selection
 */
async function handleGenerateFromSelection() {
    const selectedCount = sectionSelectorState.selectedSections.size;
    const serviceType = document.getElementById('service-select')?.value || 'A1-P';
    
    if (selectedCount === 0) {
        showNotification('Please select at least one section', 'warning');
        return;
    }

    try {
        // Close modal
        closeSectionSelectionModal();

        // Show progress
        showLoader(`Generating catalog from ${selectedCount} selected sections...`);

        // Build selection map: { "TS_103_989": ["5.2.6.2.1", ...], ... }
        const selectionMap = {};
        sectionSelectorState.selectedSections.forEach(sectionId => {
            const [spec, ...sectionParts] = sectionId.split('-');
            const sectionNumber = sectionParts.join('-');
            
            if (!selectionMap[spec]) {
                selectionMap[spec] = [];
            }
            selectionMap[spec].push(sectionNumber);
        });

        const response = await fetch(
            `/api/oran/generate-from-selection?catalog_name=${encodeURIComponent(sectionSelectorState.catalogName)}&description=${encodeURIComponent(sectionSelectorState.catalogDescription)}&service_type=${encodeURIComponent(serviceType)}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(selectionMap)
            }
        );

        hideLoader();

        if (!response.ok) {
            const error = await response.json();
            showNotification(error.detail || 'Failed to generate catalog', 'error');
            return;
        }

        const result = await response.json();

        showNotification(
            `Successfully generated catalog with ${result.total_tests} test cases from ${selectedCount} selected sections`,
            'success'
        );

        // Switch to Test Catalog tab
        setTimeout(() => {
            const catalogTab = document.querySelector('[data-tab="catalog"]');
            if (catalogTab) {
                catalogTab.click();
            }
        }, 1500);

    } catch (error) {
        hideLoader();
        console.error('Error generating from selection:', error);
        showNotification('Failed to generate catalog: ' + error.message, 'error');
    }
}

/**
 * Close section selection modal
 */
window.closeSectionSelectionModal = function() {
    const modal = document.getElementById('section-selection-modal');
    if (modal) {
        modal.style.display = 'none';
    }
};

/**
 * Helper: Show loader
 */
function showLoader(message) {
    const uploadProgress = document.getElementById('upload-progress');
    const progressText = uploadProgress?.querySelector('.progress-text');
    
    if (uploadProgress && progressText) {
        progressText.textContent = message;
        uploadProgress.style.display = 'block';
    }
}

/**
 * Helper: Hide loader
 */
function hideLoader() {
    const uploadProgress = document.getElementById('upload-progress');
    if (uploadProgress) {
        uploadProgress.style.display = 'none';
    }
}

/**
 * Helper: Show notification
 */
function showNotification(message, type = 'info') {
    // Use existing notification system or create simple alert
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : type === 'warning' ? '#ed8936' : '#4299e1'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
