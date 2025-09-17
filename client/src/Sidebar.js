import React from 'react';

export default function Sidebar({ messages = [] }) {
  const sources = [
    'Source A — placeholder',
    'Source B — placeholder',
    'Source C — placeholder'
  ];

  const pastConvos = messages.length ? [
    { id: 1, title: 'Recent convo (preview)', preview: messages.slice(-2).map(m => `${m.role}: ${m.text}`).join(' | ') }
  ] : [];

  return (
    <div className="sidebar">
      <div className="sidebar-card">
        <h3 className="card-title">Sources</h3>
        <ul className="sources-list">
          {sources.map((s, i) => <li key={i} className="source-item">{s}</li>)}
        </ul>
      </div>

      <div className="sidebar-card">
        <h3 className="card-title">Past conversations</h3>
        {pastConvos.length ? (
          <ul className="convos-list">
            {pastConvos.map(c => (
              <li key={c.id} className="convo-item">
                <strong>{c.title}</strong>
                <div className="conv-preview">{c.preview}</div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="placeholder">No past conversations yet</div>
        )}
      </div>
    </div>
  );
}