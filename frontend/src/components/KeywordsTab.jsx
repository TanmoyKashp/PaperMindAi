import React, { useState } from 'react';
import { Tag, Copy, Check, Sparkles } from 'lucide-react';

export default function KeywordsTab({ analysis, onTriggerAnalysis, isAnalyzing }) {
  const [copied, setCopied] = useState(false);

  if (!analysis) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <Sparkles size={36} style={{ color: 'var(--accent-primary)', margin: '0 auto 1rem auto' }} />
        <h3 className="font-serif" style={{ fontSize: '1.65rem', marginBottom: '0.65rem' }}>
          Keywords Not Yet Extracted
        </h3>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto 1.5rem auto' }}>
          Analyze the paper to surface domain-specific keywords and conceptual identifiers.
        </p>
        <button onClick={onTriggerAnalysis} disabled={isAnalyzing} className="btn-primary">
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
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div style={{ maxWidth: '850px', margin: '0 auto' }}>
      <div className="card" style={{ padding: '2rem 2.25rem' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1.25rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <Tag size={18} style={{ color: 'var(--accent-primary)' }} />
              <h2 className="font-serif" style={{ fontSize: '1.6rem', fontWeight: 500 }}>
                Domain Research Keywords
              </h2>
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              Context-specific technical terminology extracted from paper abstract, methodology, and experimental sections.
            </p>
          </div>

          <button
            onClick={handleCopyKeywords}
            className="btn-secondary"
            style={{ fontSize: '0.82rem', padding: '0.45rem 0.85rem' }}
          >
            {copied ? <Check size={14} style={{ color: 'var(--success-text)' }} /> : <Copy size={14} />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy All'}</span>
          </button>
        </div>

        {/* Badges Container */}
        <div style={{ margin: '1.5rem 0 2rem 0', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {keywords.map((kw, i) => (
            <span key={i} className="keyword-tag">
              #{kw}
            </span>
          ))}
        </div>

        <div
          style={{
            backgroundColor: 'var(--bg-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem 1.5rem',
            border: '1px solid var(--border-light)',
          }}
        >
          <h4 style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
            Academic Indexing Value
          </h4>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            These terms isolate the novel concepts introduced by the authors while omitting generic stopwords
            like <em>"paper"</em>, <em>"study"</em>, or <em>"method"</em>. You can use these keywords directly in Google Scholar,
            Semantic Scholar, or arXiv to discover related baseline literature.
          </p>
        </div>
      </div>
    </div>
  );
}
