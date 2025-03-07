import React, { useContext, useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FaRocket, FaMoon, FaSun, FaDownload, FaTrash, FaCog } from 'react-icons/fa';
import { ThemeContext } from '../context/ThemeContext';
import { useChat } from '../context/ChatContext';
import { Link, useLocation } from 'react-router-dom';

const HeaderContainer = styled.header`
  background-color: var(--primary-color);
  color: white;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: bold;
  text-decoration: none;
  color: white;
  
  svg {
    font-size: 1.5rem;
  }
  
  &:hover {
    opacity: 0.9;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 0.75rem;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
`;

const ExportMenu = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 5px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  z-index: 100;
  display: ${props => props.isOpen ? 'block' : 'none'};
  min-width: 150px;
  margin-top: 5px;
`;

const ExportOption = styled.div`
  padding: 10px 16px;
  cursor: pointer;
  color: var(--text-primary);
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background-color: var(--primary-color);
    color: white;
  }
`;

const NavLink = styled(Link)`
  margin-left: 20px;
  color: var(--text-primary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  
  &:hover {
    background-color: var(--bg-hover);
  }
  
  &.active {
    background-color: var(--accent-light);
    color: var(--accent);
  }
`;

const ThemeToggle = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
`;

const Header = () => {
  const { isDarkMode, toggleTheme } = useContext(ThemeContext);
  const { clearChat, exportChat } = useChat();
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const exportMenuRef = useRef(null);
  const location = useLocation();

  // Close the export menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target)) {
        setExportMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleExportClick = () => {
    setExportMenuOpen(!exportMenuOpen);
  };

  const handleExportFormat = (format) => {
    exportChat(format);
    setExportMenuOpen(false);
  };

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo to="/">
          <FaRocket />
          <span>Brandworkz AI Assistant</span>
        </Logo>
        <ActionButtons>
          <NavLink 
            to="/admin" 
            className={location.pathname === '/admin' ? 'active' : ''}
          >
            <FaCog /> Admin
          </NavLink>
          <ThemeToggle onClick={toggleTheme}>
            {isDarkMode ? <FaSun /> : <FaMoon />}
          </ThemeToggle>
          <div style={{ position: 'relative' }} ref={exportMenuRef}>
            <Button onClick={handleExportClick}>
              <FaDownload />
              Export Chat
            </Button>
            <ExportMenu isOpen={exportMenuOpen}>
              <ExportOption onClick={() => handleExportFormat('pdf')}>PDF Format</ExportOption>
              <ExportOption onClick={() => handleExportFormat('doc')}>DOC Format</ExportOption>
              <ExportOption onClick={() => handleExportFormat('md')}>Markdown Format</ExportOption>
            </ExportMenu>
          </div>
          <Button onClick={clearChat}>
            <FaTrash />
            Clear Chat
          </Button>
        </ActionButtons>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;
