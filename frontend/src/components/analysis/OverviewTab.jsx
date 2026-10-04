import React from 'react';
import { BookOpen, Target, Flag, Award, ArrowRight, Sparkles } from 'lucide-react';

export default function OverviewTab({ analysis, onTriggerAnalysis, isAnalyzing, setActiveTab }) {
  if (!analysis) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <Sparkles size={36} style={{ color: 'var(--accent-primary)', margin: '0 auto 1rem auto' }} />
        <h3 className="font-serif" style={{ fontSize: '1.65rem', marginBottom: '0.65rem', fontWeight: 500 }}>
          Research Summary Ready to Generate
        </h3>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '520px', margin: '0 auto 1.75rem auto' }}>
          Trigger Gemini analysis to extract the core problem statement, research objectives, contributions, and findings.
        </p>
        <button
          type="button"
          onClick={onTriggerAnalysis}
          disabled={isAnalyzing}
          className="btn-primary"
          style={{ margin: '0 auto' }}
        >
          {isAnalyzing ? 'Extracting Insights...' : 'Generate Research Overview'}
        </button>
      </div>
    );
  }

  const { summary, problem_statement } = analysis;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Executive Overview Card */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid var(--accent-primary)',
          backgroundColor: 'var(--bg-surface)',
          padding: '2rem 2.25rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
          <BookOpen size={18} style={{ color: 'var(--accent-primary)' }} />
          <span className="eyebrow">Executive Summary</span>
        </div>
        <p
          style={{
            fontSize: '1.08rem',
            lineHeight: 1.75,
            color: 'var(--text-main)',
            maxWidth: '75ch', // Comfortable typographic line length
            margin: 0,
          }}
        >
          {summary?.overview || 'Not explicitly stated in the paper.'}
        </p>
      </div>

      {/* Problem Statement & Conclusion Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.5rem',
        }}
      >
        {/* Problem Statement */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <Target size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500, margin: 0 }}>
              Problem Statement
            </h3>
          </div>
          <p style={{ color: 'var(--text-main)', lineHeight: 1.65, fontSize: '0.94rem', margin: 0 }}>
            {problem_statement || 'Not explicitly stated in the paper.'}
          </p>
        </div>

        {/* Conclusion */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <Flag size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500, margin: 0 }}>
              Concluding Takeaway
            </h3>
          </div>
          <p style={{ color: 'var(--text-main)', lineHeight: 1.65, fontSize: '0.94rem', margin: 0 }}>
            {summary?.conclusion || 'Not explicitly stated in the paper.'}
          </p>
        </div>
      </div>

      {/* Core Contributions */}
      <div className="card" style={{ padding: '2rem 2.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <Award size={18} style={{ color: 'var(--accent-primary)' }} />
          <h3 className="font-serif" style={{ fontSize: '1.35rem', fontWeight: 500, margin: 0 }}>
            Core Scientific & Technical Contributions
          </h3>
        </div>

        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {(summary?.contributions || []).map((contrib, idx) => (
            <li
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.85rem',
                padding: '0.75rem 0',
                borderBottom:
                  idx < (summary?.contributions?.length || 1) - 1 ? '1px solid var(--border-subtle)' : 'none',
              }}
            >
              <span
                style={{
                  color: 'var(--accent-primary)',
                  fontWeight: 700,
                  fontSize: '0.88rem',
                  lineHeight: '1.5rem',
                  flexShrink: 0,
                }}
              >
                0{idx + 1}.
              </span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-main)', lineHeight: 1.65 }}>
                {contrib}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Next Steps Prompt */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-subtle)',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-lg)',
          padding: '1.35rem 1.75rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h4 className="font-serif" style={{ fontSize: '1.1rem', marginBottom: '0.25rem', fontWeight: 500 }}>
            Explore full methodology & benchmarks
          </h4>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', margin: 0 }}>
            Inspect detailed architectural workflows, algorithm hyperparameters, and limitations.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setActiveTab('analysis')}
          className="btn-outline-terracotta"
        >
          <span>View Research Components</span>
          <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
}
