import React, { useState } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import { FaUser, FaRobot, FaThumbsUp, FaThumbsDown } from 'react-icons/fa';

const MessageContainer = styled.div`
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  align-items: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
`;

const MessageHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.3125rem;
`;

const Avatar = styled.div`
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  background-color: ${props => props.$isUser ? 'var(--text-secondary)' : 'var(--primary-color)'};
`;

const Name = styled.span`
  font-weight: 500;
  color: var(--text-primary);
`;

const Timestamp = styled.span`
  font-size: 0.75rem;
  color: var(--text-secondary);
`;

const MessageContent = styled.div`
  padding: 0.75rem 1rem;
  border-radius: 1.125rem;
  max-width: 85%;
  background-color: ${props => props.$isUser ? 'var(--primary-color)' : 'var(--bg-tertiary)'};
  color: ${props => props.$isUser ? 'white' : 'var(--text-primary)'};
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  
  p {
    margin: 0 0 1rem;
    line-height: 1.5;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  /* Add vertical rhythm between paragraphs */
  p + p {
    margin-top: 1rem;
  }
  
  pre {
    background-color: ${props => props.$isUser ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.05)'};
    border-radius: 0.25rem;
    padding: 0.5rem;
    overflow-x: auto;
    margin: 1rem 0;
  }
  
  code {
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 0.875rem;
  }
  
  ul, ol {
    margin: 0 0 1rem;
    padding-left: 1.25rem;
  }
  
  /* Improved styling for headings */
  h1 {
    font-size: 1.5rem;
    margin: 1.5rem 0 1rem;
    color: ${props => props.$isUser ? 'white' : '#B8860B'};
    border-bottom: 1px solid ${props => props.$isUser ? 'rgba(255, 255, 255, 0.2)' : 'var(--border-color)'};
    padding-bottom: 0.5rem;
  }
  
  h2 {
    font-size: 1.25rem;
    margin: 1.25rem 0 1rem;
    color: ${props => props.$isUser ? 'white' : '#B8860B'};
    border-bottom: 1px solid ${props => props.$isUser ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
    padding-bottom: 0.25rem;
  }
  
  h3 {
    font-size: 1.1rem;
    margin: 1rem 0 0.75rem;
    font-weight: 600;
    color: ${props => props.$isUser ? 'white' : '#B8860B'};
  }
  
  h4, h5, h6 {
    font-size: 1rem;
    margin: 1rem 0 0.75rem;
    font-weight: 600;
  }
  
  /* Better formatting for lists (especially for process guides) */
  ol li, ul li {
    margin-bottom: 0.75rem;
    line-height: 1.5;
    display: list-item;
    padding-left: 0.5rem;
  }
  
  /* Fix for numbered list items to stay together with their content */
  li p {
    margin: 0;
    display: inline;
  }
  
  /* Fix for bold numbered items */
  li strong {
    margin-right: 0.25rem;
    display: inline;
  }
  
  /* Proper list rendering */
  ol {
    list-style-type: decimal;
  }
  
  ul {
    list-style-type: disc;
  }
  
  /* Add spacing between list items for better readability */
  ol li:not(:last-child), ul li:not(:last-child) {
    margin-bottom: 1rem;
  }
  
  /* Highlight important information */
  strong {
    color: ${props => props.$isUser ? 'white' : '#B8860B'};
    font-weight: 600;
  }
  
  /* Make links stand out */
  a {
    color: ${props => props.$isUser ? 'white' : '#B8860B'};
    text-decoration: underline;
    
    &:hover {
      opacity: 0.8;
    }
  }
  
  /* Table styling for structured data */
  table {
    border-collapse: collapse;
    margin: 1rem 0;
    width: 100%;
  }
  
  th, td {
    border: 1px solid ${props => props.$isUser ? 'rgba(255, 255, 255, 0.2)' : 'var(--border-color)'};
    padding: 0.5rem;
    text-align: left;
  }
  
  th {
    background-color: ${props => props.$isUser ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
    font-weight: 600;
  }
  
  /* Improved section styling */
  h1 + p, h2 + p, h3 + p, h4 + p, h5 + p, h6 + p {
    margin-top: 0.5rem;
  }
  
  /* Better styling for multi-paragraph content */
  & > *:first-child {
    margin-top: 0;
  }
  
  & > *:last-child {
    margin-bottom: 0;
  }
  
  /* Override any markdown-generated breaks in numbered lists */
  li br {
    display: none;
  }
`;

const FeedbackContainer = styled.div`
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
  gap: 0.625rem;
  padding-left: 0.625rem;
`;

const FeedbackButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: ${props => props.$isActive ? 
    (props.$isPositive ? 'var(--success-color)' : 'var(--danger-color)') : 
    'var(--text-secondary)'};
  display: flex;
  align-items: center;
  transition: transform 0.2s, color 0.2s;
  
  &:hover {
    transform: scale(1.2);
  }
`;

const FeedbackText = styled.span`
  font-size: 0.75rem;
  color: var(--text-secondary);
`;

const FeedbackThanks = styled.span`
  font-size: 0.75rem;
  color: var(--success-color);
`;

const ChatMessage = ({ message }) => {
  const { role, content, timestamp } = message;
  const isUser = role === 'user';
  const [feedback, setFeedback] = useState(null);
  
  const handleFeedback = (isPositive) => {
    setFeedback(isPositive);
    // In a real app, you would send this feedback to your server
    console.log(`User gave ${isPositive ? 'positive' : 'negative'} feedback for message ${message.id}`);
  };
  
  return (
    <MessageContainer $isUser={isUser}>
      <MessageHeader>
        <Avatar $isUser={isUser}>
          {isUser ? <FaUser /> : <FaRobot />}
        </Avatar>
        <Name>{isUser ? 'You' : 'Assistant'}</Name>
        <Timestamp>{timestamp}</Timestamp>
      </MessageHeader>
      
      <MessageContent $isUser={isUser}>
        <ReactMarkdown>{content}</ReactMarkdown>
      </MessageContent>
      
      {!isUser && feedback === null && (
        <FeedbackContainer>
          <FeedbackText>Was this helpful?</FeedbackText>
          <FeedbackButton $isPositive={true} onClick={() => handleFeedback(true)}>
            <FaThumbsUp />
          </FeedbackButton>
          <FeedbackButton $isPositive={false} onClick={() => handleFeedback(false)}>
            <FaThumbsDown />
          </FeedbackButton>
        </FeedbackContainer>
      )}
      
      {!isUser && feedback !== null && (
        <FeedbackContainer>
          <FeedbackThanks>Thanks for your feedback!</FeedbackThanks>
        </FeedbackContainer>
      )}
    </MessageContainer>
  );
};

export default ChatMessage;