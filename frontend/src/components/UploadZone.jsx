import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export default function UploadZone({ onFileUpload, isUploading, uploadError }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      onFileUpload(file);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      onFileUpload(file);
    }
  };

  return (
    <div style={{ maxWidth: '820px', margin: '0 auto', textAlign: 'center', paddingTop: '1.5rem' }}>
      {/* Eyebrow Label */}
      <div className="eyebrow" style={{ marginBottom: '1rem' }}>
        PaperMind AI Intelligence Assistant
      </div>

      {/* Editorial Headline */}
      <h1
        className="font-serif"
        style={{
          fontSize: '3.6rem',
          fontWeight: 400,
          color: 'var(--text-main)',
          lineHeight: 1.15,
          letterSpacing: '-0.02em',
          marginBottom: '1.25rem',
        }}
      >
        Research papers, understood.
      </h1>

      {/* Subtitle */}
      <p
        style={{
          fontSize: '1.15rem',
          color: 'var(--text-secondary)',
          maxWidth: '600px',
          margin: '0 auto 2.5rem auto',
          lineHeight: 1.6,
        }}
      >
        Turn complex academic literature into structured insights, clear explanations, and meaningful conversations.
      </p>

      {/* Upload Box */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        style={{
          backgroundColor: isDragOver ? 'var(--accent-subtle)' : 'var(--bg-surface)',
          border: `2px dashed ${isDragOver ? 'var(--accent-primary)' : 'var(--border-light)'}`,
          borderRadius: 'var(--radius-xl)',
          padding: '3.5rem 2rem',
          cursor: isUploading ? 'wait' : 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: 'var(--shadow-card)',
          position: 'relative',
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf"
          style={{ display: 'none' }}
          disabled={isUploading}
        />

        {isUploading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <Loader2
              size={40}
              className="spin-animation"
              style={{ color: 'var(--accent-primary)', animation: 'spin 1s linear infinite' }}
            />
            <p style={{ fontWeight: 500, color: 'var(--text-main)' }}>
              Parsing PDF layout and computing linguistic statistics...
            </p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Extracting multi-page text via PyMuPDF
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.9rem' }}>
            <div
              style={{
                width: '54px',
                height: '54px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-subtle)',
                color: 'var(--accent-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <UploadCloud size={28} />
            </div>

            <div style={{ marginTop: '0.5rem' }}>
              <span
                style={{
                  fontWeight: 600,
                  color: 'var(--accent-primary)',
                  textDecoration: 'underline',
                  textUnderlineOffset: '3px',
                }}
              >
                Click to upload
              </span>{' '}
              <span style={{ color: 'var(--text-secondary)' }}>or drag and drop your research paper here</span>
            </div>

            <p style={{ fontSize: '0.82rem', color: 'var(--text-tertiary)' }}>
              PDF documents with selectable text up to 20 MB (arXiv, IEEE, ACM, Springer)
            </p>
          </div>
        )}
      </div>

      {/* Error Alert */}
      {uploadError && (
        <div className="alert-error" style={{ marginTop: '1.5rem', textAlign: 'left' }}>
          <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Upload Failed:</strong> {uploadError}
          </div>
        </div>
      )}

      {/* Value Proposition Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.25rem',
          marginTop: '3.5rem',
          textAlign: 'left',
        }}
      >
        <div className="card" style={{ padding: '1.35rem 1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.5rem' }}>
            <FileText size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.1rem', fontWeight: 500 }}>
              Text & Statistics
            </h3>
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Clean multi-column PDF text extraction with lexical diversity, sentence segmentation, and estimated reading time.
          </p>
        </div>

        <div className="card" style={{ padding: '1.35rem 1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.5rem' }}>
            <CheckCircle2 size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.1rem', fontWeight: 500 }}>
              Component Extraction
            </h3>
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Identifies problem statements, objectives, algorithms, benchmarks, findings, limitations, and future directions.
          </p>
        </div>

        <div className="card" style={{ padding: '1.35rem 1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.5rem' }}>
            <UploadCloud size={18} style={{ color: 'var(--accent-primary)' }} />
            <h3 className="font-serif" style={{ fontSize: '1.1rem', fontWeight: 500 }}>
              Grounded Q&A
            </h3>
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Conversational interaction strictly verified against document context without generic hallucinations.
          </p>
        </div>
      </div>
    </div>
  );
}
