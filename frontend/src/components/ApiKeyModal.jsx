import React, { useState } from 'react';
import { X, Key, CheckCircle2, AlertCircle, Loader2, ExternalLink } from 'lucide-react';

export default function ApiKeyModal({ isOpen, onClose, isConfigured, onSaveKey }) {
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    if (!apiKeyInput.trim()) return;

    setIsTesting(true);
    setTestResult(null);

    const res = await onSaveKey(apiKeyInput.trim());
    setIsTesting(false);
    setTestResult(res);
  };

  const handleTestExisting = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const response = await fetch('/api/config/test-connection', { method: 'POST' });
      const data = await response.json();
      setTestResult(data);
    } catch (err) {
      setTestResult({ success: false, message: err.message || 'Connection failed' });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Key size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.35rem', fontWeight: 500 }}>
              Gemini API Setup
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-tertiary)',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Status Indicator */}
        <div
          style={{
            backgroundColor: isConfigured ? 'var(--success-bg)' : 'var(--bg-subtle)',
            border: `1px solid ${isConfigured ? 'var(--success-border)' : 'var(--border-light)'}`,
            borderRadius: 'var(--radius-md)',
            padding: '0.85rem 1rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {isConfigured ? (
              <CheckCircle2 size={16} style={{ color: 'var(--success-text)' }} />
            ) : (
              <AlertCircle size={16} style={{ color: 'var(--accent-primary)' }} />
            )}
            <span style={{ fontSize: '0.86rem', fontWeight: 500, color: 'var(--text-main)' }}>
              {isConfigured ? 'API Key Detected & Configured' : 'No API Key Configured'}
            </span>
          </div>

          {isConfigured && (
            <button
              onClick={handleTestExisting}
              disabled={isTesting}
              className="btn-secondary"
              style={{ fontSize: '0.78rem', padding: '0.25rem 0.65rem' }}
            >
              {isTesting ? 'Testing...' : 'Test Connection'}
            </button>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSave}>
          <label
            style={{
              display: 'block',
              fontSize: '0.84rem',
              fontWeight: 600,
              color: 'var(--text-main)',
              marginBottom: '0.4rem',
            }}
          >
            Enter Google Gemini API Key
          </label>
          <input
            type="password"
            value={apiKeyInput}
            onChange={(e) => setApiKeyInput(e.target.value)}
            placeholder="AIzaSy..."
            style={{
              width: '100%',
              padding: '0.65rem 0.85rem',
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-light)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.9rem',
              color: 'var(--text-main)',
              outline: 'none',
              marginBottom: '0.75rem',
            }}
          />

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1.25rem',
            }}
          >
            <a
              href="https://aistudio.google.com/"
              target="_blank"
              rel="noreferrer"
              style={{
                fontSize: '0.8rem',
                color: 'var(--accent-primary)',
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
              }}
            >
              <span>Get API key from Google AI Studio</span>
              <ExternalLink size={12} />
            </a>
          </div>

          {/* Test Feedback */}
          {testResult && (
            <div
              className={testResult.success ? 'alert-success' : 'alert-error'}
              style={{ marginBottom: '1.25rem', fontSize: '0.84rem' }}
            >
              {testResult.message}
            </div>
          )}

          {/* Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.65rem' }}>
            <button type="button" onClick={onClose} className="btn-secondary">
              Close
            </button>
            <button
              type="submit"
              disabled={!apiKeyInput.trim() || isTesting}
              className="btn-primary"
            >
              {isTesting ? (
                <>
                  <Loader2 size={14} className="spin-animation" style={{ animation: 'spin 1s linear infinite' }} />
                  <span>Validating...</span>
                </>
              ) : (
                'Save & Verify'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
