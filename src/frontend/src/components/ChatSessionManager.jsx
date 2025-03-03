import React, { useState } from 'react';
import styled from 'styled-components';
import { MdAdd, MdClose, MdEdit, MdCheck, MdClear } from 'react-icons/md';
import { useChat } from '../context/ChatContext';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  border-bottom: 1px solid var(--border-color);
`;

const TabsContainer = styled.div`
  display: flex;
  overflow-x: auto;
  background-color: var(--bg-secondary);
  padding: 0.25rem 0.25rem 0;
  
  &::-webkit-scrollbar {
    height: 0.375rem;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--bg-secondary);
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: var(--primary-color);
    border-radius: 0.3125rem;
  }
`;

const Tab = styled.div`
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background-color: ${props => props.isActive ? 'var(--primary-color)' : 'var(--bg-primary)'};
  color: ${props => props.isActive ? 'white' : 'var(--text-primary)'};
  border-top-left-radius: 0.375rem;
  border-top-right-radius: 0.375rem;
  margin-right: 0.25rem;
  cursor: pointer;
  white-space: nowrap;
  min-width: 7.5rem;
  max-width: 12.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: ${props => props.isActive ? 'var(--primary-color)' : 'var(--primary-color-light)'};
  }
`;

const TabName = styled.span`
  margin-right: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const TabInput = styled.input`
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--primary-color);
  border-radius: 0.25rem;
  padding: 0.25rem;
  margin-right: 0.5rem;
  font-size: 0.875rem;
  width: 7.5rem;
`;

const TabActions = styled.div`
  display: flex;
  align-items: center;
  margin-left: auto;
`;

const ActionButton = styled.button`
  background: transparent;
  border: none;
  color: ${props => props.isActive ? 'white' : 'var(--text-primary)'};
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: ${props => props.isActive ? 'white' : 'var(--primary-color)'};
  }
  
  & > svg {
    font-size: 1rem;
  }
`;

const NewChatButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.75rem;
  background-color: var(--primary-color-light);
  color: #5a189a;
  font-weight: 700;
  border: none;
  border-top-left-radius: 0.375rem;
  border-top-right-radius: 0.375rem;
  cursor: pointer;
  white-space: nowrap;
  font-size: 0.875rem;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: var(--primary-color);
    color: white;
  }
  
  & > svg {
    margin-right: 0.25rem;
    font-size: 1rem;
    color: #5a189a;
  }
`;

const ChatSessionManager = () => {
  const { 
    chatSessions, 
    currentChatId, 
    createNewChat, 
    switchChat, 
    renameChat, 
    deleteChat 
  } = useChat();
  
  const [editingTabId, setEditingTabId] = useState(null);
  const [newTabName, setNewTabName] = useState('');
  
  const handleEditTab = (chatId, currentName) => {
    setEditingTabId(chatId);
    setNewTabName(currentName);
  };
  
  const handleSaveTabName = (chatId) => {
    if (newTabName.trim()) {
      renameChat(chatId, newTabName.trim());
    }
    setEditingTabId(null);
    setNewTabName('');
  };
  
  const handleKeyDown = (e, chatId) => {
    if (e.key === 'Enter') {
      handleSaveTabName(chatId);
    } else if (e.key === 'Escape') {
      setEditingTabId(null);
      setNewTabName('');
    }
  };
  
  return (
    <Container>
      <TabsContainer>
        {Object.values(chatSessions).map((session) => (
          <Tab 
            key={session.id} 
            isActive={session.id === currentChatId}
            onClick={() => switchChat(session.id)}
          >
            {editingTabId === session.id ? (
              <>
                <TabInput 
                  value={newTabName}
                  onChange={(e) => setNewTabName(e.target.value)}
                  onKeyDown={(e) => handleKeyDown(e, session.id)}
                  autoFocus
                />
                <ActionButton 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSaveTabName(session.id);
                  }}
                  isActive={session.id === currentChatId}
                >
                  <MdCheck />
                </ActionButton>
                <ActionButton 
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingTabId(null);
                  }}
                  isActive={session.id === currentChatId}
                >
                  <MdClear />
                </ActionButton>
              </>
            ) : (
              <>
                <TabName>{session.name}</TabName>
                <TabActions>
                  <ActionButton 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditTab(session.id, session.name);
                    }}
                    isActive={session.id === currentChatId}
                  >
                    <MdEdit />
                  </ActionButton>
                  {Object.keys(chatSessions).length > 1 && (
                    <ActionButton 
                      onClick={(e) => {
                        e.stopPropagation();
                        if (window.confirm('Are you sure you want to close this chat?')) {
                          deleteChat(session.id);
                        }
                      }}
                      isActive={session.id === currentChatId}
                    >
                      <MdClose />
                    </ActionButton>
                  )}
                </TabActions>
              </>
            )}
          </Tab>
        ))}
        <NewChatButton onClick={createNewChat}>
          <MdAdd />
          New Chat
        </NewChatButton>
      </TabsContainer>
    </Container>
  );
};

export default ChatSessionManager; 