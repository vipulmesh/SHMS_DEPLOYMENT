// ===========================
// CONFIGURATION
// ===========================
// Use same-origin relative URLs so this works on Render without localhost.
const API_URL = "";

// ===========================
// DATA SUBMISSION FUNCTION
// ===========================
async function submitData() {
    // Get form values
    const village = document.getElementById('village').value.trim();
    const diarrhea = document.getElementById('diarrhea').value;
    const fever = document.getElementById('fever').value;
    const rainfall = document.getElementById('rainfall').value;

    // Validation
    if (!village || !diarrhea || !fever) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }

    // Prepare data object
    const data = {
        village: village,
        diarrhea: parseInt(diarrhea),
        fever: parseInt(fever),
        rainfall: rainfall
    };

    try {
        // Send POST request to Flask backend
        const response = await fetch(`${API_URL}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (response.status === 401) {
            window.location.href = 'login.html';
            return;
        }

        const result = await response.json();

        if (response.ok) {
            showNotification(`Data submitted successfully! Risk Level: ${result.risk}`, 'success');
            // Clear form
            document.getElementById('village').value = '';
            document.getElementById('diarrhea').value = '';
            document.getElementById('fever').value = '';
            document.getElementById('rainfall').value = 'Low';
        } else {
            showNotification('Error submitting data. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Cannot connect to server. Please ensure Flask is running.', 'error');
    }
}

// ===========================
// LOAD DASHBOARD DATA
// ===========================
async function loadData() {
    try {
        // Fetch data from Flask backend
        const response = await fetch(`${API_URL}/data`);
        if (response.status === 401) {
            window.location.href = 'login.html';
            return;
        }
        const data = await response.json();

        // Update statistics
        updateStatistics(data);

        // Populate table
        populateTable(data);

        // Show high risk alert if needed
        showHighRiskAlert(data);

    } catch (error) {
        console.error('Error loading data:', error);
        showEmptyState('Cannot connect to server. Please ensure Flask is running.');
    }
}

// ===========================
// UPDATE STATISTICS CARDS
// ===========================
function updateStatistics(data) {
    const total = data.length;
    const safe = data.filter(record => record.risk === 'Safe').length;
    const medium = data.filter(record => record.risk === 'Medium Risk').length;
    const high = data.filter(record => record.risk === 'High Risk').length;

    document.getElementById('total-records').textContent = total;
    document.getElementById('safe-areas').textContent = safe;
    document.getElementById('medium-risk').textContent = medium;
    document.getElementById('high-risk').textContent = high;
}

// ===========================
// POPULATE DATA TABLE
// ===========================
function populateTable(data) {
    const container = document.getElementById('table-container');

    if (data.length === 0) {
        showEmptyState();
        return;
    }

    let tableHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Village</th>
                    <th>Diarrhea Cases</th>
                    <th>Fever Cases</th>
                    <th>Rainfall</th>
                    <th>Risk Level</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.forEach(record => {
        const riskClass = getRiskClass(record.risk);
        tableHTML += `
            <tr>
                <td><strong>${record.village}</strong></td>
                <td>${record.diarrhea}</td>
                <td>${record.fever}</td>
                <td>${record.rainfall}</td>
                <td><span class="risk-badge ${riskClass}">${record.risk}</span></td>
                <td>${record.date || 'N/A'}</td>
            </tr>
        `;
    });

    tableHTML += `
            </tbody>
        </table>
    `;

    container.innerHTML = tableHTML;
}

// ===========================
// SHOW EMPTY STATE
// ===========================
function showEmptyState(message = 'No health data recorded yet') {
    const container = document.getElementById('table-container');
    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <p>${message}</p>
            <a href="data-entry.html" class="btn btn-primary">Add First Record</a>
        </div>
    `;
}

// ===========================
// SHOW HIGH RISK ALERT
// ===========================
function showHighRiskAlert(data) {
    const highRiskAreas = data.filter(record => record.risk === 'High Risk');
    const alertBox = document.getElementById('high-risk-alert');

    if (highRiskAreas.length > 0) {
        const alertMessage = document.getElementById('alert-message');
        const areaText = highRiskAreas.length === 1 ? 'area has' : 'areas have';
        alertMessage.textContent = `${highRiskAreas.length} ${areaText} been identified as high risk for water-borne disease outbreak. Immediate action and monitoring recommended.`;
        alertBox.style.display = 'block';
    } else {
        alertBox.style.display = 'none';
    }
}

// ===========================
// HELPER FUNCTIONS
// ===========================
function getRiskClass(risk) {
    switch(risk) {
        case 'Safe':
            return 'safe';
        case 'Medium Risk':
            return 'medium';
        case 'High Risk':
            return 'high';
        default:
            return '';
    }
}

function showNotification(message, type) {
    const notification = document.getElementById('notification');
    if (notification) {
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.style.display = 'block';

        // Hide after 3 seconds
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
}