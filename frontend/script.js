const API_BASE_URL = 'http://localhost:8000';

// --- Rich Text Formatter ---
// Converts LLM output (pseudo-markdown) into clean, styled HTML
function formatResponse(text) {
    if (typeof text !== 'string') return text;
    
    let html = text;

    // Escape HTML first
    html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    // Headers: ### Header -> <h4>, ## Header -> <h3>
    html = html.replace(/^### (.+)$/gm, '<h4 class="resp-h4">$1</h4>');
    html = html.replace(/^## (.+)$/gm, '<h3 class="resp-h3">$1</h3>');

    // Bold: **text** -> <strong>
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic: *text* -> <em>  (but not inside bold)
    html = html.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '<em>$1</em>');
    
    // Bullet points: lines starting with • or - or *
    html = html.replace(/^[•\-\*]\s+(.+)$/gm, '<li>$1</li>');
    // Wrap consecutive <li> in <ul>
    html = html.replace(/((?:<li>.*?<\/li>\s*)+)/g, '<ul class="resp-list">$1</ul>');

    // Numbered lists: 1. text, 2. text
    html = html.replace(/^\d+\.\s+(.+)$/gm, '<li class="numbered">$1</li>');
    html = html.replace(/((?:<li class="numbered">.*?<\/li>\s*)+)/g, '<ol class="resp-list">$1</ol>');
    
    // Source references: [1], [2], etc — make them styled
    html = html.replace(/\[(\d+)\]/g, '<span class="source-ref">[$1]</span>');

    // Line breaks (double newline = paragraph break, single = <br>)
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    // Wrap in paragraph
    html = '<p>' + html + '</p>';
    // Clean up empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, '');

    return html;
}

// Tab logic
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.sidebar-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    
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

// --- AI Assistant ---
async function askAssistant() {
    const input = document.getElementById('ask-input');
    const question = input.value.trim();
    if (!question) return;

    const btnText = document.getElementById('ask-btn-text');
    const loader = document.getElementById('ask-loader');

    // Add user message
    addMessage(question, 'user');
    input.value = '';
    
    // Show loading with typing indicator
    const typingId = showTypingIndicator();
    btnText.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Build rich AI response
        addRichMessage(data);

    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('⚠ Connection to retrieval engine lost. Please check if the server is running.', 'ai');
        console.error(error);
    } finally {
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}

// Typing indicator
function showTypingIndicator() {
    const chatHistory = document.getElementById('chat-history');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai-message typing-indicator';
    typingDiv.id = 'typing-' + Date.now();
    typingDiv.innerHTML = `
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
        <span class="typing-label">Analyzing documentation...</span>
    `;
    chatHistory.appendChild(typingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return typingDiv.id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Rich message renderer for AI responses
function addRichMessage(data) {
    const chatHistory = document.getElementById('chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message rich-response';
    
    // Confidence badge (only for informational queries with context)
    let metaBadge = '';
    if (data.intent === 'informational' && data.confidence != null) {
        const confClass = data.confidence >= 70 ? 'high' : data.confidence >= 40 ? 'medium' : 'low';
        metaBadge = `<div class="response-meta">
            <span class="confidence-badge ${confClass}">
                <span class="conf-dot"></span>
                Relevance: ${data.confidence.toFixed(0)}%
            </span>
            <span class="sources-count">${data.context_used.length} source${data.context_used.length !== 1 ? 's' : ''} analyzed</span>
        </div>`;
    } else if (data.intent && data.intent !== 'informational') {
        const intentLabels = {
            'greeting': '👋 Welcome',
            'closing': '✅ Session',
            'unclear': '❓ Clarification'
        };
        metaBadge = `<div class="response-meta">
            <span class="intent-badge">${intentLabels[data.intent] || data.intent}</span>
        </div>`;
    }

    // Format the answer content
    const formattedAnswer = formatResponse(data.answer);
    
    // Build suggestions chips
    let suggestionsHTML = '';
    if (data.suggestions && data.suggestions.length > 0) {
        const chips = data.suggestions.map(s => 
            `<button class="suggestion-chip" onclick="askFromSuggestion(this)" data-query="${s.replace(/"/g, '&quot;')}">${s}</button>`
        ).join('');
        suggestionsHTML = `<div class="suggestions-row">
            <span class="suggestions-label">Try asking:</span>
            ${chips}
        </div>`;
    }

    msgDiv.innerHTML = `
        ${metaBadge}
        <div class="response-body">${formattedAnswer}</div>
        ${suggestionsHTML}
    `;
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Update sources panel
    updateSourcesPanel(data.context_used);
}

function askFromSuggestion(btn) {
    const query = btn.getAttribute('data-query');
    document.getElementById('ask-input').value = query;
    askAssistant();
}

function updateSourcesPanel(contextUsed) {
    const sourcesContainer = document.getElementById('sources-container');
    if (contextUsed && contextUsed.length > 0) {
        sourcesContainer.innerHTML = '<h4 class="sources-title">📄 Retrieved Context Sources</h4>';
        const grid = document.createElement('div');
        grid.className = 'result-grid';
        
        contextUsed.forEach((src, idx) => {
            const relevanceClass = src.score >= 0.7 ? 'high' : src.score >= 0.4 ? 'medium' : 'low';
            const item = document.createElement('div');
            item.className = 'result-hex source-card';
            item.innerHTML = `
                <div class="source-header">
                    <span class="source-index">[${idx + 1}]</span>
                    <span class="source-file">${src.source.replace('.json', '').toUpperCase()}</span>
                    <span class="relevance-pill ${relevanceClass}">${(src.score * 100).toFixed(1)}%</span>
                </div>
                <div class="source-id">${src.id}</div>
                <p class="source-preview">${src.content.substring(0, 180)}...</p>
            `;
            grid.appendChild(item);
        });
        sourcesContainer.appendChild(grid);
    } else {
        sourcesContainer.innerHTML = '';
    }
}

// Basic message adder (for user messages and simple AI messages)
function addMessage(text, side) {
    const chatHistory = document.getElementById('chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${side === 'user' ? 'user-message' : 'ai-message'}`;
    
    if (side === 'ai') {
        msgDiv.innerHTML = `<div class="response-body">${formatResponse(text)}</div>`;
    } else {
        msgDiv.textContent = text;
    }
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// --- Technical Search ---
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
            list.innerHTML = '<p class="empty-state">No matching documentation found. Try rephrasing your query with more specific terms.</p>';
        } else {
            results.forEach((res, idx) => {
                const relevanceClass = res.score >= 0.7 ? 'high' : res.score >= 0.4 ? 'medium' : 'low';
                const item = document.createElement('div');
                item.className = 'result-hex';
                item.innerHTML = `
                    <div class="source-header">
                        <span class="source-index">[${idx + 1}]</span>
                        <span class="source-file">${res.source.replace('.json', '').toUpperCase()}</span>
                        <span class="relevance-pill ${relevanceClass}">${(res.score * 100).toFixed(1)}%</span>
                    </div>
                    <div class="source-id">${res.id}</div>
                    <p style="margin-top: 0.8rem; line-height: 1.7;">${formatResponse(res.content)}</p>
                `;
                list.appendChild(item);
            });
        }
    } catch (error) {
        list.innerHTML = '<p style="color: #ff4d4d; text-align: center;">Connection error during retrieval. Please verify the server is running.</p>';
        console.error(error);
    } finally {
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}

// --- Recommendations ---
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
            list.innerHTML = '<p class="empty-state">No vehicles matched your requirements. Try describing your needs differently (e.g., towing, family, city driving).</p>';
        } else {
            // Add AI Summary if available
            if (data.summary) {
                const summaryDiv = document.createElement('div');
                summaryDiv.className = 'ai-summary-box';
                summaryDiv.innerHTML = `
                    <div class="summary-header">
                        <span class="ai-burst-icon">✨</span>
                         Professional Recommendation Analysis
                    </div>
                    <div class="summary-content">${formatResponse(data.summary)}</div>
                `;
                list.appendChild(summaryDiv);
            }

            data.recommendations.forEach((rec, idx) => {
                const relevanceClass = rec.score >= 0.7 ? 'high' : rec.score >= 0.4 ? 'medium' : 'low';
                const item = document.createElement('div');
                item.className = 'result-hex recommend-card';
                item.innerHTML = `
                    <div class="rec-header">
                        <span class="rec-rank">#${idx + 1}</span>
                        <h3 class="rec-model">${rec.model.toUpperCase()}</h3>
                        <span class="relevance-pill ${relevanceClass}">RELEVANCE: ${(rec.score * 100).toFixed(0)}%</span>
                    </div>
                    <p class="rec-reasoning">${formatResponse(rec.reasoning)}</p>
                `;
                list.appendChild(item);
            });
        }

    } catch (error) {
        list.innerHTML = '<p style="color: #ff4d4d; text-align: center;">Recommendation engine unavailable.</p>';
        console.error(error);
    } finally {
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}
