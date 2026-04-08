import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

const QUICK_ACTIONS = [
  { label: '📊 Forecast top products', message: 'Forecast my top selling products for the next 2 weeks' },
  { label: '🔍 Scan for anomalies', message: 'Are there any anomalies in our sales or returns data?' },
  { label: '⚙️ Optimize stock', message: 'Give me a full stock optimization report' },
  { label: '👟 Blue Sneakers forecast', message: 'What\'s the demand forecast for blue sneakers next week?' },
  { label: '👕 Red T-Shirt stock', message: 'When should I reorder red t-shirts?' },
];

export default function ChatWindow({ messages, isLoading, onSendMessage }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickAction = (msg) => {
    onSendMessage(msg);
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-logo">🏭</div>
        <div className="chat-header-info">
          <h1>Agnes</h1>
          <p>AI Supply Chain Manager</p>
        </div>
        <div className="chat-header-agents">
          <div className="agent-indicator" style={{ background: '#3b82f6', color: '#3b82f6' }} title="Forecaster" />
          <div className="agent-indicator" style={{ background: '#ef4444', color: '#ef4444' }} title="Scout" />
          <div className="agent-indicator" style={{ background: '#10b981', color: '#10b981' }} title="Optimizer" />
        </div>
      </div>

      {/* Messages or Welcome */}
      {isEmpty ? (
        <div className="welcome-container">
          <div className="welcome-logo">🏭</div>
          <h2 className="welcome-title">Meet Agnes</h2>
          <p className="welcome-subtitle">
            Your AI supply chain manager with three specialist agents ready to forecast demand,
            detect anomalies, and optimize your inventory.
          </p>
          <div className="welcome-agents">
            <div
              className="welcome-agent-card"
              onClick={() => handleQuickAction('Forecast my top selling products')}
            >
              <div className="welcome-agent-icon" style={{ background: 'rgba(59,130,246,0.15)' }}>📊</div>
              <div className="welcome-agent-name">Forecaster</div>
              <div className="welcome-agent-role">The Strategist</div>
            </div>
            <div
              className="welcome-agent-card"
              onClick={() => handleQuickAction('Scan for anomalies in our data')}
            >
              <div className="welcome-agent-icon" style={{ background: 'rgba(239,68,68,0.15)' }}>🔍</div>
              <div className="welcome-agent-name">Scout</div>
              <div className="welcome-agent-role">The Lookout</div>
            </div>
            <div
              className="welcome-agent-card"
              onClick={() => handleQuickAction('Give me a stock optimization report')}
            >
              <div className="welcome-agent-icon" style={{ background: 'rgba(16,185,129,0.15)' }}>⚙️</div>
              <div className="welcome-agent-name">Optimizer</div>
              <div className="welcome-agent-role">The Builder</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="chat-messages">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isLoading && (
            <div className="message agent" style={{ opacity: 1 }}>
              <div className="message-avatar" style={{ background: 'linear-gradient(135deg, #8b5cf6, #6366f1)' }}>
                🏭
              </div>
              <div className="message-content">
                <div className="message-agent-name" style={{ color: '#8b5cf6' }}>Agnes</div>
                <div className="message-bubble">
                  <div className="typing-indicator">
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Input */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Agnes about forecasts, anomalies, or stock optimization..."
            rows={1}
            disabled={isLoading}
          />
          <button
            className="chat-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            title="Send message"
          >
            ➤
          </button>
        </div>
        {isEmpty && (
          <div className="quick-actions">
            {QUICK_ACTIONS.map((action, i) => (
              <button
                key={i}
                className="quick-action-chip"
                onClick={() => handleQuickAction(action.message)}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
