import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FaPaperPlane } from 'react-icons/fa';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ChatSessionManager from './ChatSessionManager';
import { useChat } from '../context/ChatContext';

const Container = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1.25rem;
  overflow: hidden;
`;

const ChatHistory = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 0.625rem;
  border-radius: 0.5rem;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  margin-bottom: 1.25rem;
`;

const LoadingIndicator = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.25rem;
  margin-top: 0.625rem;
  
  .spinner {
    width: 2.5rem;
    height: 2.5rem;
    border: 0.25rem solid var(--primary-color);
    border-radius: 50%;
    border-top-color: transparent;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

const ChatContainer = () => {
  const { messages, isLoading, sendMessage } = useChat();
  const [input, setInput] = useState('');
  const chatHistoryRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (input.trim() === '') return;
    
    sendMessage(input);
    setInput('');
  };

  return (
    <Container>
      <ChatSessionManager />
      <ChatHistory ref={chatHistoryRef}>
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        
        {isLoading && (
          <LoadingIndicator>
            <div className="spinner" />
          </LoadingIndicator>
        )}
      </ChatHistory>
      
      <ChatInput
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={handleSendMessage}
        disabled={isLoading}
      />
    </Container>
  );
};

export default ChatContainer;
