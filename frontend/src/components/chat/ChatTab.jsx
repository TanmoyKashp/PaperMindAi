import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Loader2, Sparkles, HelpCircle } from 'lucide-react';
import ChatMessage from './ChatMessage';

export default function ChatTab({
  chatHistory = [],
  onSendMessage,
  onClearChat,
  isSending,
  isApiConfigured,
  onOpenSettings,
}) {
  const [inputQuestion, setInputQuestion] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isSending]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (inputQuestion.trim() && !isSending && isApiConfigured) {
      onSendMessage(inputQuestion.trim());
      setInputQuestion('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestedClick = (text) => {
    if (!isSending && isApiConfigured) {
      onSendMessage(text);
    }
  };

  return (
    <div
      style={{
        maxWidth: '900px',
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        height: '720px',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-xl)',
        overflow: 'hidden',
        boxShadow: 'var(--shadow-card)',
      }}
    >
      {/* Chat Header Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1.25rem 1.75rem',
          borderBottom: '1px solid var(--border-light)',
          backgroundColor: 'var(--bg-surface)',
          flexWrap: 'wrap',
          gap: '0.75rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={16} style={{ color: 'var(--accent-primary)' }} />
            <h2 className="font-serif" style={{ fontSize: '1.35rem', fontWeight: 500, margin: 0 }}>
              Grounded Research Conversation
            </h2>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Answers are strictly cited and verified against extracted document sections.
          </p>
        </div>

        {chatHistory.length > 0 && (
          <button
            type="button"
            onClick={onClearChat}
            className="btn-secondary"
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
            title="Clear all messages in this conversation"
          >
            <Trash2 size={13} />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {/* Suggested Questions Strip */}
      <div
        style={{
          padding: '0.75rem 1.75rem',
          backgroundColor: 'var(--bg-subtle)',
          borderBottom: '1px solid var(--border-light)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.65rem',
          flexWrap: 'wrap',
        }}
      >
        <span style={{ fontSize: '0.76rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)' }}>
          Suggested:
        </span>
        <button
          type="button"
          onClick={() => handleSuggestedClick('What core problem does this research paper address?')}
          className="btn-outline-terracotta"
          style={{ fontSize: '0.78rem', padding: '0.3rem 0.75rem', borderRadius: 'var(--radius-pill)' }}
          disabled={isSending || !isApiConfigured}
        >
          What problem does this solve?
        </button>
        <button
          type="button"
          onClick={() => handleSuggestedClick('Explain the proposed methodology in clear, intuitive terms.')}
          className="btn-outline-terracotta"
          style={{ fontSize: '0.78rem', padding: '0.3rem 0.75rem', borderRadius: 'var(--radius-pill)' }}
          disabled={isSending || !isApiConfigured}
        >
          Explain methodology intuitively
        </button>
        <button
          type="button"
          onClick={() => handleSuggestedClick('What benchmark datasets were evaluated and what were the quantitative findings?')}
          className="btn-outline-terracotta"
          style={{ fontSize: '0.78rem', padding: '0.3rem 0.75rem', borderRadius: 'var(--radius-pill)' }}
          disabled={isSending || !isApiConfigured}
        >
          Datasets & quantitative results
        </button>
        <button
          type="button"
          onClick={() => handleSuggestedClick('What limitations or constraints did the authors explicitly acknowledge?')}
          className="btn-outline-terracotta"
          style={{ fontSize: '0.78rem', padding: '0.3rem 0.75rem', borderRadius: 'var(--radius-pill)' }}
          disabled={isSending || !isApiConfigured}
        >
          What are the limitations?
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1.5rem 1.75rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.35rem',
          backgroundColor: 'var(--bg-primary)',
        }}
      >
        {chatHistory.length === 0 ? (
          <div
            style={{
              margin: 'auto',
              textAlign: 'center',
              color: 'var(--text-secondary)',
              padding: '2.5rem 1rem',
            }}
          >
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-light)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem auto',
                color: 'var(--accent-primary)',
              }}
            >
              <HelpCircle size={24} />
            </div>
            <h3
              className="font-serif"
              style={{ fontSize: '1.35rem', color: 'var(--text-main)', marginBottom: '0.45rem', fontWeight: 500 }}
            >
              Ask questions about this paper
            </h3>
            <p style={{ fontSize: '0.9rem', maxWidth: '460px', margin: '0 auto', lineHeight: 1.6 }}>
              Inquire about technical proofs, neural network architectures, experimental setups, or mathematical derivations.
            </p>
          </div>
        ) : (
          chatHistory.map((msg, index) => <ChatMessage key={index} message={msg} />)
        )}

        {/* Real-time thinking indicator */}
        {isSending && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-light)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-primary)',
              }}
            >
              <Loader2 size={16} className="spin-animation" style={{ animation: 'spin 1s linear infinite' }} />
            </div>
            <div
              style={{
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-light)',
                borderRadius: '16px 16px 16px 4px',
                padding: '0.85rem 1.15rem',
                fontSize: '0.9rem',
                color: 'var(--text-secondary)',
                boxShadow: 'var(--shadow-subtle)',
              }}
            >
              Retrieving document passages and formulating verified answer...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Region */}
      <div
        style={{
          padding: '1.15rem 1.75rem',
          backgroundColor: 'var(--bg-surface)',
          borderTop: '1px solid var(--border-light)',
        }}
      >
        <form onSubmit={handleSubmit} style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <input
            ref={inputRef}
            type="text"
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isApiConfigured
                ? 'Ask a question about this research paper (press Enter to submit)...'
                : 'Configure your Google Gemini API Key to chat...'
            }
            disabled={!isApiConfigured || isSending}
            style={{
              width: '100%',
              padding: '0.95rem 4rem 0.95rem 1.25rem',
              backgroundColor: isApiConfigured ? 'var(--bg-surface)' : 'var(--bg-muted)',
              border: '1px solid var(--border-light)',
              borderRadius: 'var(--radius-pill)',
              fontSize: '0.94rem',
              fontFamily: 'var(--font-sans)',
              color: 'var(--text-main)',
              outline: 'none',
              boxShadow: 'var(--shadow-subtle)',
              transition: 'all 0.18s ease',
            }}
            onFocus={(e) => {
              if (isApiConfigured) e.target.style.borderColor = 'var(--accent-primary)';
            }}
            onBlur={(e) => (e.target.style.borderColor = 'var(--border-light)')}
          />

          <button
            type="submit"
            disabled={!inputQuestion.trim() || isSending || !isApiConfigured}
            style={{
              position: 'absolute',
              right: '8px',
              width: '38px',
              height: '38px',
              borderRadius: '50%',
              backgroundColor: inputQuestion.trim() && !isSending ? 'var(--accent-primary)' : 'var(--bg-muted)',
              color: inputQuestion.trim() && !isSending ? 'var(--text-inverted)' : 'var(--text-tertiary)',
              border: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: inputQuestion.trim() && !isSending ? 'pointer' : 'default',
              transition: 'all 0.2s ease',
            }}
            title="Send question"
          >
            <Send size={15} />
          </button>
        </form>

        {!isApiConfigured && (
          <p style={{ fontSize: '0.78rem', color: 'var(--accent-primary)', marginTop: '0.5rem', textAlign: 'center' }}>
            Gemini API key is required.{' '}
            <button
              type="button"
              onClick={onOpenSettings}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--accent-primary)',
                textDecoration: 'underline',
                fontWeight: 600,
                cursor: 'pointer',
                fontSize: '0.78rem',
              }}
            >
              Open API Settings
            </button>
          </p>
        )}
      </div>
    </div>
  );
}
