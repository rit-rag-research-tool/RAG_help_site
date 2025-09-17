import React, { useState } from 'react';
import './App.css';
import ChatBox from './ChatBox';
import Sidebar from './Sidebar';

function App() {
  const [messages, setMessages] = useState([]);

  const sendMessage = async (text) => {
    const userMsg = { role: 'User', text };
    setMessages((m) => [...m, userMsg]);

    try {
      const res = await fetch('/rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });
      const data = await res.json();
      const botText = data.answer || data?.message || 'No answer';
      setMessages((m) => [...m, { role: 'RAG', text: botText }]);
    } catch (err) {
      setMessages((m) => [...m, { role: 'System', text: 'Error contacting backend' }]);
      console.error(err);
    }
  };

  return (
    <div className="app-root">
      <div className="app-container">
        <main className="chat-area">
          <h2>RAG Chat</h2>
          <ChatBox messages={messages} onSend={sendMessage} />
        </main>

        <aside className="sidebar-area">
          <Sidebar messages={messages} />
        </aside>
      </div>
    </div>
  );
}

export default App;
