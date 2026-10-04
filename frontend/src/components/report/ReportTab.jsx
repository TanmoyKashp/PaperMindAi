import React from 'react';
import { Download, FileText, CheckCircle2, Sparkles, Code2 } from 'lucide-react';
import { getReportDownloadUrl } from '../../services/api';

export default function ReportTab({ docId, analysis, filename, onTriggerAnalysis, isAnalyzing }) {
  if (!analysis) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
        <Sparkles size={36} style={{ color: 'var(--accent-primary)', margin: '0 auto 1rem auto' }} />
        <h3 className="font-serif" style={{ fontSize: '1.65rem', marginBottom: '0.65rem', fontWeight: 500 }}>
          Report Requires Completed Analysis
        </h3>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto 1.5rem auto' }}>
          Please generate the AI research analysis first before downloading the synthesized Markdown report.
        </p>
        <button
          type="button"
          onClick={onTriggerAnalysis}
          disabled={isAnalyzing}
          className="btn-primary"
        >
          {isAnalyzing ? 'Extracting...' : 'Analyze Paper First'}
        </button>
      </div>
    );
  }

  const downloadUrl = getReportDownloadUrl(docId);

  return (
    <div style={{ maxWidth: '880px', margin: '0 auto' }}>
      <div className="card" style={{ padding: '2.25rem' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1.75rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <FileText size={18} style={{ color: 'var(--accent-primary)' }} />
              <h2 className="font-serif" style={{ fontSize: '1.65rem', fontWeight: 500, margin: 0 }}>
                Academic Markdown Report
              </h2>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: 0 }}>
              Export a publication-grade Markdown document containing the complete research findings and metrics.
            </p>
          </div>

          <a
            href={downloadUrl}
            download
            className="btn-primary"
            style={{ textDecoration: 'none', padding: '0.65rem 1.35rem', fontSize: '0.92rem' }}
          >
            <Download size={16} />
            <span>Download Report (.md)</span>
          </a>
        </div>

        {/* Content Summary Card */}
        <div
          style={{
            backgroundColor: 'var(--bg-subtle)',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-md)',
            padding: '1.35rem 1.65rem',
            marginBottom: '1.75rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <CheckCircle2 size={16} style={{ color: 'var(--accent-primary)' }} />
            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Verified Document-Specific Analysis
            </span>
          </div>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.65, margin: 0 }}>
            The downloaded report includes: Document Metadata & NLP Metrics, Executive Summary & Conclusions, Problem Statement & Objectives, Methodology & Architecture, Datasets & Quantitative Findings, Limitations & Future Scope, and Filtered Keywords.
          </p>
        </div>

        {/* Formatted Preview Box */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.65rem' }}>
            <Code2 size={15} style={{ color: 'var(--accent-primary)' }} />
            <span className="eyebrow">Markdown Structure Preview</span>
          </div>
          <div
            style={{
              backgroundColor: '#1E1E1E',
              color: '#D4D4D4',
              borderRadius: 'var(--radius-md)',
              padding: '1.35rem 1.65rem',
              fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
              fontSize: '0.84rem',
              lineHeight: 1.6,
              overflowX: 'auto',
              maxHeight: '320px',
              overflowY: 'auto',
            }}
          >
            <pre style={{ margin: 0 }}>
{`# PaperMind AI — Academic Research Analysis Report

> **Source File:** \`${filename}\`
> **System:** PaperMind AI (Powered by Google Gemini & PyMuPDF)

## 1. Document Identity & Overview
**Paper Title:** ${analysis.title}

## 2. Research Summary
### High-Level Overview
${analysis.summary?.overview || ''}

### Core Contributions
${(analysis.summary?.contributions || []).map(c => `- ${c}`).join('\n')}

### Conclusion
${analysis.summary?.conclusion || ''}

## 3. Problem Statement & Research Objectives
### Problem Statement
${analysis.problem_statement}

### Research Objectives
${(analysis.research_objectives || []).map(o => `- ${o}`).join('\n')}

## 4. Methodology & Technical Architecture
### Proposed Framework
${analysis.methodology}

### Algorithms & Models
${(analysis.algorithms_models || []).map(a => `- ${a}`).join('\n')}

## 5. Experimental Results & Findings
${(analysis.key_findings || []).map(f => `- ${f}`).join('\n')}

## 6. Critical Evaluation: Limitations & Future Scope
### Acknowledged Limitations
${(analysis.limitations || []).map(l => `- ${l}`).join('\n')}

### Proposed Future Directions
${(analysis.future_scope || []).map(d => `- ${d}`).join('\n')}

## 7. Extracted Research Keywords
${(analysis.keywords || []).map(k => `\`${k}\``).join(', ')}
`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
