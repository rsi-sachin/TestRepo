/**
 * O-RAN A1 Test Generation Tool - Web Interface
 * Main Application Script (ORAN MVP Branch)
 */

// Import ORAN modules with cache-busting query strings so browser reloads pick up edits
import { initOranUI } from './oran.js?v=7';
import { initTestManagement } from './test_management.js?v=6';
import { initSectionSelector } from './section_selector.js?v=7';

// Configuration
const API_BASE = window.location.origin + '/api';
const WS_BASE = `ws://${window.location.host}/ws`;

// State
let currentDemo = null;
let currentExecution = null;
let websocket = null;
let chartData = {};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    console.log('O-RAN A1 Test Generation Tool initializing...');
    
    // Initialize Mermaid
    mermaid.initialize({ 
        startOnLoad: true,
        theme: 'default'
    });
    
    // Set up event listeners
    setupNavigation();
    // setupDemoList(); // Disabled for ORAN MVP
    // setupTrafficGenerator(); // Disabled for ORAN MVP
    setupHistory();
    setupConsoleControls();
    
    // Initialize ORAN UI
    initOranUI();
    
    // Initialize Test Management UI (Phase 3)
    initTestManagement();
    
    // Initialize Section Selector UI (Phase 3C)
    initSectionSelector();
    
    // Load initial data
    // await loadDemos(); // Disabled for ORAN MVP
    checkConnection();
});

// Console Controls
function setupConsoleControls() {
    document.getElementById('clear-console-btn').addEventListener('click', () => {
        document.getElementById('console-output').innerHTML = '';
    });
    
    document.getElementById('clear-callflow-btn').addEventListener('click', () => {
        document.getElementById('callflow-diagram').innerHTML = '';
    });
}

// Navigation
function setupNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            switchTab(tab);
        });
    });
}

function switchTab(tabName) {
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}

// Connection Status
async function checkConnection() {
    try {
        const response = await fetch(`${API_BASE}/../health`);
        if (response.ok) {
            updateConnectionStatus(true);
        } else {
            updateConnectionStatus(false);
        }
    } catch (error) {
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const dot = document.getElementById('connection-status');
    const text = document.getElementById('connection-text');
    
    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

// Demo List
function setupDemoList() {
    const searchInput = document.getElementById('demo-search');
    const protocolFilter = document.getElementById('protocol-filter');
    const complexityFilter = document.getElementById('complexity-filter');
    
    searchInput.addEventListener('input', filterDemos);
    protocolFilter.addEventListener('change', filterDemos);
    complexityFilter.addEventListener('change', filterDemos);
}

async function loadDemos() {
    try {
        const response = await fetch(`${API_BASE}/demos`);
        const demos = await response.json();
        
        // Populate protocol filter
        const protocols = [...new Set(demos.map(d => d.protocol))];
        const protocolFilter = document.getElementById('protocol-filter');
        protocols.forEach(proto => {
            const option = document.createElement('option');
            option.value = proto;
            option.textContent = proto;
            protocolFilter.appendChild(option);
        });
        
        // Render demo list
        renderDemoList(demos);
        
    } catch (error) {
        console.error('Failed to load demos:', error);
    }
}

function renderDemoList(demos) {
    const container = document.getElementById('demo-list');
    container.innerHTML = '';
    
    demos.forEach(demo => {
        const item = document.createElement('div');
        item.className = 'demo-item';
        item.innerHTML = `
            <h3>${demo.title}</h3>
            <div>
                <span class="badge">${demo.protocol}</span>
                <span class="badge">${demo.complexity}</span>
            </div>
        `;
        item.addEventListener('click', () => selectDemo(demo));
        container.appendChild(item);
    });
}

function selectDemo(demo) {
    currentDemo = demo;
    
    // Update selection UI
    document.querySelectorAll('.demo-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    
    // Render demo details
    const detailsContainer = document.getElementById('demo-detail-content');
    detailsContainer.innerHTML = `
        <h2>${demo.title}</h2>
        <p><strong>Protocol:</strong> ${demo.protocol}</p>
        <p><strong>Complexity:</strong> ${demo.complexity}</p>
        <p><strong>Description:</strong> ${demo.description}</p>
        <p><strong>Expected Outcome:</strong> ${demo.expectedOutcome}</p>
        <h3>Parameters</h3>
        <div id="demo-params"></div>
        <button class="btn-primary" onclick="runDemo()">Run Demo</button>
    `;
    
    // Render parameters
    const paramsContainer = document.getElementById('demo-params');
    Object.entries(demo.defaultParams || {}).forEach(([key, value]) => {
        const param = document.createElement('div');
        param.className = 'form-group';
        param.innerHTML = `
            <label>${key}</label>
            <input type="text" value="${value}" data-param="${key}">
        `;
        paramsContainer.appendChild(param);
    });
}

async function filterDemos() {
    const searchText = document.getElementById('demo-search').value;
    const protocol = document.getElementById('protocol-filter').value;
    const complexity = document.getElementById('complexity-filter').value;
    
    // Build query parameters
    const params = new URLSearchParams();
    if (protocol) params.append('protocol', protocol);
    if (complexity) params.append('complexity', complexity);
    if (searchText) params.append('search', searchText);
    
    try {
        const response = await fetch(`${API_BASE}/demos?${params}`);
        const demos = await response.json();
        renderDemoList(demos);
    } catch (error) {
        console.error('Failed to filter demos:', error);
    }
}

async function runDemo() {
    if (!currentDemo) return;
    
    // Collect parameters
    const parameters = {};
    document.querySelectorAll('[data-param]').forEach(input => {
        parameters[input.dataset.param] = input.value;
    });
    
    try {
        const response = await fetch(`${API_BASE}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                demo_id: currentDemo.id,
                parameters
            })
        });
        
        const result = await response.json();
        currentExecution = result.execution_id;
        
        // Switch to execution tab
        switchTab('execution');
        
        // Connect WebSocket
        connectWebSocket(result.execution_id);
        
    } catch (error) {
        console.error('Failed to start execution:', error);
        alert('Failed to start demo execution');
    }
}

// WebSocket
function connectWebSocket(executionId) {
    if (websocket) {
        websocket.close();
    }
    
    websocket = new WebSocket(`${WS_BASE}/demo-output/${executionId}`);
    
    websocket.onopen = () => {
        console.log('WebSocket connected');
    };
    
    websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
    };
    
    websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    websocket.onclose = () => {
        console.log('WebSocket closed');
    };
}

function handleWebSocketMessage(message) {
    console.log('WebSocket message:', message);
    
    switch (message.type) {
        case 'connected':
            console.log('Connected to execution stream:', message.execution_id);
            break;
        case 'output':
            // Backend sends output as message.data (string)
            appendConsoleOutput(message.data);
            break;
        case 'sip_message':
            // Individual SIP message
            updateCallFlow({ type: 'sip_message', ...message });
            break;
        case 'call_flow_diagram':
            // Complete Mermaid diagram
            updateCallFlow({ type: 'call_flow_diagram', ...message });
            break;
        case 'traffic_stats':
            updateTrafficStats(message);
            break;
        case 'status':
            updateExecutionStatus(message);
            break;
        case 'error':
            appendConsoleOutput(`ERROR: ${message.data}`);
            break;
        case 'complete':
            onExecutionComplete(message);
            break;
    }
}

function appendConsoleOutput(line) {
    const console = document.getElementById('console-output');
    const lineDiv = document.createElement('div');
    lineDiv.className = 'console-line';
    lineDiv.textContent = line;
    console.appendChild(lineDiv);
    console.scrollTop = console.scrollHeight;
}

function updateCallFlow(message) {
    // Handle individual SIP message
    if (message.type === 'sip_message') {
        const msg = message;
        const from = msg.from_actor || 'Unknown';
        const to = msg.to_actor || 'Unknown';
        
        let arrow = '';
        if (msg.method) {
            // Request message
            arrow = `${from}->>${to}: ${msg.method}`;
        } else if (msg.response_code) {
            // Response message
            arrow = `${to}-->>${from}: ${msg.response_code} ${msg.response_text || ''}`;
        }
        
        console.log('SIP Message:', arrow);
    }
    
    // Handle complete diagram
    if (message.type === 'call_flow_diagram') {
        renderMermaidDiagram(message.mermaid);
    }
}

function renderMermaidDiagram(mermaidSyntax) {
    const container = document.getElementById('callflow-diagram');
    
    // Clear previous diagram
    container.innerHTML = '';
    
    if (!mermaidSyntax) {
        container.innerHTML = '<p class=\"placeholder\">No call flow data available</p>';
        return;
    }
    
    // Create diagram container
    const diagramDiv = document.createElement('div');
    diagramDiv.className = 'mermaid';
    diagramDiv.textContent = mermaidSyntax;
    container.appendChild(diagramDiv);
    
    // Render with Mermaid
    try {
        mermaid.init(undefined, diagramDiv);
        console.log('Mermaid diagram rendered successfully');
    } catch (error) {
        console.error('Error rendering Mermaid diagram:', error);
        container.innerHTML = '<p class=\"error\">Failed to render call flow diagram</p>';
    }
}

function updateExecutionStatus(message) {
    const statusText = message.status || 'unknown';
    console.log('Execution status:', statusText);
    appendConsoleOutput(`>>> Status: ${statusText}`);
}

function onExecutionComplete(message) {
    console.log('Execution complete:', message);
    appendConsoleOutput('\n=== EXECUTION COMPLETE ===');
    
    if (message.statistics) {
        const stats = message.statistics;
        appendConsoleOutput(`Total Attempts: ${stats.total_attempts || 0}`);
        appendConsoleOutput(`Successful: ${stats.successful || 0}`);
        appendConsoleOutput(`Failed: ${stats.failed || 0}`);
        appendConsoleOutput(`Success Rate: ${stats.success_rate || 0}%`);
    }
    
    if (message.status === 'failed' && message.error) {
        appendConsoleOutput(`Error: ${message.error}`);
    }
    
    // Close WebSocket
    if (websocket) {
        websocket.close();
    }
}

function updateTrafficStats(stats) {
    // Update stat cards
    document.getElementById('stat-total').textContent = stats.total_attempts || 0;
    document.getElementById('stat-success').textContent = stats.successful || 0;
    document.getElementById('stat-failed').textContent = stats.failed || 0;
    document.getElementById('stat-rate').textContent = (stats.success_rate || 0).toFixed(1) + '%';
}

// Traffic Generator
function setupTrafficGenerator() {
    // Range sliders
    document.getElementById('concurrent-calls').addEventListener('input', (e) => {
        document.getElementById('concurrent-value').textContent = e.target.value;
    });
    
    document.getElementById('total-calls').addEventListener('input', (e) => {
        document.getElementById('total-value').textContent = e.target.value;
    });
    
    document.getElementById('rampup-time').addEventListener('input', (e) => {
        document.getElementById('rampup-value').textContent = e.target.value;
    });
    
    document.getElementById('failure-rate').addEventListener('input', (e) => {
        document.getElementById('failure-value').textContent = e.target.value;
    });
    
    // Initialize empty Plotly chart
    initializeThroughputChart();
}

function initializeThroughputChart() {
    const layout = {
        title: 'Messages per Second by Node',
        xaxis: { title: 'Time (seconds)' },
        yaxis: { title: 'Messages/Second' },
        showlegend: true
    };
    
    Plotly.newPlot('throughput-chart', [], layout);
}

function updateThroughputChart(stats) {
    // Update Plotly chart with per-node data
    if (!stats.node_stats) return;
    
    const traces = stats.node_stats.map(node => ({
        x: [stats.elapsed_seconds],
        y: [node.messages_per_second],
        name: node.node_name,
        mode: 'lines+markers',
        type: 'scatter'
    }));
    
    Plotly.extendTraces('throughput-chart', 
        {
            x: traces.map(t => t.x),
            y: traces.map(t => t.y)
        },
        traces.map((_, i) => i)
    );
}

// History
function setupHistory() {
    document.getElementById('refresh-history-btn').addEventListener('click', loadHistory);
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/history`);
        const history = await response.json();
        renderHistory(history);
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function renderHistory(history) {
    const container = document.getElementById('history-list');
    container.innerHTML = '<p>No history available yet</p>';
}

// Export functions for inline onclick handlers
window.runDemo = runDemo;
