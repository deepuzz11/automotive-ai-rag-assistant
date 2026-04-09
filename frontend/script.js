const API_BASE_URL = 'http://localhost:8000';

// Tab logic
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.sidebar-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    
    // Find the button that was clicked and set it to active
    // If it's called from the onclick directly, event.currentTarget works
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}

function handleEnter(event, type) {
    if (event.key === 'Enter') {
        if (type === 'ask') askAssistant();
        if (type === 'search') performSearch();
        if (type === 'recommend') getRecommendations();
    }
}

// AI Assistant
async function askAssistant() {
    const input = document.getElementById('ask-input');
    const question = input.value.trim();
    if (!question) return;

    const btnText = document.getElementById('ask-btn-text');
    const loader = document.getElementById('ask-loader');

    // Add user message
    addMessage(question, 'user');
    input.value = '';
    
    // Show loading
    btnText.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        const data = await response.json();
        
        addMessage(data.answer, 'ai');

        // Show sources if available
        const sourcesContainer = document.getElementById('sources-container');
        if (data.context_used && data.context_used.length > 0) {
            sourcesContainer.innerHTML = '<h4 style="font-size: 0.8rem; color: var(--accent); margin-bottom: 1rem; text-transform: uppercase;">Reference Intelligence:</h4>';
            const grid = document.createElement('div');
            grid.className = 'result-grid';
            
            data.context_used.forEach(src => {
                const item = document.createElement('div');
                item.className = 'result-hex';
                item.style.fontSize = '0.85rem';
                item.innerHTML = `
                    <div class="source-badge">${src.source}</div>
                    <p style="margin-top: 8px;">${src.content.substring(0, 200)}...</p>
                `;
                grid.appendChild(item);
            });
            sourcesContainer.appendChild(grid);
        }
    } catch (error) {
        addMessage('SYSTEM ERROR: Connection to retrieval engine lost.', 'ai');
        console.error(error);
    } finally {
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}

function addMessage(text, side) {
    const chatHistory = document.getElementById('chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${side === 'user' ? 'user-message' : 'ai-message'}`;
    
    if (side === 'ai') {
        msgDiv.innerHTML = `<strong>INTEL_LOG:</strong><br>${text.replace(/\n/g, '<br>')}`;
    } else {
        msgDiv.textContent = text;
    }
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Technical Search
async function performSearch() {
    const input = document.getElementById('search-input');
    const query = input.value.trim();
    if (!query) return;

    const list = document.getElementById('search-results-list');
    const btnText = document.getElementById('search-btn-text');
    const loader = document.getElementById('search-loader');

    list.innerHTML = '';
    btnText.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const results = await response.json();

        if (results.length === 0) {
            list.innerHTML = '<p style="text-align: center; margin-top: 2rem;">NULL RESULTS: No matching documentation identifiers found.</p>';
        } else {
            results.forEach(res => {
                const item = document.createElement('div');
                item.className = 'result-hex';
                item.innerHTML = `
                    <h4>${res.source} | RELABILITY: ${(res.score * 100).toFixed(1)}%</h4>
                    <p>${res.content}</p>
                    <div class="source-badge">UID: ${res.id}</div>
                `;
                list.appendChild(item);
            });
        }
    } catch (error) {
        list.innerHTML = '<p style="color: #ff4d4d; text-align: center;">SYSTEM FAULT during retrieval operation.</p>';
        console.error(error);
    } finally {
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}

// Recommendations
async function getRecommendations() {
    const input = document.getElementById('recommend-input');
    const needs = input.value.trim();
    if (!needs) return;

    const list = document.getElementById('recommend-results');
    const btnText = document.getElementById('recommend-btn-text');
    const loader = document.getElementById('recommend-loader');

    list.innerHTML = '';
    btnText.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ needs })
        });
        const data = await response.json();

        if (data.recommendations.length === 0) {
            list.innerHTML = '<p style="text-align: center;">MATCH_FAILURE: No vehicle configurations met the submitted parameters.</p>';
        } else {
            data.recommendations.forEach(rec => {
                const item = document.createElement('div');
                item.className = 'result-hex';
                item.style.borderLeft = '4px solid var(--accent)';
                item.innerHTML = `
                    <h3 style="color: white; margin-bottom: 0.5rem;">${rec.model.toUpperCase()}</h3>
                    <p style="font-size: 0.9rem; border-top: 1px solid var(--glass-border); padding-top: 10px;">${rec.reasoning}</p>
                    <div class="source-badge">RELEVANCE: ${(rec.score * 100).toFixed(0)}%</div>
                `;
                list.appendChild(item);
            });
        }
    } catch (error) {
        list.innerHTML = '<p style="color: #ff4d4d; text-align: center;">MATCH_ENGINE_FAULT</p>';
        console.error(error);
    } finally {
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}
