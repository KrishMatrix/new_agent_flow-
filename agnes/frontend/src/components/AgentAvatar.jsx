import React from 'react';

const AGENT_SPRITES = {
  Forecaster: '/assets/forecaster.png',
  Scout: '/assets/scout.png',
  Optimizer: '/assets/optimizer.png',
};

export default function AgentAvatar({ agent, color, icon }) {
  const sprite = AGENT_SPRITES[agent];

  if (sprite) {
    return (
      <div
        className="message-avatar"
        style={{
          background: `${color}20`,
          border: `2px solid ${color}40`,
        }}
      >
        <img src={sprite} alt={agent} style={{ imageRendering: 'pixelated' }} />
      </div>
    );
  }

  return (
    <div
      className="message-avatar"
      style={{
        background: `linear-gradient(135deg, ${color}, ${color}cc)`,
      }}
    >
      {icon || '🏭'}
    </div>
  );
}
