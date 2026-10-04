import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Trash2, Loader2, Sparkles, HelpCircle } from 'lucide-react';

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isSending]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputQuestion.trim() && !isSending) {
      onSendMessage(inputQuestion.trim());
      setInputQuestion('');
    }
  };

  const handleSuggestedClick = (text) => {
    if (!isSending) {
      onSendMessage(text);
    }
  };

  return (
    <div style={{ maxWidth: '850px', margin: '0 auto', display: 'flex', flexDirection: 'column', height: '680px' }}>
      {/* Chat Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingBottom: '1rem',
          borderBottom: '1px solid var(--border-light)',
          marginBottom: '1rem',
        }}
      >
        <div>
          <h2 className="font-serif" style={{ fontSize: '1.45rem', fontWeight: 500 }}>
            Ask Your Research Paper
          </h2>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
            Strictly grounded in paper sections. No unverified assumptions or generic hallucinations.
          </p>
        </div>

        {chatHistory.length > 0 && (
          <button
            onClick={onClearChat}
            className="btn-secondary"
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
          >
            <Trash2 size={13} />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {/* Suggested Questions (Pills) */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem', marginBottom: '1rem' }}>
        <button
          onClick={() => handleSuggestedClick('What problem does this paper solve?')}
          className="btn-outline-terracotta"
          style={{ fontSize: '0.8rem', padding: '0.3rem 0.75rem' }}
          disabled={isSending}
        >
          What problem does this paper solve?
        </button>
        <button
          onClick={() => handleSuggestedClick('Explain the methodology in simple language.')}
          className="btn-outline-terracotta"
          style={{ fontSize: '0.8rem', padding: '0.3rem 0.75rem' }}
          disabled={isSending}
        >
          Explain methodology simply
        </button>
        <button
          onClick={() => handleSuggestedClick('What are the key limitations of this work?')}
          className="btn-outline-terracotta"
          style={{ fontSize: '0.8rem', padding: '0.3rem 0.75rem' }}
          disabled={isSending}
        >
          What are the limitations?
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1rem 0.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
        }}
      >
        {chatHistory.length === 0 ? (
          <div
            style={{
              margin: 'auto',
              textAlign: 'center',
              color: 'var(--text-secondary)',
              padding: '2rem 1rem',
            }}
          >
            <HelpCircle size={32} style={{ color: 'var(--text-tertiary)', margin: '0 auto 0.75rem auto' }} />
            <p className="font-serif" style={{ fontSize: '1.25rem', color: 'var(--text-main)', marginBottom: '0.35rem' }}>
              No messages yet
            </p>
            <p style={{ fontSize: '0.88rem', maxWidth: '420px', margin: '0 auto' }}>
              Ask questions about the paper's experiments, benchmark results, mathematical equations, or baseline comparisons.
            </p>
          </div>
        ) : (
          chatHistory.map((msg, index) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={index}
                style={{
                  display: 'flex',
                  justifyContent: isUser ? 'flex-end' : 'flex-start',
                  gap: '0.75rem',
                }}
              >
                {!isUser && (
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--bg-muted)',
                      border: '1px solid var(--border-light)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--accent-primary)',
                      flexShrink: 0,
                    }}
                  >
                    <Bot size={16} />
                  </div>
                )}

                <div
                  style={{
                    maxWidth: '82%',
                    backgroundColor: isUser ? 'var(--accent-primary)' : 'var(--bg-surface)',
                    color: isUser ? '#FFFFFF' : 'var(--text-main)',
                    border: isUser ? '1px solid var(--accent-primary)' : '1px solid var(--border-light)',
                    borderRadius: isUser ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                    padding: '0.85rem 1.15rem',
                    fontSize: '0.92rem',
                    lineHeight: 1.6,
                    boxShadow: 'var(--shadow-subtle)',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {msg.content}
                </div>

                {isUser && (
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--accent-subtle)',
                      border: '1px solid var(--accent-border)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--accent-primary)',
                      flexShrink: 0,
                    }}
                  >
                    <User size={16} />
                  </div>
                )}
              </div>
            );
          })
        )}

        {/* Typing indicator */}
        {isSending && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: 'var(--bg-muted)',
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
                borderRadius: 'var(--radius-lg)',
                padding: '0.75rem 1rem',
                fontSize: '0.88rem',
                color: 'var(--text-secondary)',
              }}
            >
              Searching paper context & generating answer...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{ marginTop: '1rem', position: 'relative' }}>
        <input
          type="text"
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          placeholder={
            isApiConfigured
              ? 'Ask a question about this paper (e.g. Which dataset was used?)...'
              : 'Configure Gemini API Key in settings to chat...'
          }
          disabled={!isApiConfigured || isSending}
          style={{
            width: '100%',
            padding: '0.9rem 3.5rem 0.9rem 1.15rem',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-xl)',
            fontSize: '0.94rem',
            fontFamily: 'var(--font-sans)',
            color: 'var(--text-main)',
            outline: 'none',
            boxShadow: 'var(--shadow-subtle)',
            transition: 'border-color 0.18s ease',
          }}
          onFocus={(e) => (e.target.style.borderColor = 'var(--accent-primary)')}
          onBlur={(e) => (e.target.style.borderColor = 'var(--border-light)')}
        />
        <button
          type="submit"
          disabled={!inputQuestion.trim() || isSending || !isApiConfigured}
          style={{
            position: 'absolute',
            right: '8px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: inputQuestion.trim() && !isSending ? 'var(--accent-primary)' : 'var(--bg-muted)',
            color: inputQuestion.trim() && !isSending ? '#FFFFFF' : 'var(--text-tertiary)',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: inputQuestion.trim() && !isSending ? 'pointer' : 'default',
            transition: 'all 0.18s ease',
          }}
        >
          <Send size={15} />
        </button>
      </form>
    </div>
  );
}
