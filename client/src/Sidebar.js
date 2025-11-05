import React, { useState } from 'react';

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
  onToggleFavorite = () => {},
}) {
  const [activeTab, setActiveTab] = useState('all'); // 'all' or 'favorites'

  // Sources from the active conversation
  const lastRag = [...messages].reverse().find((m) => m.role === 'RAG');
  const sources = (lastRag?.citations || []).slice(0, 6);

  // Sort conversations by last updated (desc)
  const convosSorted = [...conversations].sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
  
  // Filter based on active tab
  const displayedConvos = activeTab === 'favorites' 
    ? convosSorted.filter(c => c.isFavorite)
    : convosSorted;

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
        
        {/* Tabs */}
        <div className="tabs" style={{
          display: 'flex',
          borderBottom: '2px solid rgba(0,0,0,0.15)',
          marginBottom: '12px',
          gap: '4px',
          background: 'rgba(0,0,0,0.03)',
          borderRadius: '8px 8px 0 0',
          padding: '4px',
        }}>
          <button
            onClick={() => setActiveTab('all')}
            style={{
              flex: 1,
              padding: '10px 14px',
              border: 'none',
              background: activeTab === 'all' ? 'white' : 'transparent',
              cursor: 'pointer',
              fontWeight: activeTab === 'all' ? 600 : 500,
              color: activeTab === 'all' ? '#000' : '#555',
              borderRadius: '6px',
              transition: 'all 0.2s',
              boxShadow: activeTab === 'all' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
            }}
            onMouseEnter={(e) => {
              if (activeTab !== 'all') {
                e.target.style.background = 'rgba(0,0,0,0.05)';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'all') {
                e.target.style.background = 'transparent';
              }
            }}
          >
            All ({convosSorted.length})
          </button>
          <button
            onClick={() => setActiveTab('favorites')}
            style={{
              flex: 1,
              padding: '10px 14px',
              border: 'none',
              background: activeTab === 'favorites' ? 'white' : 'transparent',
              cursor: 'pointer',
              fontWeight: activeTab === 'favorites' ? 600 : 500,
              color: activeTab === 'favorites' ? '#000' : '#555',
              borderRadius: '6px',
              transition: 'all 0.2s',
              boxShadow: activeTab === 'favorites' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
            }}
            onMouseEnter={(e) => {
              if (activeTab !== 'favorites') {
                e.target.style.background = 'rgba(0,0,0,0.05)';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'favorites') {
                e.target.style.background = 'transparent';
              }
            }}
          >
            ⭐ Favorites ({convosSorted.filter(c => c.isFavorite).length})
          </button>
        </div>

        {displayedConvos.length ? (
          <ul className="convos-list">
            {displayedConvos.map((c) => {
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
                  style={{
                    cursor: 'pointer',
                    padding: '6px 8px',
                    borderRadius: 8,
                    background: c.id === selectedId ? 'rgba(0,0,0,0.06)' : 'transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '8px',
                  }}
                >
                  <div 
                    onClick={() => onSelect(c.id)}
                    style={{ flex: 1, minWidth: 0 }}
                  >
                    <div style={{ fontWeight: 600 }} title={c.title || displayTitle}>
                      {displayTitle}
                    </div>
                    <div className="conv-preview" style={{ opacity: 0.7, fontSize: 12 }}>
                      Last updated: {fmtDate(c.updatedAt)}
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleFavorite(c.id);
                    }}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '18px',
                      padding: '4px',
                      lineHeight: 1,
                      opacity: c.isFavorite ? 1 : 0.3,
                      transition: 'opacity 0.2s',
                    }}
                    onMouseEnter={(e) => e.target.style.opacity = 1}
                    onMouseLeave={(e) => e.target.style.opacity = c.isFavorite ? 1 : 0.3}
                    title={c.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    ⭐
                  </button>
                </li>
              );
            })}
          </ul>
        ) : (
          <div className="placeholder">
            {activeTab === 'favorites' ? 'No favorites yet' : 'No past conversations yet'}
          </div>
        )}
      </div>
    </div>
  );
}
