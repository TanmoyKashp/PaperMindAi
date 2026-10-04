import React from 'react';
import { Sparkles, CheckCircle2, AlertCircle, Loader2, RotateCcw } from 'lucide-react';

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
        <span style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>{filename}</span>
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
            fontSize: '2.15rem',
            fontWeight: 400,
            color: 'var(--text-main)',
            lineHeight: 1.25,
            letterSpacing: '-0.015em',
            maxWidth: '780px',
            margin: 0,
          }}
        >
          {displayTitle}
        </h1>

        {/* Action Trigger */}
        <div style={{ flexShrink: 0 }}>
          {!analysis ? (
            <button
              type="button"
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
                  {analysisError ? <RotateCcw size={16} /> : <Sparkles size={16} />}
                  <span>{analysisError ? 'Retry Analysis' : 'Analyze Research Paper'}</span>
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
                padding: '0.5rem 1rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.86rem',
                fontWeight: 600,
              }}
            >
              <CheckCircle2 size={15} />
              <span>Analysis Synthesized</span>
            </div>
          )}
        </div>
      </div>

      {analysisError && (
        <div
          className="alert-error"
          style={{
            marginTop: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            flexWrap: 'wrap',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.65rem', flex: 1, minWidth: '240px' }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Analysis Notice:</strong> {analysisError}
            </div>
          </div>
          {isApiConfigured && (
            <button
              type="button"
              onClick={onAnalyze}
              disabled={isAnalyzing}
              className="btn-secondary"
              style={{
                fontSize: '0.84rem',
                padding: '0.45rem 0.95rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                flexShrink: 0,
                backgroundColor: '#ffffff',
              }}
            >
              <RotateCcw size={14} />
              <span>Retry Analysis</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
