import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

// Create the context
const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  // Initialize with saved messages or default welcome message
  const [messages, setMessages] = useState(() => {
    const savedMessages = localStorage.getItem('brandworkz-chat-messages');
    if (savedMessages) {
      try {
        return JSON.parse(savedMessages);
      } catch (error) {
        console.error('Error parsing saved messages:', error);
      }
    }
    return [
      {
        id: 'welcome',
        role: 'assistant',
        content: "Hello! I'm your Brandworkz AI Assistant. I can provide step-by-step guides for common Brandworkz processes. Please ask me how to perform a specific task or ask any questions you have about Brandworkz.",
        timestamp: new Date().toLocaleTimeString()
      }
    ];
  });
  
  // Current active chat ID (used for multiple chat windows)
  const [currentChatId, setCurrentChatId] = useState(() => {
    const savedChatId = localStorage.getItem('brandworkz-current-chat-id');
    return savedChatId || 'default';
  });
  
  // All chat sessions (multiple windows)
  const [chatSessions, setChatSessions] = useState(() => {
    const savedSessions = localStorage.getItem('brandworkz-chat-sessions');
    if (savedSessions) {
      try {
        return JSON.parse(savedSessions);
      } catch (error) {
        console.error('Error parsing saved chat sessions:', error);
      }
    }
    return {
      default: {
        id: 'default',
        name: 'Main Chat',
        messages: messages,
        createdAt: new Date().toISOString()
      }
    };
  });

  const [isLoading, setIsLoading] = useState(false);
  
  // Persist messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('brandworkz-chat-messages', JSON.stringify(messages));
    
    // Also update the current chat session's messages
    setChatSessions(prevSessions => {
      const updatedSessions = {
        ...prevSessions,
        [currentChatId]: {
          ...prevSessions[currentChatId],
          messages: messages
        }
      };
      localStorage.setItem('brandworkz-chat-sessions', JSON.stringify(updatedSessions));
      return updatedSessions;
    });
  }, [messages, currentChatId]);
  
  // Persist current chat ID whenever it changes
  useEffect(() => {
    localStorage.setItem('brandworkz-current-chat-id', currentChatId);
  }, [currentChatId]);

  const addMessage = (role, content) => {
    const newMessage = {
      id: `msg-${Date.now()}`,
      role,
      content,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prevMessages => [...prevMessages, newMessage]);
    return newMessage.id;
  };

  const sendMessage = async (message) => {
    if (!message.trim()) return;
    
    // Add user message to chat
    addMessage('user', message);
    
    // Set loading state
    setIsLoading(true);
    
    try {
      // Send message to API
      const response = await axios.post('/api/chat', { message });
      
      if (response.data.success) {
        addMessage('assistant', response.data.response);
      } else {
        addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getProcessInstructions = async (processName) => {
    // Set loading state
    setIsLoading(true);
    
    // Add process request to chat
    addMessage('user', `How to ${processName.replace('_', ' ')}?`);
    
    try {
      // Send process request to API
      const response = await axios.post('/api/process', { process_name: processName });
      
      if (response.data.success) {
        addMessage('assistant', response.data.response);
        return response.data.response;
      } else {
        const errorMsg = 'Sorry, I couldn\'t find instructions for that process.';
        addMessage('assistant', errorMsg);
        return errorMsg;
      }
    } catch (error) {
      console.error('Error getting process instructions:', error);
      const errorMsg = 'Sorry, I encountered an error while retrieving process instructions.';
      addMessage('assistant', errorMsg);
      return errorMsg;
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    const welcomeMessage = {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I'm your Brandworkz AI Assistant. I can provide step-by-step guides for common Brandworkz processes. Please ask me how to perform a specific task or ask any questions you have about Brandworkz.",
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages([welcomeMessage]);
  };
  
  // New functions for multiple chat windows
  const createNewChat = () => {
    const newChatId = `chat-${Date.now()}`;
    const welcomeMessage = {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I'm your Brandworkz AI Assistant. I can provide step-by-step guides for common Brandworkz processes. Please ask me how to perform a specific task or ask any questions you have about Brandworkz.",
      timestamp: new Date().toLocaleTimeString()
    };
    
    setChatSessions(prevSessions => {
      const updatedSessions = {
        ...prevSessions,
        [newChatId]: {
          id: newChatId,
          name: `Chat ${Object.keys(prevSessions).length + 1}`,
          messages: [welcomeMessage],
          createdAt: new Date().toISOString()
        }
      };
      localStorage.setItem('brandworkz-chat-sessions', JSON.stringify(updatedSessions));
      return updatedSessions;
    });
    
    // Switch to the new chat
    switchChat(newChatId);
    
    return newChatId;
  };
  
  const switchChat = (chatId) => {
    if (chatSessions[chatId]) {
      setCurrentChatId(chatId);
      setMessages(chatSessions[chatId].messages);
    }
  };
  
  const renameChat = (chatId, newName) => {
    if (chatSessions[chatId]) {
      setChatSessions(prevSessions => {
        const updatedSessions = {
          ...prevSessions,
          [chatId]: {
            ...prevSessions[chatId],
            name: newName
          }
        };
        localStorage.setItem('brandworkz-chat-sessions', JSON.stringify(updatedSessions));
        return updatedSessions;
      });
    }
  };
  
  const deleteChat = (chatId) => {
    if (chatSessions[chatId]) {
      setChatSessions(prevSessions => {
        const updatedSessions = { ...prevSessions };
        delete updatedSessions[chatId];
        localStorage.setItem('brandworkz-chat-sessions', JSON.stringify(updatedSessions));
        return updatedSessions;
      });
      
      // If the deleted chat was the current one, switch to another chat
      if (chatId === currentChatId) {
        const remainingChatIds = Object.keys(chatSessions).filter(id => id !== chatId);
        if (remainingChatIds.length > 0) {
          switchChat(remainingChatIds[0]);
        } else {
          // If no chats remain, create a new one
          createNewChat();
        }
      }
    }
  };

  const exportChat = (format = 'pdf') => {
    // Create a text version of the conversation
    let conversationText = "# Brandworkz AI Assistant Conversation\n\n";
    
    messages.forEach(message => {
      const role = message.role === 'user' ? 'You' : 'Assistant';
      conversationText += `## ${role} (${message.timestamp})\n\n${message.content}\n\n`;
    });

    // Set filename with current date/time
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    
    if (format === 'pdf') {
      // PDF export
      import('jspdf').then(({ default: jsPDF }) => {
        // Create a new PDF document
        const doc = new jsPDF({
          orientation: 'portrait',
          unit: 'mm',
          format: 'a4',
          putOnlyUsedFonts: true,
          compress: true
        });
        
        // Set document properties
        doc.setProperties({
          title: 'Brandworkz AI Assistant Conversation',
          subject: 'Chat Export',
          creator: 'Brandworkz AI Assistant',
          author: 'Brandworkz'
        });
        
        // Define margins and dimensions
        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();
        const margin = {
          left: 20,
          right: 20,
          top: 20,
          bottom: 25
        };
        const textWidth = pageWidth - margin.left - margin.right;
        
        // Font settings
        const normalFontSize = 11;
        const titleFontSize = 16;
        const headingFontSize = 14;
        const footerFontSize = 9;
        
        // Line height calculations
        const normalLineHeight = normalFontSize * 0.5;
        const titleLineHeight = titleFontSize * 0.5;
        const headingLineHeight = headingFontSize * 0.5;
        
        // Start at the top margin
        let y = margin.top;
        let currentPage = 1;
        
        // Function to add a new page
        const addNewPage = () => {
          doc.addPage();
          currentPage++;
          y = margin.top;
          // Add footer with page number
          addFooter(currentPage);
        };
        
        // Function to add footer with page number
        const addFooter = (pageNum) => {
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(footerFontSize);
          doc.setTextColor(100, 100, 100);
          doc.text(`Page ${pageNum}`, pageWidth / 2, pageHeight - margin.bottom / 2, { align: 'center' });
          doc.setTextColor(0, 0, 0);
        };
        
        // Add title to first page
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(titleFontSize);
        doc.text('Brandworkz AI Assistant Conversation', margin.left, y);
        y += titleLineHeight + 5;
        
        // Add date
        doc.setFont('helvetica', 'italic');
        doc.setFontSize(normalFontSize);
        doc.text(`Generated on: ${new Date().toLocaleString()}`, margin.left, y);
        y += normalLineHeight + 10;
        
        // Add footer to first page
        addFooter(currentPage);
        
        // Process each message
        messages.forEach(message => {
          const role = message.role === 'user' ? 'You' : 'Assistant';
          const timestamp = message.timestamp;
          const content = message.content;
          
          // Check if we need a new page for this message
          if (y > pageHeight - margin.bottom - 30) {
            addNewPage();
          }
          
          // Add message header
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(headingFontSize);
          doc.text(`${role} (${timestamp})`, margin.left, y);
          y += headingLineHeight + 5;
          
          // Process the message content
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(normalFontSize);
          
          // Split content by paragraphs
          const paragraphs = content.split('\n\n');
          
          // Process each paragraph
          paragraphs.forEach(paragraph => {
            if (!paragraph.trim()) return;
            
            // Clean the paragraph text of any special characters
            const cleanParagraph = paragraph.replace(/[^\x20-\x7E]/g, '');
            
            // Handle markdown headers within content
            let processedText = cleanParagraph;
            let isBold = false;
            
            if (cleanParagraph.startsWith('### ')) {
              processedText = cleanParagraph.substring(4);
              doc.setFont('helvetica', 'bold');
              isBold = true;
            } else if (cleanParagraph.startsWith('## ')) {
              processedText = cleanParagraph.substring(3);
              doc.setFont('helvetica', 'bold');
              isBold = true;
            } else if (cleanParagraph.startsWith('# ')) {
              processedText = cleanParagraph.substring(2);
              doc.setFont('helvetica', 'bold');
              isBold = true;
            }
            
            // Split text to fit within margins
            const wrappedText = doc.splitTextToSize(processedText, textWidth);
            
            // Check if we need a new page
            const estimatedHeight = wrappedText.length * (normalFontSize * 0.5 + 2);
            if (y + estimatedHeight > pageHeight - margin.bottom) {
              addNewPage();
            }
            
            // Add the wrapped text
            wrappedText.forEach((line, index) => {
              doc.text(line, margin.left, y);
              y += normalLineHeight + 2;
              
              // Check if we need a new page
              if (y > pageHeight - margin.bottom - normalLineHeight) {
                addNewPage();
              }
            });
            
            // Reset to normal font if we changed it
            if (isBold) {
              doc.setFont('helvetica', 'normal');
            }
            
            // Add spacing between paragraphs
            y += 4;
          });
          
          // Add space between messages
          y += 8;
        });
        
        // Save the PDF
        doc.save(`brandworkz-conversation-${dateStr}.pdf`);
      }).catch(error => {
        console.error("Error loading jsPDF:", error);
        alert("Failed to generate PDF. Falling back to Markdown export.");
        // Fall back to markdown if PDF generation fails
        exportMarkdown(conversationText, dateStr);
      });
    } 
    else if (format === 'doc') {
      // DOC export
      import('docx').then(({ Document, Packer, Paragraph, TextRun, HeadingLevel }) => {
        // Create an array to hold all paragraphs
        const docxParagraphs = [];
        
        // Add title
        docxParagraphs.push(
          new Paragraph({
            text: "Brandworkz AI Assistant Conversation",
            heading: HeadingLevel.HEADING_1,
            spacing: { after: 200 }
          })
        );
        
        // Process each message
        messages.forEach(message => {
          const role = message.role === 'user' ? 'You' : 'Assistant';
          
          // Add message header
          docxParagraphs.push(
            new Paragraph({
              text: `${role} (${message.timestamp})`,
              heading: HeadingLevel.HEADING_2,
              spacing: { before: 200, after: 100 }
            })
          );
          
          // Split message content by paragraphs and add each
          const contentParagraphs = message.content.split('\n\n');
          contentParagraphs.forEach(para => {
            if (para.trim()) {
              docxParagraphs.push(
                new Paragraph({
                  children: [new TextRun(para)],
                  spacing: { after: 100 }
                })
              );
            }
          });
        });
        
        // Create the document with the paragraphs
        const doc = new Document({
          sections: [{
            properties: {},
            children: docxParagraphs
          }]
        });

        // Generate the .docx file
        Packer.toBlob(doc).then(blob => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `brandworkz-conversation-${dateStr}.docx`;
          a.click();
          URL.revokeObjectURL(url);
        });
      }).catch(error => {
        console.error("Error loading docx library:", error);
        alert("Failed to generate DOC. Falling back to Markdown export.");
        // Fall back to markdown if DOC generation fails
        exportMarkdown(conversationText, dateStr);
      });
    } 
    else {
      // Default Markdown export
      exportMarkdown(conversationText, dateStr);
    }
  };

  // Helper function for Markdown export
  const exportMarkdown = (content, dateStr) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `brandworkz-conversation-${dateStr}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Using React.createElement instead of JSX
  return React.createElement(
    ChatContext.Provider,
    { value: {
      messages,
      isLoading,
      sendMessage,
      getProcessInstructions,
      clearChat,
      exportChat,
      // New values for multiple chat windows
      chatSessions,
      currentChatId,
      createNewChat,
      switchChat,
      renameChat,
      deleteChat
    } },
    children
  );
};

export const useChat = () => useContext(ChatContext);

export default ChatContext;
