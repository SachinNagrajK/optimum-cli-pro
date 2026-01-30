// API Base URL
const API_BASE = 'http://localhost:8000/api/v1';

// Global state
let models = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    checkServerStatus();
    loadModels();
    setInterval(checkServerStatus, 30000); // Check every 30 seconds
});

// Tab Navigation
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;

            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab
            button.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');

            // Load data based on tab
            if (targetTab === 'models') {
                loadModels();
            } else if (targetTab === 'inference') {
                populateModelSelect();
            } else if (targetTab === 'ab-testing') {
                populateABSelects();
            }
        });
    });
}

// Check Server Status
async function checkServerStatus() {
    const statusElement = document.getElementById('serverStatus');
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            statusElement.className = 'server-status online';
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Online</span>';
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        statusElement.className = 'server-status offline';
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Offline</span>';
    }
}

// Load Models
async function loadModels() {
    const grid = document.getElementById('modelsGrid');
    grid.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Loading models...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/registry/models`);
        models = await response.json();

        if (models.length === 0) {
            grid.innerHTML = '<div class="loading"><i class="fas fa-box-open"></i><p>No models registered yet</p></div>';
            return;
        }

        grid.innerHTML = models.map(model => createModelCard(model)).join('');
    } catch (error) {
        grid.innerHTML = `<div class="loading"><i class="fas fa-exclamation-circle"></i><p>Error loading models: ${error.message}</p></div>`;
    }
}

// Create Model Card
function createModelCard(model) {
    const backendClass = `badge-${model.backend.toLowerCase()}`;
    return `
        <div class="model-card">
            <div class="model-card-header">
                <div class="model-name">${model.name}</div>
                <div class="model-version">${model.version}</div>
            </div>
            <div class="model-info">
                <div class="model-info-item">
                    <i class="fas fa-microchip"></i>
                    <span class="badge ${backendClass}">${model.backend.toUpperCase()}</span>
                </div>
                <div class="model-info-item">
                    <i class="fas fa-tasks"></i>
                    <span>${model.task || 'N/A'}</span>
                </div>
                <div class="model-info-item">
                    <i class="fas fa-database"></i>
                    <span>${model.size_mb.toFixed(2)} MB</span>
                </div>
                <div class="model-info-item">
                    <i class="fas fa-cube"></i>
                    <span>${model.base_model || 'N/A'}</span>
                </div>
                <div class="model-info-item">
                    <i class="fas fa-clock"></i>
                    <span>${new Date(model.created_at).toLocaleDateString()}</span>
                </div>
            </div>
            <div class="model-actions">
                <button class="btn btn-success btn-small" onclick="useModelForInference('${model.name}', '${model.version}')">
                    <i class="fas fa-play"></i> Test
                </button>
                <button class="btn btn-primary btn-small" onclick="viewModelDetails('${model.name}', '${model.version}')">
                    <i class="fas fa-info-circle"></i> Details
                </button>
            </div>
        </div>
    `;
}

// Use Model for Inference
function useModelForInference(name, version) {
    // Switch to inference tab
    document.querySelector('[data-tab="inference"]').click();
    
    // Select the model
    setTimeout(() => {
        const select = document.getElementById('modelSelect');
        select.value = `${name}:${version}`;
    }, 100);
}

// View Model Details
async function viewModelDetails(name, version) {
    try {
        const response = await fetch(`${API_BASE}/registry/models/${name}?version=${version}`);
        const model = await response.json();
        
        alert(`Model Details:\n\nName: ${model.name}\nVersion: ${model.version}\nBackend: ${model.backend}\nTask: ${model.task}\nSize: ${model.size_mb.toFixed(2)} MB\nBase Model: ${model.base_model}\nCreated: ${new Date(model.created_at).toLocaleString()}`);
    } catch (error) {
        alert(`Error loading model details: ${error.message}`);
    }
}

// Populate Model Select for Inference
function populateModelSelect() {
    const select = document.getElementById('modelSelect');
    
    if (models.length === 0) {
        select.innerHTML = '<option value="">No models available</option>';
        return;
    }

    select.innerHTML = '<option value="">Select a model...</option>' +
        models.map(model => 
            `<option value="${model.name}:${model.version}">${model.name} v${model.version} (${model.backend})</option>`
        ).join('');
}

// Run Inference
async function runInference() {
    const selectValue = document.getElementById('modelSelect').value;
    const inputText = document.getElementById('inputText').value;
    const resultsDiv = document.getElementById('inferenceResults');

    if (!selectValue) {
        alert('Please select a model');
        return;
    }

    if (!inputText.includes('[MASK]')) {
        alert('Input text must contain [MASK] token');
        return;
    }

    const [name, version] = selectValue.split(':');

    resultsDiv.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Running inference...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/registry/models/${name}/predict?version=${version}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input_text: inputText })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Inference failed');
        }

        const result = await response.json();
        displayInferenceResults(result);
    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="loading">
                <i class="fas fa-exclamation-circle" style="color: var(--danger);"></i>
                <p>Error: ${error.message}</p>
            </div>
        `;
    }
}

// Display Inference Results
function displayInferenceResults(result) {
    const resultsDiv = document.getElementById('inferenceResults');
    
    const predictionsHTML = result.predictions.map((pred, index) => `
        <div class="prediction-item" style="opacity: ${1 - (index * 0.15)}">
            <div class="prediction-token">
                <i class="fas fa-award" style="color: ${index === 0 ? 'gold' : index === 1 ? 'silver' : '#cd7f32'};"></i>
                ${pred.token}
            </div>
            <div class="prediction-score">Score: ${pred.score.toFixed(4)}</div>
        </div>
    `).join('');

    resultsDiv.innerHTML = `
        <div class="result-header">
            <h3><i class="fas fa-chart-bar"></i> Predictions</h3>
            <div class="result-meta">
                <div class="meta-item">
                    <i class="fas fa-box"></i>
                    <strong>${result.model_name}</strong>
                </div>
                <div class="meta-item">
                    <i class="fas fa-microchip"></i>
                    <span>${result.backend.toUpperCase()}</span>
                </div>
                <div class="meta-item">
                    <i class="fas fa-clock"></i>
                    <span>${(result.inference_time * 1000).toFixed(2)}ms</span>
                </div>
            </div>
        </div>
        <div class="predictions-list">
            ${predictionsHTML}
        </div>
    `;
}

// Populate A/B Testing Selects
function populateABSelects() {
    const selectA = document.getElementById('modelA');
    const selectB = document.getElementById('modelB');

    if (models.length === 0) {
        selectA.innerHTML = '<option value="">No models available</option>';
        selectB.innerHTML = '<option value="">No models available</option>';
        return;
    }

    const options = '<option value="">Select a model...</option>' +
        models.map(model => 
            `<option value="${model.name}:${model.version}">${model.name} v${model.version} (${model.backend})</option>`
        ).join('');

    selectA.innerHTML = options;
    selectB.innerHTML = options;
}

// Compare Models
async function compareModels() {
    const modelA = document.getElementById('modelA').value;
    const modelB = document.getElementById('modelB').value;
    const testInput = document.getElementById('testInput').value;
    const resultsDiv = document.getElementById('comparisonResults');

    if (!modelA || !modelB) {
        alert('Please select both models');
        return;
    }

    if (modelA === modelB) {
        alert('Please select different models');
        return;
    }

    if (!testInput.includes('[MASK]')) {
        alert('Test input must contain [MASK] token');
        return;
    }

    resultsDiv.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Running comparison...</p></div>';

    try {
        // Run inference on both models
        const [nameA, versionA] = modelA.split(':');
        const [nameB, versionB] = modelB.split(':');

        const [resultA, resultB] = await Promise.all([
            fetch(`${API_BASE}/registry/models/${nameA}/predict?version=${versionA}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input_text: testInput })
            }).then(r => r.json()),
            fetch(`${API_BASE}/registry/models/${nameB}/predict?version=${versionB}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input_text: testInput })
            }).then(r => r.json())
        ]);

        displayComparisonResults(resultA, resultB);
    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="loading">
                <i class="fas fa-exclamation-circle" style="color: var(--danger);"></i>
                <p>Error: ${error.message}</p>
            </div>
        `;
    }
}

// Display Comparison Results
function displayComparisonResults(resultA, resultB) {
    const resultsDiv = document.getElementById('comparisonResults');
    
    const winnerA = resultA.inference_time < resultB.inference_time;
    const speedup = winnerA ? 
        (resultB.inference_time / resultA.inference_time).toFixed(2) :
        (resultA.inference_time / resultB.inference_time).toFixed(2);
    const winner = winnerA ? 'Model A' : 'Model B';

    const modelSize = models.find(m => m.name === resultA.model_name)?.size_mb || 0;
    const modelBSize = models.find(m => m.name === resultB.model_name)?.size_mb || 0;

    resultsDiv.innerHTML = `
        <div class="comparison-header">
            <h3><i class="fas fa-trophy"></i> Comparison Results</h3>
            <p>Test Input: "${document.getElementById('testInput').value}"</p>
        </div>

        <div class="comparison-grid">
            <div class="model-result ${winnerA ? 'winner' : ''}">
                <div class="model-result-header">
                    <h4>${resultA.model_name} v${resultA.model_version}</h4>
                    ${winnerA ? '<span class="winner-badge"><i class="fas fa-trophy"></i> Winner</span>' : ''}
                </div>
                <div class="metrics-list">
                    <div class="metric-item">
                        <span class="metric-label">Backend</span>
                        <span class="metric-value">${resultA.backend.toUpperCase()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Inference Time</span>
                        <span class="metric-value">${(resultA.inference_time * 1000).toFixed(2)}ms</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Throughput</span>
                        <span class="metric-value">${(1 / resultA.inference_time).toFixed(2)} req/s</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Model Size</span>
                        <span class="metric-value">${modelSize.toFixed(2)} MB</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Top Prediction</span>
                        <span class="metric-value">${resultA.predictions[0].token}</span>
                    </div>
                </div>
            </div>

            <div class="model-result ${!winnerA ? 'winner' : ''}">
                <div class="model-result-header">
                    <h4>${resultB.model_name} v${resultB.model_version}</h4>
                    ${!winnerA ? '<span class="winner-badge"><i class="fas fa-trophy"></i> Winner</span>' : ''}
                </div>
                <div class="metrics-list">
                    <div class="metric-item">
                        <span class="metric-label">Backend</span>
                        <span class="metric-value">${resultB.backend.toUpperCase()}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Inference Time</span>
                        <span class="metric-value">${(resultB.inference_time * 1000).toFixed(2)}ms</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Throughput</span>
                        <span class="metric-value">${(1 / resultB.inference_time).toFixed(2)} req/s</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Model Size</span>
                        <span class="metric-value">${modelBSize.toFixed(2)} MB</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Top Prediction</span>
                        <span class="metric-value">${resultB.predictions[0].token}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="speedup-banner">
            <h4><i class="fas fa-rocket"></i> Performance Summary</h4>
            <div class="speedup-value">${speedup}x</div>
            <p>${winner} is ${speedup}x faster!</p>
        </div>
    `;
}
