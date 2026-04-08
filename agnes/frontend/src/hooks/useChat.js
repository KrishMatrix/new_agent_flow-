import { useState, useCallback, useRef } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState(null);
  const abortRef = useRef(null);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setActiveAgent('thinking');

    try {
      const res = await axios.post(`${API_URL}/chat`, {
        message: text,
      });

      const data = res.data;

      const agentMessage = {
        id: Date.now() + 1,
        role: 'agent',
        agent: data.agent,
        agentColor: data.agent_color,
        agentIcon: data.agent_icon,
        content: data.message,
        data: data.data,
        chartType: data.chart_type,
        chartData: data.chart_data,
        tableData: data.table_data,
        timestamp: new Date().toISOString(),
      };

      setActiveAgent(data.agent?.toLowerCase() || null);
      setMessages((prev) => [...prev, agentMessage]);
    } catch (err) {
      const errorMessage = {
        id: Date.now() + 1,
        role: 'agent',
        agent: 'Agnes',
        agentColor: '#8b5cf6',
        agentIcon: '🏭',
        content: `⚠️ **Connection Error**\n\nI couldn't connect to the backend. Make sure the FastAPI server is running:\n\n\`cd backend && uvicorn main:app --reload --port 8000\``,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setActiveAgent(null);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setActiveAgent(null);
  }, []);

  return {
    messages,
    isLoading,
    activeAgent,
    sendMessage,
    clearMessages,
  };
}
