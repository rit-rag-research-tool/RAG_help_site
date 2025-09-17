import React, { useState, useRef, useEffect } from 'react';

export default function ChatBox({ messages, onSend }) {
  const [input, setInput] = useState('');
  const endRef = useRef();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const t = input.trim();
    if (!t) return;
    onSend(t);
    setInput('');
  };

  return (
    <div style={{ maxWidth: 700 }}>
      <div className="messages-box">
        {messages.map((m, i) => (
          <div key={i} className={`message-row ${m.role === 'User' ? 'msg-user' : m.role === 'RAG' ? 'msg-bot' : 'msg-system'}`}>
            <strong style={{ marginRight: 8 }}>{m.role}:</strong>
            <span>{m.text}</span>
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
        />
        <button onClick={handleSend} className="send-button">Send</button>
      </div>
    </div>
  );
}