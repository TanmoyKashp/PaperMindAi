import React from 'react';
import { Layers, FileText, AlignLeft, Hash, Clock } from 'lucide-react';

export default function MetricsRow({ pageCount, stats, totalWords }) {
  const wordCount = stats?.word_count ?? totalWords ?? 0;
  const sentenceCount = stats?.sentence_count ?? 0;
  const vocabSize = stats?.vocabulary_size ?? 0;
  const readingTime = stats?.estimated_reading_time_minutes ?? 0;

  return (
    <div className="metric-grid">
      <div className="metric-item">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="metric-label">Pages</div>
          <Layers size={14} style={{ color: 'var(--text-tertiary)' }} />
        </div>
        <div className="metric-value">{pageCount}</div>
      </div>

      <div className="metric-item">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="metric-label">Word Count</div>
          <FileText size={14} style={{ color: 'var(--text-tertiary)' }} />
        </div>
        <div className="metric-value">{wordCount.toLocaleString()}</div>
      </div>

      <div className="metric-item">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="metric-label">Sentences</div>
          <AlignLeft size={14} style={{ color: 'var(--text-tertiary)' }} />
        </div>
        <div className="metric-value">{sentenceCount > 0 ? sentenceCount.toLocaleString() : '—'}</div>
      </div>

      <div className="metric-item">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="metric-label">Unique Vocab</div>
          <Hash size={14} style={{ color: 'var(--text-tertiary)' }} />
        </div>
        <div className="metric-value">{vocabSize > 0 ? vocabSize.toLocaleString() : '—'}</div>
      </div>

      <div className="metric-item">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="metric-label">Est. Read Time</div>
          <Clock size={14} style={{ color: 'var(--text-tertiary)' }} />
        </div>
        <div className="metric-value">~{readingTime} min</div>
      </div>
    </div>
  );
}
