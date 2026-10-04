import React, { useState } from 'react';
import { Tag, Copy, Check, Sparkles } from 'lucide-react';

export default function KeywordsTab({ analysis, onTriggerAnalysis, isAnalyzing }) {
  const [copied, setCopied] = useState(false);

  if (!analysis) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <Sparkles size={36} style={{ color: 'var(--accent-primary)', margin: '0 auto 1rem auto' }} />
        <h3 className="font-serif" style={{ fontSize: '1.65rem', marginBottom: '0.65rem', fontWeight: 500 }}>
          Keywords Not Yet Extracted
        </h3>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto 1.5rem auto' }}>
          Analyze the paper to surface domain-specific keywords and conceptual identifiers.
        </p>
        <button
          type="button"
          onClick={onTriggerAnalysis}
          disabled={isAnalyzing}
          className="btn-primary"
        >
          {isAnalyzing ? 'Extracting...' : 'Extract Keywords'}
        </button>
      </div>
    );
  }

  const keywords = analysis.keywords || [];

  const handleCopyKeywords = () => {
    if (keywords.length > 0) {
      navigator.clipboard.writeText(keywords.join(', '));
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <div style={{ maxWidth: '880px', margin: '0 auto' }}>
      <div className="card" style={{ padding: '2.25rem' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1.5rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <Tag size={18} style={{ color: 'var(--accent-primary)' }} />
              <h2 className="font-serif" style={{ fontSize: '1.65rem', fontWeight: 500, margin: 0 }}>
                Domain Research Keywords
              </h2>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: 0 }}>
              Specific technical terminology extracted from paper abstract, methodology, and experimental sections.
            </p>
          </div>

          <button
            type="button"
            onClick={handleCopyKeywords}
            className="btn-secondary"
            style={{
              fontSize: '0.84rem',
              padding: '0.5rem 1rem',
              borderColor: copied ? 'var(--success-border)' : 'var(--border-light)',
              backgroundColor: copied ? 'var(--success-bg)' : 'var(--bg-surface)',
              color: copied ? 'var(--success-text)' : 'var(--text-main)',
            }}
          >
            {copied ? <Check size={14} style={{ color: 'var(--success-text)' }} /> : <Copy size={14} />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy All Keywords'}</span>
          </button>
        </div>

        {/* Badges Container */}
        <div
          style={{
            margin: '1.75rem 0 2.25rem 0',
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.65rem',
            alignItems: 'center',
          }}
        >
          {keywords.map((kw, i) => (
            <span
              key={i}
              className="keyword-tag"
              style={{
                fontSize: '0.88rem',
                padding: '0.45rem 1rem',
                maxWidth: '100%',
                wordBreak: 'break-word',
              }}
            >
              #{kw}
            </span>
          ))}
        </div>

        <div
          style={{
            backgroundColor: 'var(--bg-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '1.35rem 1.65rem',
            border: '1px solid var(--border-light)',
          }}
        >
          <h4 style={{ fontSize: '0.94rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
            Academic Literature Search Utility
          </h4>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.65, margin: 0 }}>
            These keywords isolate the specific conceptual identifiers of the work while filtering out generic academic stop-words
            such as <em>"paper"</em>, <em>"study"</em>, or <em>"method"</em>. You can query these directly in Google Scholar,
            Semantic Scholar, or arXiv to surface baseline or companion research papers.
          </p>
        </div>
      </div>
    </div>
  );
}
