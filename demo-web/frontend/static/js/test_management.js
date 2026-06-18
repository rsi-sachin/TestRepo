/**
 * Test Case Management UI (Phase 3)
 * Handles test case review, filtering, editing, and enrichment display
 */

// State
const testMgmtState = {
    tests: [],
    currentPage: 1,
    pageSize: 50,
    totalTests: 0,
    sectionsBySpec: {},
    filters: {
        source_spec: [],
        source_section: null,
        http_method: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    },
    currentEditTest: null
};

// Initialize Test Management UI
export function initTestManagement() {
    console.log('Initializing Test Management UI...');
    
    // Setup event listeners
    document.getElementById('refresh-tests-btn')?.addEventListener('click', loadTests);
    document.getElementById('apply-filters-btn')?.addEventListener('click', applyFilters);
    document.getElementById('clear-filters-btn')?.addEventListener('click', clearFilters);
    document.getElementById('filter-spec')?.addEventListener('change', handleSourceSpecChange);
    document.getElementById('prev-page-btn')?.addEventListener('click', () => changePage(-1));
    document.getElementById('next-page-btn')?.addEventListener('click', () => changePage(1));
    
    // Setup edit form submission
    document.getElementById('edit-test-form')?.addEventListener('submit', handleSaveEdit);
    
    loadSectionOptions();

    // Load initial data
    loadTests();
}

// Load test cases from database
async function loadTests() {
    try {
        console.log('Loading test cases from database...');
        
        // Build query parameters
        const params = new URLSearchParams({
            page: testMgmtState.currentPage,
            page_size: testMgmtState.pageSize
        });
        
        // Add filters
        if (testMgmtState.filters.source_spec.length > 0) {
            testMgmtState.filters.source_spec.forEach(spec => {
                params.append('source_spec', spec);
            });
        }
        
        if (testMgmtState.filters.source_section) {
            params.append('source_section', testMgmtState.filters.source_section);
        }
        
        if (testMgmtState.filters.http_method.length > 0 && testMgmtState.filters.http_method.length < 5) {
            testMgmtState.filters.http_method.forEach(method => {
                params.append('http_method', method);
            });
        }
        
        const response = await fetch(`/api/oran/test-cases?${params}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        testMgmtState.tests = data.test_cases;
        testMgmtState.totalTests = data.total;
        testMgmtState.currentPage = data.page;
        
        displayTests();
        updatePagination();
        updateTestCount();
        
        console.log(`Loaded ${data.test_cases.length} test cases (page ${data.page})`);
        
    } catch (error) {
        console.error('Failed to load test cases:', error);
        showError('Failed to load test cases');
    }
}

// Display test cases in table
function displayTests() {
    const tbody = document.getElementById('test-management-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (testMgmtState.tests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">No test cases found</td></tr>';
        return;
    }
    
    testMgmtState.tests.forEach(test => {
        const row = document.createElement('tr');
        row.dataset.testId = test.id;
        
        row.innerHTML = `
            <td><code>${escapeHtml(test.test_id)}</code></td>
            <td class="test-scenario">${escapeHtml(test.scenario)}</td>
            <td><span class="badge badge-spec">${test.source_spec}</span><br>
                <small>§${test.source_section} p.${test.source_page || 'N/A'}</small></td>
            <td><span class="badge badge-method badge-${test.http_method}">${test.http_method}</span></td>
            <td><code class="endpoint">${escapeHtml(test.endpoint)}</code></td>
            <td><span class="badge badge-status">${test.expected_status}</span></td>
            <td>
                <button class="btn-icon" onclick="showEnrichment(${test.id})" title="View enrichment sources">
                    <svg width="16" height="16" fill="currentColor">
                        <path d="M8 2a6 6 0 100 12A6 6 0 008 2zm0 9.5a.75.75 0 110-1.5.75.75 0 010 1.5zm.75-3.25a.75.75 0 01-1.5 0v-3a.75.75 0 011.5 0v3z"/>
                    </svg>
                </button>
            </td>
            <td class="actions">
                <button class="btn-icon btn-edit" onclick="editTest(${test.id})" title="Edit test case">
                    <svg width="16" height="16" fill="currentColor">
                        <path d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 000-.354l-1.086-1.086zM11.189 6.25L9.75 4.81 2.28 12.28a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.249.249 0 00.108-.064l7.47-7.47z"/>
                    </svg>
                </button>
                <button class="btn-icon btn-delete" onclick="deleteTest(${test.id}, '${escapeHtml(test.test_id)}')" title="Delete test case">
                    <svg width="16" height="16" fill="currentColor">
                        <path d="M6.5 1.75a.25.25 0 01.25-.25h2.5a.25.25 0 01.25.25V3h-3V1.75zm4.5 0V3h2.25a.75.75 0 010 1.5H2.75a.75.75 0 010-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75zM4.496 6.675a.75.75 0 10-1.492.15l.66 6.6A1.75 1.75 0 005.405 15h5.19c.9 0 1.652-.681 1.741-1.576l.66-6.6a.75.75 0 00-1.492-.149l-.66 6.6a.25.25 0 01-.249.225h-5.19a.25.25 0 01-.249-.225l-.66-6.6z"/>
                    </svg>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Apply filters
function applyFilters() {
    // Get selected spec
    const specSelect = document.getElementById('filter-spec');
    testMgmtState.filters.source_spec = specSelect.value ? [specSelect.value] : [];
    
    // Get section filter
    testMgmtState.filters.source_section = document.getElementById('filter-section').value || null;
    
    // Get selected HTTP methods
    const methodCheckboxes = document.querySelectorAll('input[name="method"]:checked');
    testMgmtState.filters.http_method = Array.from(methodCheckboxes).map(cb => cb.value);
    
    // Reset to first page
    testMgmtState.currentPage = 1;
    
    // Reload tests
    loadTests();
}

// Clear all filters
function clearFilters() {
    // Reset form
    document.getElementById('filter-spec').selectedIndex = 0;
    document.getElementById('filter-section').value = '';
    document.querySelectorAll('input[name="method"]').forEach(cb => cb.checked = true);
    populateSectionDatalist('');
    
    // Reset state
    testMgmtState.filters = {
        source_spec: [],
        source_section: null,
        http_method: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    };
    
    testMgmtState.currentPage = 1;
    loadTests();
}

async function loadSectionOptions() {
    try {
        const response = await fetch('/api/oran/sections/options');
        if (!response.ok) {
            return;
        }

        const data = await response.json();
        testMgmtState.sectionsBySpec = data.sections_by_spec || {};
        populateSectionDatalist('');
    } catch (error) {
        console.warn('Section options not available yet:', error);
    }
}

function handleSourceSpecChange(event) {
    const selectedSpec = event.target.value;
    const sectionInput = document.getElementById('filter-section');

    populateSectionDatalist(selectedSpec);

    const specSections = testMgmtState.sectionsBySpec[selectedSpec] || [];
    if (selectedSpec && specSections.length > 0) {
        sectionInput.value = specSections[0].section_number;
    } else {
        sectionInput.value = '';
    }
}

function populateSectionDatalist(spec) {
    const datalist = document.getElementById('filter-section-options');
    if (!datalist) return;

    let options = [];
    if (spec) {
        options = testMgmtState.sectionsBySpec[spec] || [];
    } else {
        Object.values(testMgmtState.sectionsBySpec).forEach(specSections => {
            options = options.concat(specSections || []);
        });
    }

    const seen = new Set();
    datalist.innerHTML = options
        .filter(option => {
            if (!option.section_number || seen.has(option.section_number)) return false;
            seen.add(option.section_number);
            return true;
        })
        .map(option => `<option value="${option.section_number}">${escapeHtml(option.title || '')}</option>`)
        .join('');
}

// Change page
function changePage(delta) {
    const totalPages = Math.ceil(testMgmtState.totalTests / testMgmtState.pageSize);
    const newPage = testMgmtState.currentPage + delta;
    
    if (newPage >= 1 && newPage <= totalPages) {
        testMgmtState.currentPage = newPage;
        loadTests();
    }
}

// Update pagination UI
function updatePagination() {
    const totalPages = Math.ceil(testMgmtState.totalTests / testMgmtState.pageSize);
    
    document.getElementById('pagination-text').textContent = `Page ${testMgmtState.currentPage} of ${totalPages}`;
    document.getElementById('prev-page-btn').disabled = testMgmtState.currentPage === 1;
    document.getElementById('next-page-btn').disabled = testMgmtState.currentPage === totalPages;
    
    // Update page numbers
    const pageNumbers = document.getElementById('page-numbers');
    if (pageNumbers) {
        pageNumbers.innerHTML = '';
        const start = Math.max(1, testMgmtState.currentPage - 2);
        const end = Math.min(totalPages, testMgmtState.currentPage + 2);
        
        for (let i = start; i <= end; i++) {
            const btn = document.createElement('button');
            btn.textContent = i;
            btn.className = i === testMgmtState.currentPage ? 'page-btn active' : 'page-btn';
            btn.onclick = () => {
                testMgmtState.currentPage = i;
                loadTests();
            };
            pageNumbers.appendChild(btn);
        }
    }
}

// Update test count badge
function updateTestCount() {
    const badge = document.getElementById('test-count-badge');
    if (badge) {
        badge.textContent = `${testMgmtState.totalTests} test${testMgmtState.totalTests !== 1 ? 's' : ''}`;
    }
}

// Edit test case
window.editTest = async function(testId) {
    try {
        const response = await fetch(`/api/oran/test-cases/${testId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const test = await response.json();
        testMgmtState.currentEditTest = test;
        
        // Populate form
        document.getElementById('edit-test-id').value = test.id;
        document.getElementById('edit-scenario').value = test.scenario;
        document.getElementById('edit-description').value = test.description || '';
        document.getElementById('edit-method').value = test.http_method;
        document.getElementById('edit-status').value = test.expected_status;
        document.getElementById('edit-endpoint').value = test.endpoint;
        document.getElementById('edit-complexity').value = test.complexity;
        
        // Show modal
        document.getElementById('edit-test-modal').style.display = 'flex';
        
    } catch (error) {
        console.error('Failed to load test case:', error);
        showError('Failed to load test case');
    }
};

// Handle save edit
async function handleSaveEdit(event) {
    event.preventDefault();
    
    const testId = document.getElementById('edit-test-id').value;
    const updates = {
        scenario: document.getElementById('edit-scenario').value,
        description: document.getElementById('edit-description').value,
        http_method: document.getElementById('edit-method').value,
        expected_status: parseInt(document.getElementById('edit-status').value),
        endpoint: document.getElementById('edit-endpoint').value,
        complexity: document.getElementById('edit-complexity').value
    };
    
    try {
        const response = await fetch(`/api/oran/test-cases/${testId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(updates)
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        closeEditModal();
        showSuccess('Test case updated successfully');
        loadTests(); // Reload to show changes
        
    } catch (error) {
        console.error('Failed to update test case:', error);
        showError('Failed to update test case');
    }
}

// Close edit modal
window.closeEditModal = function() {
    document.getElementById('edit-test-modal').style.display = 'none';
    testMgmtState.currentEditTest = null;
};

// Delete test case
window.deleteTest = async function(testId, testName) {
    if (!confirm(`Delete test case "${testName}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/oran/test-cases/${testId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        showSuccess('Test case deleted successfully');
        loadTests(); // Reload to show changes
        
    } catch (error) {
        console.error('Failed to delete test case:', error);
        showError('Failed to delete test case');
    }
};

// Show enrichment details
window.showEnrichment = async function(testId) {
    try {
        const response = await fetch(`/api/oran/test-cases/${testId}/enrichments`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const enrichments = await response.json();
        
        const content = document.getElementById('enrichment-content');
        if (!content) return;
        
        if (enrichments.length === 0) {
            content.innerHTML = '<p class="text-muted">No enrichment data available</p>';
        } else {
            content.innerHTML = `
                <div class="enrichment-list">
                    ${enrichments.map(e => `
                        <div class="enrichment-item">
                            <div class="enrichment-type">${formatEnrichmentType(e.enrichment_type)}</div>
                            <div class="enrichment-source">
                                <strong>${e.source_spec}</strong>
                                ${e.source_section ? `Section ${e.source_section}` : ''}
                                ${e.source_page ? `(Page ${e.source_page})` : ''}
                            </div>
                            ${e.value ? `<div class="enrichment-value">${escapeHtml(e.value)}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        document.getElementById('enrichment-modal').style.display = 'flex';
        
    } catch (error) {
        console.error('Failed to load enrichments:', error);
        showError('Failed to load enrichment data');
    }
};

// Close enrichment modal
window.closeEnrichmentModal = function() {
    document.getElementById('enrichment-modal').style.display = 'none';
};

// Utility functions
function formatEnrichmentType(type) {
    const types = {
        'base': 'Base Clause',
        'endpoint': 'API Endpoint',
        'status_code': 'Status Code',
        'payload': 'Payload Schema',
        'validation': 'Validation Rules',
        'terminology': 'Terminology'
    };
    return types[type] || type;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccess(message) {
    // Simple success notification - can be enhanced with a toast library
    alert(message);
}

function showError(message) {
    // Simple error notification - can be enhanced with a toast library
    alert(`Error: ${message}`);
}
