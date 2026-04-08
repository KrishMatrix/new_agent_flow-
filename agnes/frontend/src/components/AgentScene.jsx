import React from 'react';
import { useAgentAnimation } from '../hooks/useAgentAnimation';

export default function AgentScene({ activeAgent }) {
  const { getAgentState, showSpeech, agents } = useAgentAnimation(activeAgent);

  const agentKeys = ['forecaster', 'scout', 'optimizer'];

  return (
    <div className="agent-scene">
      <div className="agent-scene-ground" />

      {agentKeys.map((key) => {
        const agent = getAgentState(key);
        const isActive = agent.isActive;
        const stateClass = activeAgent === 'thinking'
          ? ''
          : isActive ? 'active walking' : activeAgent ? 'inactive' : '';

        return (
          <div
            key={key}
            className={`agent-character ${key} ${stateClass}`}
            style={{ color: agent.color }}
          >
            {isActive && showSpeech && (
              <div className="agent-speech-bubble">
                {agent.speech}
              </div>
            )}
            <div className="agent-label" style={{ color: agent.color }}>
              {agent.name}
            </div>
            <img
              src={agent.sprite}
              alt={agent.name}
              draggable={false}
            />
          </div>
        );
      })}

      {activeAgent === 'thinking' && (
        <div
          className="agent-speech-bubble"
          style={{
            position: 'absolute',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 10,
          }}
        >
          <span className="typing-indicator">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </span>
        </div>
      )}
    </div>
  );
}
