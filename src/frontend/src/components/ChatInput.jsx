import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FaPaperPlane } from 'react-icons/fa';

const InputContainer = styled.form`
  display: flex;
  align-items: flex-end;
  gap: 0.625rem;
`;

const StyledTextarea = styled.textarea`
  flex: 1;
  border-radius: 1.25rem;
  padding: 0.75rem 1rem;
  resize: none;
  border: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9375rem;
  line-height: 1.5;
  min-height: 3.25rem;
  max-height: 10rem;
  overflow-y: auto;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.25);
  }
  
  &::placeholder {
    color: var(--text-secondary);
  }
`;

const SendButton = styled.button`
  width: 3.125rem;
  height: 3.125rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-color);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  
  &:hover {
    background-color: var(--primary-color-dark, #0b5ed7);
    transform: translateY(-2px);
  }
  
  &:disabled {
    background-color: var(--text-secondary);
    cursor: not-allowed;
    transform: none;
  }
`;

const ChatInput = ({ value, onChange, onSubmit, disabled }) => {
  const textareaRef = useRef(null);
  
  useEffect(() => {
    if (textareaRef.current) {
      // Auto-resize the textarea based on content
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [value]);
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };
  
  return (
    <InputContainer onSubmit={onSubmit}>
      <StyledTextarea 
        ref={textareaRef}
        value={value}
        onChange={onChange}
        onKeyDown={handleKeyDown}
        placeholder="Type your message here..."
        disabled={disabled}
        rows={1}
      />
      <SendButton type="submit" disabled={disabled || !value.trim()}>
        <FaPaperPlane />
      </SendButton>
    </InputContainer>
  );
};

export default ChatInput;
