import { useState, useEffect, useCallback } from 'react';

const AGENT_CONFIGS = {
  forecaster: {
    name: 'Forecaster',
    sprite: '/assets/forecaster.png',
    color: '#3b82f6',
    position: 'left',
    speech: 'Analyzing trends...',
  },
  scout: {
    name: 'Scout',
    sprite: '/assets/scout.png',
    color: '#ef4444',
    position: 'center',
    speech: 'Scanning for anomalies...',
  },
  optimizer: {
    name: 'Optimizer',
    sprite: '/assets/optimizer.png',
    color: '#10b981',
    position: 'right',
    speech: 'Crunching numbers...',
  },
  agnes: {
    name: 'Agnes',
    sprite: null,
    color: '#8b5cf6',
    position: 'center',
    speech: 'How can I help?',
  },
};

export function useAgentAnimation(activeAgent) {
  const [animatingAgent, setAnimatingAgent] = useState(null);
  const [showSpeech, setShowSpeech] = useState(false);

  useEffect(() => {
    if (!activeAgent || activeAgent === 'thinking') {
      setShowSpeech(false);
      return;
    }

    const agentKey = activeAgent.toLowerCase();
    setAnimatingAgent(agentKey);
    setShowSpeech(true);

    const timer = setTimeout(() => {
      setShowSpeech(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, [activeAgent]);

  const getAgentState = useCallback((agentName) => {
    const key = agentName.toLowerCase();
    const config = AGENT_CONFIGS[key] || {};

    if (!activeAgent || activeAgent === 'thinking') {
      return { ...config, state: 'idle', isActive: false };
    }

    const activeKey = activeAgent.toLowerCase();
    if (key === activeKey) {
      return { ...config, state: 'active', isActive: true };
    }

    return { ...config, state: 'inactive', isActive: false };
  }, [activeAgent]);

  return {
    animatingAgent,
    showSpeech,
    getAgentState,
    agents: AGENT_CONFIGS,
  };
}
