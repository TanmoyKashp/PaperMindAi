import React from 'react';
import { 
  FileText, 
  Sparkles, 
  MessageSquare, 
  Download, 
  Key, 
  RotateCcw,
  BookOpen,
  Tag
} from 'lucide-react';

export default function AppHeader({
  activeTab,
  setActiveTab,
  docData,
  onResetDoc,
  isApiConfigured,
  onOpenSettings,
}) {
  return (
    <header className="top-nav">
      <div className="nav-container">
        {/* Brand */}
        <div className="brand-wrap" onClick={() => setActiveTab('overview')}>
          <FileText className="brand-logo-icon" />
          <span className="brand-name">PaperMind AI</span>
          <span className="brand-badge">Research</span>
        </div>

        {/* Navigation Tabs (Only visible when document is loaded) */}
        {docData && (
          <nav className="nav-links">
            <button
              onClick={() => setActiveTab('overview')}
              className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
            >
              <BookOpen size={16} />
              <span>Overview</span>
            </button>
            <button
              onClick={() => setActiveTab('analysis')}
              className={`nav-btn ${activeTab === 'analysis' ? 'active' : ''}`}
            >
              <Sparkles size={16} />
              <span>Analysis</span>
            </button>
            <button
              onClick={() => setActiveTab('keywords')}
              className={`nav-btn ${activeTab === 'keywords' ? 'active' : ''}`}
            >
              <Tag size={16} />
              <span>Keywords</span>
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
            >
              <MessageSquare size={16} />
              <span>Ask Paper</span>
            </button>
            <button
              onClick={() => setActiveTab('report')}
              className={`nav-btn ${activeTab === 'report' ? 'active' : ''}`}
            >
              <Download size={16} />
              <span>Report</span>
            </button>
          </nav>
        )}

        {/* Right Action Items */}
        <div className="nav-actions">
          {/* Document Reset Button */}
          {docData && (
            <button
              onClick={onResetDoc}
              className="btn-secondary"
              title="Close current paper and upload another"
              style={{ padding: '0.45rem 0.85rem', fontSize: '0.82rem' }}
            >
              <RotateCcw size={14} />
              <span>Change Paper</span>
            </button>
          )}

          {/* API Key Status / Trigger */}
          <button
            onClick={onOpenSettings}
            className={`btn-secondary ${!isApiConfigured ? 'alert-missing-key' : ''}`}
            style={{
              padding: '0.45rem 0.85rem',
              fontSize: '0.82rem',
              borderColor: isApiConfigured ? 'var(--border-light)' : 'var(--accent-primary)',
              color: isApiConfigured ? 'var(--text-main)' : 'var(--accent-primary)',
            }}
          >
            <Key size={14} />
            <span>{isApiConfigured ? 'API Connected' : 'Set Gemini Key'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
