import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, Copy, Check } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const [copiedCode, setCopiedCode] = useState(null);

  const handleCopyCode = (codeText, id) => {
    navigator.clipboard.writeText(codeText);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        gap: '0.85rem',
        width: '100%',
      }}
    >
      {!isUser && (
        <div
          style={{
            width: '34px',
            height: '34px',
            borderRadius: '50%',
            backgroundColor: 'var(--bg-muted)',
            border: '1px solid var(--border-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-primary)',
            flexShrink: 0,
            marginTop: '2px',
          }}
          aria-label="Assistant"
        >
          <Bot size={17} />
        </div>
      )}

      <div
        style={{
          maxWidth: isUser ? '80%' : '88%',
          backgroundColor: isUser ? 'var(--accent-primary)' : 'var(--bg-surface)',
          color: isUser ? 'var(--text-inverted)' : 'var(--text-main)',
          border: isUser ? '1px solid var(--accent-primary)' : '1px solid var(--border-light)',
          borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
          padding: '1rem 1.35rem',
          fontSize: '0.94rem',
          lineHeight: 1.65,
          boxShadow: 'var(--shadow-subtle)',
          wordBreak: 'break-word',
          overflowWrap: 'break-word',
        }}
      >
        {isUser ? (
          <div style={{ whiteSpace: 'pre-wrap', fontWeight: 400 }}>{message.content}</div>
        ) : (
          <div className="chat-markdown-body">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p style={{ margin: '0 0 0.85rem 0', lineHeight: 1.65 }}>{children}</p>,
                h1: ({ children }) => (
                  <h1
                    className="font-serif"
                    style={{ fontSize: '1.45rem', margin: '1rem 0 0.5rem 0', color: 'var(--text-main)' }}
                  >
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2
                    className="font-serif"
                    style={{ fontSize: '1.25rem', margin: '0.9rem 0 0.45rem 0', color: 'var(--text-main)' }}
                  >
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3
                    className="font-serif"
                    style={{ fontSize: '1.1rem', margin: '0.75rem 0 0.4rem 0', color: 'var(--text-main)' }}
                  >
                    {children}
                  </h3>
                ),
                ul: ({ children }) => (
                  <ul style={{ margin: '0 0 0.85rem 1.35rem', padding: 0, listStyleType: 'disc' }}>
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol style={{ margin: '0 0 0.85rem 1.35rem', padding: 0, listStyleType: 'decimal' }}>
                    {children}
                  </ol>
                ),
                li: ({ children }) => <li style={{ marginBottom: '0.35rem', lineHeight: 1.6 }}>{children}</li>,
                blockquote: ({ children }) => (
                  <blockquote
                    style={{
                      borderLeft: '3px solid var(--accent-primary)',
                      paddingLeft: '0.9rem',
                      margin: '0.85rem 0',
                      color: 'var(--text-secondary)',
                      fontStyle: 'italic',
                    }}
                  >
                    {children}
                  </blockquote>
                ),
                code: ({ inline, className, children, ...props }) => {
                  const match = /language-(\w+)/.exec(className || '');
                  const codeString = String(children).replace(/\n$/, '');
                  const blockId = Math.random().toString(36).substring(7);

                  if (inline) {
                    return (
                      <code
                        style={{
                          backgroundColor: 'var(--bg-muted)',
                          color: 'var(--accent-primary)',
                          padding: '0.15rem 0.4rem',
                          borderRadius: '4px',
                          fontSize: '0.86rem',
                          fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
                          fontWeight: 500,
                        }}
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  }

                  return (
                    <div
                      style={{
                        position: 'relative',
                        margin: '0.85rem 0',
                        borderRadius: 'var(--radius-md)',
                        overflow: 'hidden',
                        backgroundColor: '#1E1E1E',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.4rem 0.85rem',
                          backgroundColor: '#2D2D2D',
                          color: '#A0A0A0',
                          fontSize: '0.74rem',
                          fontFamily: 'ui-monospace, monospace',
                          textTransform: 'uppercase',
                        }}
                      >
                        <span>{match ? match[1] : 'code'}</span>
                        <button
                          type="button"
                          onClick={() => handleCopyCode(codeString, blockId)}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#CCCCCC',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                            fontSize: '0.72rem',
                          }}
                        >
                          {copiedCode === blockId ? (
                            <>
                              <Check size={12} style={{ color: '#4ADE80' }} />
                              <span style={{ color: '#4ADE80' }}>Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy size={12} />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                      <pre
                        style={{
                          margin: 0,
                          padding: '1rem',
                          overflowX: 'auto',
                          color: '#E0E0E0',
                          fontSize: '0.84rem',
                          lineHeight: 1.5,
                          fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
                        }}
                      >
                        <code>{children}</code>
                      </pre>
                    </div>
                  );
                },
                table: ({ children }) => (
                  <div style={{ overflowX: 'auto', margin: '0.85rem 0' }}>
                    <table
                      style={{
                        borderCollapse: 'collapse',
                        width: '100%',
                        fontSize: '0.86rem',
                        border: '1px solid var(--border-light)',
                      }}
                    >
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th
                    style={{
                      border: '1px solid var(--border-light)',
                      padding: '0.5rem 0.75rem',
                      backgroundColor: 'var(--bg-muted)',
                      textAlign: 'left',
                      fontWeight: 600,
                    }}
                  >
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td style={{ border: '1px solid var(--border-light)', padding: '0.5rem 0.75rem' }}>
                    {children}
                  </td>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {isUser && (
        <div
          style={{
            width: '34px',
            height: '34px',
            borderRadius: '50%',
            backgroundColor: 'var(--accent-subtle)',
            border: '1px solid var(--accent-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-primary)',
            flexShrink: 0,
            marginTop: '2px',
          }}
          aria-label="User"
        >
          <User size={17} />
        </div>
      )}
    </div>
  );
}
