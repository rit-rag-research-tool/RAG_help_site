import React from 'react';

const fmtDate = (ts) => {
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return '';
  }
};

export default function Sidebar({
  messages = [],
  conversations = [],
  selectedId,
  onSelect = () => {},
}) {
  // Sources from the active conversation
  const lastRag = [...messages].reverse().find((m) => m.role === 'RAG');
  const sources = (lastRag?.citations || []).slice(0, 6);

  // Sort conversations by last updated (desc)
  const convosSorted = [...conversations].sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));

  return (
    <div className="sidebar">
      {/* Sources */}
      <div className="sidebar-card">
        <h3 className="card-title">Sources</h3>
        {sources.length ? (
          <ul className="sources-list">
            {sources.map((c, i) => (
              <li key={i} className="source-item">
                <a href={c.url} target="_blank" rel="noreferrer" title={c.url}>
                  {c.title || c.url}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <div className="placeholder">No sources yet</div>
        )}
      </div>

      {/* Conversations */}
      <div className="sidebar-card">
        <h3 className="card-title">Past conversations</h3>
        {convosSorted.length ? (
          <ul className="convos-list">
            {convosSorted.map((c) => {
              const hasRag = (c.messages || []).some((m) => m.role === 'RAG');
              const displayTitle =
                c.title && c.title !== 'New chat'
                  ? c.title
                  : hasRag
                  ? 'Generating title…'
                  : 'New chat';

              return (
                <li
                  key={c.id}
                  className={`convo-item ${c.id === selectedId ? 'active' : ''}`}
                  onClick={() => onSelect(c.id)}
                  style={{
                    cursor: 'pointer',
                    padding: '6px 8px',
                    borderRadius: 8,
                    background: c.id === selectedId ? 'rgba(0,0,0,0.06)' : 'transparent',
                  }}
                >
                  <div style={{ fontWeight: 600 }} title={c.title || displayTitle}>
                    {displayTitle}
                  </div>
                  <div className="conv-preview" style={{ opacity: 0.7, fontSize: 12 }}>
                    Last updated: {fmtDate(c.updatedAt)}
                  </div>
                </li>
              );
            })}
          </ul>
        ) : (
          <div className="placeholder">No past conversations yet</div>
        )}
      </div>
    </div>
  );
}
