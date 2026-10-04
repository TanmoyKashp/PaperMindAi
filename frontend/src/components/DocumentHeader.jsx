import React from 'react';
import { FileText, Sparkles, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export default function DocumentHeader({
  filename,
  analysis,
  isAnalyzing,
  onAnalyze,
  isApiConfigured,
  onOpenSettings,
  analysisError,
}) {
  const displayTitle = analysis?.title || filename;

  return (
    <div style={{ marginBottom: '1.75rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <span className="eyebrow">Academic Document</span>
        <span style={{ color: 'var(--text-tertiary)' }}>•</span>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{filename}</span>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '1.5rem',
          flexWrap: 'wrap',
        }}
      >
        <h1
          className="font-serif"
          style={{
            fontSize: '2.1rem',
            fontWeight: 400,
            color: 'var(--text-main)',
            lineHeight: 1.25,
            letterSpacing: '-0.015em',
            maxWidth: '750px',
          }}
        >
          {displayTitle}
        </h1>

        {/* Action Button */}
        <div>
          {!analysis ? (
            <button
              onClick={isApiConfigured ? onAnalyze : onOpenSettings}
              disabled={isAnalyzing}
              className="btn-primary"
              style={{ fontSize: '0.92rem', padding: '0.65rem 1.35rem' }}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 size={16} className="spin-animation" style={{ animation: 'spin 1s linear infinite' }} />
                  <span>Synthesizing Components...</span>
                </>
              ) : isApiConfigured ? (
                <>
                  <Sparkles size={16} />
                  <span>Analyze Research Paper</span>
                </>
              ) : (
                <>
                  <AlertCircle size={16} />
                  <span>Configure Gemini Key to Analyze</span>
                </>
              )}
            </button>
          ) : (
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
                backgroundColor: 'var(--success-bg)',
                color: 'var(--success-text)',
                border: '1px solid var(--success-border)',
                padding: '0.45rem 0.95rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.85rem',
                fontWeight: 600,
              }}
            >
              <CheckCircle size={15} />
              <span>Analysis Synthesized</span>
            </div>
          )}
        </div>
      </div>

      {analysisError && (
        <div className="alert-error" style={{ marginTop: '1rem' }}>
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Analysis Error:</strong> {analysisError}
          </div>
        </div>
      )}
    </div>
  );
}
