import React from 'react';
import AgentAvatar from './AgentAvatar';
import ForecastChart from './ForecastChart';
import InventoryTable from './InventoryTable';

function formatMessage(text) {
  if (!text) return '';

  // Convert markdown-like formatting to HTML
  let html = text
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/_(.*?)_/g, '<em>$1</em>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code style="background:rgba(139,92,246,0.15);padding:2px 6px;border-radius:4px;font-size:12px;color:#c4b5fd">$1</code>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');

  // Wrap bullet points
  html = html.replace(/(•[^<]*)/g, '<span style="display:block;padding-left:4px;margin:2px 0">$1</span>');

  return `<p>${html}</p>`;
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`message ${isUser ? 'user' : 'agent'}`}>
      {!isUser && (
        <AgentAvatar
          agent={message.agent}
          color={message.agentColor}
          icon={message.agentIcon}
        />
      )}

      <div className="message-content">
        {!isUser && (
          <div
            className="message-agent-name"
            style={{ color: message.agentColor }}
          >
            {message.agent}
          </div>
        )}

        <div className="message-bubble">
          <div
            dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
          />

          {/* Inline chart */}
          {message.chartType === 'forecast' && message.chartData && (
            <ForecastChart data={message.chartData} />
          )}

          {/* Inline table */}
          {(message.chartType === 'table' || message.chartType === 'metrics') && message.tableData && (
            <InventoryTable data={message.tableData} />
          )}
        </div>

        <div style={{
          fontSize: '10px',
          color: 'var(--text-muted)',
          marginTop: '2px',
          paddingLeft: '2px',
        }}>
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>

      {isUser && (
        <div
          className="message-avatar"
          style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            fontSize: '16px',
          }}
        >
          👤
        </div>
      )}
    </div>
  );
}
