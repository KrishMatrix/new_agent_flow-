import React from 'react';
import { useChat } from './hooks/useChat';
import AgentScene from './components/AgentScene';
import ChatWindow from './components/ChatWindow';
import DashboardPanel from './components/DashboardPanel';
import './styles/global.css';
import './styles/chat.css';
import './styles/agents.css';

export default function App() {
  const { messages, isLoading, activeAgent, sendMessage } = useChat();

  return (
    <div className="app-layout">
      <div className="main-content">
        <AgentScene activeAgent={activeAgent} />
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSendMessage={sendMessage}
        />
      </div>
      <DashboardPanel />
    </div>
  );
}
