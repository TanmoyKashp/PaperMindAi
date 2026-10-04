import React from 'react';
import { 
  Crosshair, 
  Workflow, 
  Cpu, 
  Database, 
  TrendingUp, 
  AlertTriangle, 
  Compass,
  Sparkles
} from 'lucide-react';

export default function AnalysisTab({ analysis, onTriggerAnalysis, isAnalyzing }) {
  if (!analysis) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <Sparkles size={36} style={{ color: 'var(--accent-primary)', margin: '0 auto 1rem auto' }} />
        <h3 className="font-serif" style={{ fontSize: '1.65rem', marginBottom: '0.65rem' }}>
          Detailed Components Not Yet Extracted
        </h3>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto 1.5rem auto' }}>
          Run the analysis to view objectives, algorithms, benchmarks, findings, limitations, and future scope.
        </p>
        <button onClick={onTriggerAnalysis} disabled={isAnalyzing} className="btn-primary">
          {isAnalyzing ? 'Extracting...' : 'Analyze Research Paper'}
        </button>
      </div>
    );
  }

  const {
    research_objectives = [],
    methodology,
    algorithms_models = [],
    datasets,
    key_findings = [],
    limitations = [],
    future_scope = [],
  } = analysis;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.75rem' }}>
      {/* Column 1: Objectives, Methodology, Algorithms */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
        {/* Research Objectives */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <Crosshair size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500 }}>
              Research Objectives
            </h3>
          </div>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {research_objectives.map((obj, i) => (
              <li key={i} style={{ display: 'flex', gap: '0.6rem', marginBottom: '0.65rem', fontSize: '0.94rem', lineHeight: 1.6 }}>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>•</span>
                <span>{obj}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Methodology */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <Workflow size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500 }}>
              Proposed Methodology
            </h3>
          </div>
          <p style={{ fontSize: '0.94rem', lineHeight: 1.7, color: 'var(--text-main)' }}>
            {methodology || 'Not explicitly stated in the paper.'}
          </p>
        </div>

        {/* Algorithms & Models */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <Cpu size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500 }}>
              Algorithms & Models Employed
            </h3>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem' }}>
            {algorithms_models.map((algo, i) => (
              <span
                key={i}
                style={{
                  backgroundColor: 'var(--bg-muted)',
                  border: '1px solid var(--border-light)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.35rem 0.65rem',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  color: 'var(--text-main)',
                }}
              >
                {algo}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Column 2: Datasets, Findings, Limitations, Future Directions */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
        {/* Datasets & Benchmarks */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <Database size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500 }}>
              Datasets & Benchmarks
            </h3>
          </div>
          {Array.isArray(datasets) ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {datasets.map((ds, i) => (
                <li key={i} style={{ display: 'flex', gap: '0.6rem', marginBottom: '0.5rem', fontSize: '0.94rem' }}>
                  <span style={{ color: 'var(--accent-primary)' }}>•</span>
                  <span>{ds}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ fontSize: '0.94rem', lineHeight: 1.6, color: 'var(--text-main)' }}>
              {datasets || 'Not explicitly stated in the paper.'}
            </p>
          )}
        </div>

        {/* Key Findings */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <TrendingUp size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500 }}>
              Key Findings & Experimental Results
            </h3>
          </div>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {key_findings.map((f, i) => (
              <li key={i} style={{ display: 'flex', gap: '0.6rem', marginBottom: '0.65rem', fontSize: '0.94rem', lineHeight: 1.6 }}>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>•</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Limitations & Future Scope */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <AlertTriangle size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500 }}>
              Acknowledged Limitations
            </h3>
          </div>
          <ul style={{ listStyle: 'none', padding: 0, marginBottom: '1.5rem' }}>
            {limitations.map((lim, i) => (
              <li key={i} style={{ display: 'flex', gap: '0.6rem', marginBottom: '0.5rem', fontSize: '0.92rem', color: 'var(--text-secondary)' }}>
                <span style={{ color: 'var(--accent-primary)' }}>•</span>
                <span>{lim}</span>
              </li>
            ))}
          </ul>

          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
              <Compass size={18} style={{ color: 'var(--accent-primary)' }} />
              <h3 className="font-serif" style={{ fontSize: '1.25rem', fontWeight: 500 }}>
                Future Research Directions
              </h3>
            </div>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {future_scope.map((fut, i) => (
                <li key={i} style={{ display: 'flex', gap: '0.6rem', marginBottom: '0.5rem', fontSize: '0.92rem', color: 'var(--text-secondary)' }}>
                  <span style={{ color: 'var(--accent-primary)' }}>•</span>
                  <span>{fut}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
