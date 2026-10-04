import React, { useState } from 'react';
import { 
  FileText, 
  Sparkles, 
  MessageSquare, 
  Download, 
  Key, 
  RotateCcw,
  BookOpen,
  Tag,
  Menu,
  X,
  CheckCircle2
} from 'lucide-react';

export default function AppHeader({
  activeTab,
  setActiveTab,
  docData,
  onResetDoc,
  isApiConfigured,
  onOpenSettings,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleTabSelect = (tab) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <header className="top-nav">
      <div className="nav-container">
        {/* Brand Wordmark */}
        <div 
          className="brand-wrap" 
          onClick={() => handleTabSelect('overview')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && handleTabSelect('overview')}
        >
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--accent-subtle)',
              border: '1px solid var(--accent-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)',
            }}
          >
            <FileText size={18} />
          </div>
          <span className="brand-name">PaperMind AI</span>
          <span className="brand-badge">Assistant</span>
        </div>

        {/* Desktop Navigation Links (Only shown when document is loaded) */}
        {docData && (
          <nav className="nav-links" aria-label="Main Navigation">
            <button
              type="button"
              onClick={() => handleTabSelect('overview')}
              className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
            >
              <BookOpen size={15} />
              <span>Overview</span>
            </button>
            <button
              type="button"
              onClick={() => handleTabSelect('analysis')}
              className={`nav-btn ${activeTab === 'analysis' ? 'active' : ''}`}
            >
              <Sparkles size={15} />
              <span>Analysis</span>
            </button>
            <button
              type="button"
              onClick={() => handleTabSelect('keywords')}
              className={`nav-btn ${activeTab === 'keywords' ? 'active' : ''}`}
            >
              <Tag size={15} />
              <span>Keywords</span>
            </button>
            <button
              type="button"
              onClick={() => handleTabSelect('chat')}
              className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
            >
              <MessageSquare size={15} />
              <span>Ask Paper</span>
            </button>
            <button
              type="button"
              onClick={() => handleTabSelect('report')}
              className={`nav-btn ${activeTab === 'report' ? 'active' : ''}`}
            >
              <Download size={15} />
              <span>Report</span>
            </button>
          </nav>
        )}

        {/* Right Actions */}
        <div className="nav-actions">
          {/* Document Reset / Change Paper */}
          {docData && (
            <button
              type="button"
              onClick={onResetDoc}
              className="btn-secondary"
              title="Close current document and upload a new paper"
              style={{ padding: '0.45rem 0.85rem', fontSize: '0.82rem' }}
            >
              <RotateCcw size={14} />
              <span>Change Paper</span>
            </button>
          )}

          {/* API Key Status / Configuration Trigger */}
          <button
            type="button"
            onClick={onOpenSettings}
            className={`btn-secondary ${!isApiConfigured ? 'alert-missing-key' : ''}`}
            style={{
              padding: '0.45rem 0.85rem',
              fontSize: '0.82rem',
              borderColor: isApiConfigured ? 'var(--border-light)' : 'var(--accent-primary)',
              color: isApiConfigured ? 'var(--text-main)' : 'var(--accent-primary)',
              backgroundColor: isApiConfigured ? 'var(--bg-surface)' : 'var(--accent-subtle)',
            }}
            title={isApiConfigured ? 'Gemini API Connected' : 'Set Gemini API Key'}
          >
            {isApiConfigured ? (
              <CheckCircle2 size={14} style={{ color: 'var(--success-text)' }} />
            ) : (
              <Key size={14} />
            )}
            <span>{isApiConfigured ? 'API Connected' : 'Set Gemini Key'}</span>
          </button>

          {/* Mobile Menu Hamburger Toggle (Only when doc is active) */}
          {docData && (
            <button
              type="button"
              className="mobile-menu-btn"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-light)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.4rem',
                cursor: 'pointer',
                display: 'none', // Handled via CSS media query
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--text-main)',
              }}
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          )}
        </div>
      </div>

      {/* Mobile Navigation Dropdown Drawer */}
      {docData && mobileMenuOpen && (
        <div
          className="mobile-nav-drawer"
          style={{
            backgroundColor: 'var(--bg-surface)',
            borderTop: '1px solid var(--border-light)',
            padding: '1rem 1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
          }}
        >
          <button
            type="button"
            onClick={() => handleTabSelect('overview')}
            className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
            style={{ justifyContent: 'flex-start', width: '100%', padding: '0.65rem 1rem' }}
          >
            <BookOpen size={16} />
            <span>Document Overview</span>
          </button>
          <button
            type="button"
            onClick={() => handleTabSelect('analysis')}
            className={`nav-btn ${activeTab === 'analysis' ? 'active' : ''}`}
            style={{ justifyContent: 'flex-start', width: '100%', padding: '0.65rem 1rem' }}
          >
            <Sparkles size={16} />
            <span>Research Analysis</span>
          </button>
          <button
            type="button"
            onClick={() => handleTabSelect('keywords')}
            className={`nav-btn ${activeTab === 'keywords' ? 'active' : ''}`}
            style={{ justifyContent: 'flex-start', width: '100%', padding: '0.65rem 1rem' }}
          >
            <Tag size={16} />
            <span>Domain Keywords</span>
          </button>
          <button
            type="button"
            onClick={() => handleTabSelect('chat')}
            className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
            style={{ justifyContent: 'flex-start', width: '100%', padding: '0.65rem 1rem' }}
          >
            <MessageSquare size={16} />
            <span>Ask Your Paper</span>
          </button>
          <button
            type="button"
            onClick={() => handleTabSelect('report')}
            className={`nav-btn ${activeTab === 'report' ? 'active' : ''}`}
            style={{ justifyContent: 'flex-start', width: '100%', padding: '0.65rem 1rem' }}
          >
            <Download size={16} />
            <span>Export Report</span>
          </button>
        </div>
      )}
    </header>
  );
}
