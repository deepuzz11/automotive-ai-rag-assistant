import { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, Car, Sparkles, Loader2, Send, Search, 
  HelpCircle, Settings, ChevronRight, FileText
} from 'lucide-react';
import './index.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('assistant');
  
  // Assistant State
  const [askQuestion, setAskQuestion] = useState('');
  const [askLoading, setAskLoading] = useState(false);
  const [askResult, setAskResult] = useState(null);
  
  // Recommender State
  const [recNeeds, setRecNeeds] = useState('');
  const [recLoading, setRecLoading] = useState(false);
  const [recResult, setRecResult] = useState(null);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!askQuestion.trim()) return;
    
    setAskLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, {
        question: askQuestion
      });
      setAskResult(response.data);
    } catch (error) {
      console.error("Ask error:", error);
      setAskResult({ error: "System Error: Unable to reach AI Engine. Backend offline." });
    } finally {
      setAskLoading(false);
    }
  };

  const handleRecommend = async (e) => {
    e.preventDefault();
    if (!recNeeds.trim()) return;
    
    setRecLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/recommend`, {
        needs: recNeeds
      });
      setRecResult(response.data.recommendations);
    } catch (error) {
      console.error("Recommend error:", error);
      setRecResult({ error: "System Error: Matchmaking Engine unavailable." });
    } finally {
      setRecLoading(false);
    }
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar Navigation */}
      <motion.aside 
        className="sidebar"
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        transition={{ type: "spring", stiffness: 100, damping: 20 }}
      >
        <div className="brand-header">
          <div className="brand-logo-container">
            <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>F</span>
          </div>
          <h1>Ford AI Engine</h1>
        </div>
        
        <nav className="nav-menu">
          <div 
            className={`nav-item ${activeTab === 'assistant' ? 'active' : ''}`}
            onClick={() => setActiveTab('assistant')}
          >
            <MessageSquare size={20} />
            <span>Knowledge Base</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'recommender' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommender')}
          >
            <Car size={20} />
            <span>Vehicle Matchmaker</span>
          </div>
          <div className="nav-item opacity-50" style={{ cursor: 'not-allowed', marginTop: '2rem' }}>
            <FileText size={20} />
            <span>System Logs</span>
          </div>
          <div className="nav-item opacity-50" style={{ cursor: 'not-allowed' }}>
            <Settings size={20} />
            <span>Settings</span>
          </div>
        </nav>
        
        <div style={{ marginTop: 'auto', color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
          Ford Motor Company &copy; 2026<br/>
          Internal AI Tool v1.0.0
        </div>
      </motion.aside>

      {/* Main Workspace Area */}
      <main className="main-area">
        <header className="header-banner">
          <motion.h2
            key={activeTab} // triggers animation on tab switch
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {activeTab === 'assistant' ? 'Vehicle Knowledge Assistant' : 'Intelligent Matchmaker'}
          </motion.h2>
          <motion.p
            key={`p-${activeTab}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            {activeTab === 'assistant' 
              ? 'Query the internal vector database for RAG-augmented insights.' 
              : 'Analyze conversational requirements to recommend the optimal Ford model.'}
          </motion.p>
        </header>

        <div className="view-container">
          <AnimatePresence mode="wait">
            {/* --- ASSISTANT TAB --- */}
            {activeTab === 'assistant' && (
              <motion.div
                key="assistant-view"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
                className="glass-panel"
                style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
              >
                <form onSubmit={handleAsk} style={{ marginBottom: askResult ? '2rem' : '0' }}>
                  <div className="ai-input-wrapper">
                    <textarea 
                      className="ai-input" 
                      placeholder="Ask the AI about Ford specs, towing capacity, or maintenance..."
                      value={askQuestion}
                      onChange={(e) => setAskQuestion(e.target.value)}
                      disabled={askLoading}
                    />
                    <button type="submit" className="submit-btn" disabled={askLoading || !askQuestion.trim()}>
                      {askLoading ? <Loader2 className="spinner-icon" size={20} /> : <Send size={20} />}
                    </button>
                  </div>
                </form>

                <AnimatePresence>
                  {askLoading && (
                    <motion.div 
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      className="loading-indicator"
                    >
                      <Loader2 size={24} className="spinner-icon" />
                      <span>Synthesizing answer via RAG inference...</span>
                    </motion.div>
                  )}
                  
                  {askResult && !askLoading && !askResult.error && (
                    <motion.div 
                      className="result-display fade-in"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--ford-blue-light)', fontWeight: 'bold' }}>
                        <Sparkles size={20} /> AI Synthesis
                      </div>
                      <div style={{ whiteSpace: 'pre-wrap', marginBottom: '1.5rem' }}>
                        {askResult.answer}
                      </div>
                      
                      {askResult.context_used?.length > 0 && (
                        <div style={{ paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem' }}>
                            Retrieved Sources ({askResult.context_used.length})
                          </span>
                          <div>
                            {askResult.context_used.map((src, i) => (
                              <span key={i} className="context-tag">
                                <FileText size={12} /> {src.source}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}
                  
                  {askResult?.error && (
                    <div style={{ color: 'var(--danger)', marginTop: '1rem', padding: '1rem', background: 'rgba(229, 62, 62, 0.1)', borderRadius: '8px' }}>
                      {askResult.error}
                    </div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

            {/* --- RECOMMENDER TAB --- */}
            {activeTab === 'recommender' && (
              <motion.div
                key="recommender-view"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
                className="glass-panel"
                style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
              >
                <form onSubmit={handleRecommend} style={{ marginBottom: recResult ? '2rem' : '0' }}>
                  <div className="ai-input-wrapper">
                    <textarea 
                      className="ai-input" 
                      placeholder="Describe the customer's exact needs, family size, budget constraints, or usage scenarios..."
                      value={recNeeds}
                      onChange={(e) => setRecNeeds(e.target.value)}
                      disabled={recLoading}
                    />
                    <button type="submit" className="submit-btn" disabled={recLoading || !recNeeds.trim()}>
                      {recLoading ? <Loader2 className="spinner-icon" size={20} /> : <Search size={20} />}
                    </button>
                  </div>
                </form>

                <AnimatePresence>
                  {recLoading && (
                    <motion.div 
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      className="loading-indicator"
                    >
                      <Loader2 size={24} className="spinner-icon" />
                      <span>Computing best matches...</span>
                    </motion.div>
                  )}
                  
                  {recResult && Array.isArray(recResult) && !recLoading && (
                     <div style={{ marginTop: '1rem' }}>
                       <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-muted)', fontSize: '1rem' }}>
                         System Recommendations ({recResult.length} Results)
                       </h3>
                       <div>
                        {recResult.map((rec, i) => (
                          <motion.div 
                            key={i}
                            className="vehicle-card"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                          >
                            <div className="vehicle-header">
                              <span className="vehicle-name">
                                <ChevronRight size={20} color="var(--ford-blue-light)" /> {rec.model}
                              </span>
                              <span className="match-badge">Recommended</span>
                            </div>
                            <div className="vehicle-reasoning">
                              {rec.reasoning}
                            </div>
                          </motion.div>
                        ))}
                        {recResult.length === 0 && (
                          <div style={{ color: 'var(--text-muted)' }}>No matches found for criteria.</div>
                        )}
                       </div>
                     </div>
                  )}
                  
                  {recResult?.error && (
                    <div style={{ color: 'var(--danger)', marginTop: '1rem', padding: '1rem', background: 'rgba(229, 62, 62, 0.1)', borderRadius: '8px' }}>
                      {recResult.error}
                    </div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
