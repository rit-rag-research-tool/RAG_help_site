import React, { useEffect, useMemo, useState } from 'react';
import './App.css';
import ChatBox from './ChatBox';
import Sidebar from './Sidebar';

// --- helpers ---
const uid = () => `c_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

// (kept for possible fallbacks; we no longer auto-title with this)
const inferTitle = (text = '') => {
  const first = (text.split(/[.?!\n]/)[0] || text).trim();
  if (!first) return 'New chat';
  const cleaned = first
    .replace(/^what is\s+/i, '')
    .replace(/^who is\s+/i, '')
    .replace(/^tell me about\s+/i, '')
    .replace(/^can you\s+/i, '')
    .replace(/\s+/g, ' ')
    .trim();
  return (cleaned.length > 50 ? cleaned.slice(0, 47) + '…' : cleaned) || 'New chat';
};

const load = () => {
  try {
    const raw = localStorage.getItem('conversations_v1');
    if (raw) return JSON.parse(raw);
  } catch {}
  // default bootstrap conversation
  const id = uid();
  return [
    {
      id,
      title: 'New chat',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
    },
  ];
};

const save = (convos) => {
  try {
    localStorage.setItem('conversations_v1', JSON.stringify(convos));
  } catch {}
};

// Friendly “generating” microcopy
const HINTS = [
  'Searching the web…',
  'Verifying facts & sources…',
  'Composing your answer…',
  'Gathering up-to-date info…',
  'Cross-checking results…',
  'Summarizing findings…',
];

function App() {
  const [conversations, setConversations] = useState(load);
  const [selectedId, setSelectedId] = useState(conversations[0]?.id);

  const [isLoading, setIsLoading] = useState(false);
  const [loadingHint, setLoadingHint] = useState('');

  useEffect(() => save(conversations), [conversations]);

  const current = useMemo(
    () => conversations.find((c) => c.id === selectedId) || conversations[0],
    [conversations, selectedId]
  );
  const messages = current?.messages || [];

  const startNewChat = () => {
    const id = uid();
    const next = [
      {
        id,
        title: 'New chat',
        createdAt: Date.now(),
        updatedAt: Date.now(),
        messages: [],
      },
      ...conversations,
    ];
    setConversations(next);
    setSelectedId(id);
  };

  const updateConversation = (id, updater) => {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? updater({ ...c }) : c))
    );
  };

  const sendMessage = async (text) => {
    const userMsg = { role: 'User', text };

    // Snapshot to avoid races if selection changes mid-request
    const convId = current.id;
    const wasUntitled = current.title === 'New chat';
    const transcriptBefore = current.messages;
    const transcriptSoFar = [...transcriptBefore, userMsg];

    // 1) append user message
    updateConversation(convId, (conv) => {
      conv.messages = [...conv.messages, userMsg];
      // No auto-title here; we’ll name it via GPT after first bot reply
      conv.updatedAt = Date.now();
      return conv;
    });

    // Show loader after 200ms (prevents flicker on super-fast replies)
    const hint = HINTS[Math.floor(Math.random() * HINTS.length)];
    const loaderTimer = setTimeout(() => {
      setLoadingHint(hint);
      setIsLoading(true);
    }, 200);

    // 2) call backend
    try {
      const res = await fetch('/rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'omit',
        body: JSON.stringify({ query: text }),
      });

      if (!res.ok) {
        const txt = await res.text();
        console.error('Backend error', res.status, txt);
        const sysMsg = { role: 'System', text: `Backend error: ${res.status}` };
        updateConversation(convId, (conv) => {
          conv.messages = [...conv.messages, sysMsg];
          conv.updatedAt = Date.now();
          return conv;
        });
        return;
      }

      const data = await res.json();
      const botText = data.answer || data?.message || 'No answer';
      const ragMsg = { role: 'RAG', text: botText, citations: data.citations || [] };

      // 3) append bot message
      updateConversation(convId, (conv) => {
        conv.messages = [...conv.messages, ragMsg];
        conv.updatedAt = Date.now();
        return conv;
      });

      // 4) If still untitled, ask GPT to generate a title from the short transcript
      if (wasUntitled) {
        try {
          const titleRes = await fetch('/title', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: [...transcriptSoFar, ragMsg] }),
          });
          if (titleRes.ok) {
            const { title } = await titleRes.json();
            if (title && typeof title === 'string') {
              updateConversation(convId, (conv) => {
                if (conv.title === 'New chat') {
                  conv.title = title;
                }
                conv.updatedAt = Date.now();
                return conv;
              });
            }
          } else {
            console.warn('Title endpoint error', titleRes.status);
          }
        } catch (e) {
          console.warn('Title generation failed', e);
        }
      }
    } catch (err) {
      console.error(err);
      const sysMsg = { role: 'System', text: 'Error contacting backend' };
      updateConversation(convId, (conv) => {
        conv.messages = [...conv.messages, sysMsg];
        conv.updatedAt = Date.now();
        return conv;
      });
    } finally {
      clearTimeout(loaderTimer);
      setIsLoading(false);
      setLoadingHint('');
    }
  };

  return (
    <div className="app-root">
      <div className="app-container">
        <main className="chat-area">
          <div className="app-header">
            <h2 className="app-title">
              RAG Chat <span className="badge">Web Search + Citations</span>
            </h2>
            <button onClick={startNewChat} className="btn primary">New Chat</button>
          </div>

          <div className="subtle" style={{ marginBottom: 10 }}>
            <strong>Conversation:</strong> {current?.title || 'Untitled'}
          </div>

          <ChatBox
            messages={messages}
            onSend={sendMessage}
            isLoading={isLoading}
            loadingHint={loadingHint}
          />
        </main>

        <aside className="sidebar-area">
          <Sidebar
            messages={messages}
            conversations={conversations}
            selectedId={current?.id}
            onSelect={(id) => setSelectedId(id)}
          />
        </aside>
      </div>
    </div>
  );
}

export default App;
