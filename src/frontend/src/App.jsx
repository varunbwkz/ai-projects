import React, { useState, useEffect } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import AdminPanel from './components/AdminPanel';
import { ThemeContext } from './context/ThemeContext';
import { ChatProvider } from './context/ChatContext';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-primary);
  color: var(--text-primary);
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check if dark mode was previously enabled
    const savedTheme = localStorage.getItem('brandworkz-theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  }, []);

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    
    // Update document theme attribute
    document.documentElement.setAttribute(
      'data-theme',
      newMode ? 'dark' : 'light'
    );
    
    // Save preference to localStorage
    localStorage.setItem('brandworkz-theme', newMode ? 'dark' : 'light');
  };

  return (
    <Router>
      <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
        <ChatProvider>
          <AppContainer>
            <Header />
            <MainContent>
              <Routes>
                <Route path="/" element={<ChatContainer />} />
                <Route path="/admin" element={<AdminPanel />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </MainContent>
          </AppContainer>
        </ChatProvider>
      </ThemeContext.Provider>
    </Router>
  );
}

export default App;
