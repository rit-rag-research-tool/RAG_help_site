import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

export default function ChatBox({ messages, onSend, isLoading = false, loadingHint = "", placeholderQuestions = [] }) {
  const [input, setInput] = useState('');
  const endRef = useRef();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = (text = null) => {
    const t = (text || input).trim();
    if (!t || isLoading) return;
    onSend(t);
    setInput('');
  };

  const roleClass = (r) =>
    r === 'User' ? 'user' : r === 'RAG' ? 'bot' : 'system';

  return (
    <div style={{ minWidth: 0 }}>
      <div className="messages-box" aria-live="polite">
        {messages.map((m, i) => (
          <div key={i} className={`message-row ${roleClass(m.role)}`}>
            <div className={`bubble ${roleClass(m.role)}`}>
              {m.role === 'RAG' ? (
                <div className="markdown-content">
                  <ReactMarkdown>{m.text}</ReactMarkdown>
                </div>
              ) : (
                m.text
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message-row bot">
            <div className="bubble bot typing-bubble" role="status" aria-live="polite">
              {loadingHint || "Generating answer"}
              <span className="dots" aria-hidden="true">
                <span></span><span></span><span></span>
              </span>
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* Placeholder questions - show when conversation has messages but user hasn't started typing */}
      {placeholderQuestions.length > 0 && !input && !isLoading && (
        <div className="placeholder-questions" style={{
          padding: '12px 16px',
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          borderTop: '1px solid rgba(0,0,0,0.1)',
        }}>
          {placeholderQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => handleSend(q)}
              className="placeholder-btn"
              style={{
                padding: '8px 12px',
                borderRadius: '16px',
                border: '1px solid rgba(0,0,0,0.15)',
                background: 'white',
                cursor: 'pointer',
                fontSize: '13px',
                transition: 'all 0.2s',
                color: '#333',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(0,0,0,0.05)';
                e.target.style.borderColor = 'rgba(0,0,0,0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'white';
                e.target.style.borderColor = 'rgba(0,0,0,0.15)';
              }}
            >
              {q}
            </button>
          ))}
        </div>
      )}

      <div className="composer">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={isLoading ? "Working on it…" : "Ask anything…"}
          aria-label="Message"
          disabled={isLoading}
        />
        <button onClick={handleSend} className="btn primary" disabled={isLoading}>
          {isLoading ? "Generating…" : "Send"}
        </button>
      </div>
    </div>
  );
}
