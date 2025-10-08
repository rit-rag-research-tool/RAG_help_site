import React, { useState, useRef, useEffect } from 'react';

export default function ChatBox({ messages, onSend, isLoading = false, loadingHint = "" }) {
  const [input, setInput] = useState('');
  const endRef = useRef();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = () => {
    const t = input.trim();
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
            <div className={`bubble ${roleClass(m.role)}`}>{m.text}</div>
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
