import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaEdit, FaTrash, FaPlus, FaSave, FaTimes } from 'react-icons/fa';

const AdminContainer = styled.div`
  width: 100%;
  height: 100%;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
`;

const Title = styled.h1`
  margin-bottom: 20px;
  color: var(--text-primary);
`;

const TabsContainer = styled.div`
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border);
`;

const Tab = styled.button`
  padding: 10px 20px;
  background: ${props => props.active ? 'var(--accent)' : 'transparent'};
  color: ${props => props.active ? 'white' : 'var(--text-primary)'};
  border: none;
  cursor: pointer;
  font-size: 16px;
  margin-right: 10px;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  
  &:hover {
    background: ${props => props.active ? 'var(--accent)' : 'var(--bg-hover)'};
  }
`;

const CategorySection = styled.div`
  margin-bottom: 30px;
`;

const CategoryTitle = styled.h2`
  margin-bottom: 15px;
  color: var(--text-primary);
`;

const ProcessList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const ProcessItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background-color: var(--bg-secondary);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const ProcessName = styled.div`
  font-weight: 500;
  color: var(--text-primary);
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
`;

const IconButton = styled.button`
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: var(--accent);
  }
`;

const AddButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 10px 15px;
  background-color: var(--accent);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
  
  &:hover {
    background-color: var(--accent-dark);
  }
`;

const FormContainer = styled.div`
  background-color: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const FormTitle = styled.h3`
  margin-bottom: 20px;
  color: var(--text-primary);
`;

const FormGroup = styled.div`
  margin-bottom: 15px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  color: var(--text-primary);
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 4px;
  margin-bottom: 5px;
`;

const Select = styled.select`
  width: 100%;
  padding: 10px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 4px;
  margin-bottom: 5px;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 10px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 4px;
  min-height: 100px;
  resize: vertical;
  margin-bottom: 5px;
`;

const KeywordsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
`;

const Keyword = styled.div`
  background-color: var(--accent-light);
  color: var(--accent);
  padding: 5px 10px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 5px;
  
  button {
    background: none;
    border: none;
    color: var(--accent);
    cursor: pointer;
    padding: 0;
    font-size: 12px;
    
    &:hover {
      color: var(--accent-dark);
    }
  }
`;

const AddItemButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 8px 12px;
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 4px;
  cursor: pointer;
  
  &:hover {
    background-color: var(--bg-hover);
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 20px;
`;

const SaveButton = styled.button`
  padding: 10px 20px;
  background-color: var(--accent);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  
  &:hover {
    background-color: var(--accent-dark);
  }
`;

const CancelButton = styled.button`
  padding: 10px 20px;
  background-color: var(--bg-hover);
  color: var(--text-primary);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  
  &:hover {
    background-color: var(--border);
  }
`;

const ListItem = styled.div`
  padding: 10px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 4px;
  margin-bottom: 10px;
  position: relative;
  
  button {
    position: absolute;
    top: 5px;
    right: 5px;
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    
    &:hover {
      color: var(--accent);
    }
  }
`;

const Error = styled.div`
  color: #e74c3c;
  margin-top: 10px;
  padding: 10px;
  background-color: rgba(231, 76, 60, 0.1);
  border-radius: 4px;
`;

const AdminPanel = () => {
  const [categories, setCategories] = useState([]);
  const [processes, setProcesses] = useState({});
  const [activeTab, setActiveTab] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    category: '',
    filename: '',
    title: '',
    description: '',
    keywords: [],
    steps: [],
    troubleshooting: []
  });
  
  // New keyword input
  const [newKeyword, setNewKeyword] = useState('');
  const [newStep, setNewStep] = useState('');
  const [newTroubleshooting, setNewTroubleshooting] = useState('');
  
  // Fetch categories
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('/api/admin/categories');
        if (!response.ok) {
          throw new Error(`Failed to fetch categories: ${response.status} ${response.statusText}`);
        }
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new Error(`Expected JSON response but got ${contentType}`);
        }
        const data = await response.json();
        setCategories(data);
      } catch (err) {
        console.error("Category fetch error:", err);
        setError('Error loading categories: ' + err.message);
      }
    };
    
    fetchCategories();
  }, []);
  
  // Fetch processes
  useEffect(() => {
    const fetchProcesses = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/admin/processes');
        if (!response.ok) {
          throw new Error(`Failed to fetch processes: ${response.status} ${response.statusText}`);
        }
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          throw new Error(`Expected JSON response but got ${contentType}`);
        }
        const data = await response.json();
        setProcesses(data);
      } catch (err) {
        console.error("Process fetch error:", err);
        setError('Error loading processes: ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProcesses();
  }, []);
  
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };
  
  const handleAddProcess = () => {
    setEditMode(false);
    setFormData({
      category: categories.length > 0 ? categories[0] : '',
      filename: '',
      title: '',
      description: '',
      keywords: [],
      steps: [],
      troubleshooting: []
    });
    setShowForm(true);
  };
  
  const handleEditProcess = (category, process) => {
    setEditMode(true);
    setFormData({
      category,
      filename: process.filename,
      title: process.data.title,
      description: process.data.description,
      keywords: [...process.data.keywords],
      steps: process.data.steps ? [...process.data.steps] : [],
      troubleshooting: process.data.troubleshooting ? [...process.data.troubleshooting] : []
    });
    setShowForm(true);
  };
  
  const handleDeleteProcess = async (category, filename) => {
    if (!window.confirm(`Are you sure you want to delete the process '${filename}'?`)) {
      return;
    }
    
    try {
      const response = await fetch(`/api/admin/processes/${category}/${filename}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete process');
      }
      
      // Update the processes state
      const updatedProcesses = { ...processes };
      updatedProcesses[category] = updatedProcesses[category].filter(p => p.filename !== filename);
      setProcesses(updatedProcesses);
      
    } catch (err) {
      setError('Error deleting process: ' + err.message);
    }
  };
  
  const handleAddKeyword = () => {
    if (newKeyword.trim() && !formData.keywords.includes(newKeyword.trim())) {
      // Split by commas if multiple keywords are pasted
      const keywordsToAdd = newKeyword.split(',').map(k => k.trim()).filter(k => k && !formData.keywords.includes(k));
      
      if (keywordsToAdd.length > 0) {
        setFormData({
          ...formData,
          keywords: [...formData.keywords, ...keywordsToAdd]
        });
        setNewKeyword('');
      }
    }
  };

  const handleKeywordKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddKeyword();
    }
  };

  const handleRemoveKeyword = (keyword) => {
    setFormData({
      ...formData,
      keywords: formData.keywords.filter(k => k !== keyword)
    });
  };
  
  const handleAddStep = (e) => {
    e.preventDefault();
    if (newStep.trim()) {
      setFormData(prevState => ({
        ...prevState,
        steps: [...(prevState.steps || []), newStep.trim()]
      }));
      setNewStep('');
    }
  };
  
  const handleRemoveStep = (index) => {
    const updatedSteps = [...formData.steps];
    updatedSteps.splice(index, 1);
    setFormData({
      ...formData,
      steps: updatedSteps
    });
  };
  
  const handleAddTroubleshooting = () => {
    if (newTroubleshooting.trim()) {
      setFormData({
        ...formData,
        troubleshooting: [...formData.troubleshooting, newTroubleshooting.trim()]
      });
      setNewTroubleshooting('');
    }
  };
  
  const handleRemoveTroubleshooting = (index) => {
    const updatedTroubleshooting = [...formData.troubleshooting];
    updatedTroubleshooting.splice(index, 1);
    setFormData({
      ...formData,
      troubleshooting: updatedTroubleshooting
    });
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    // Log the current state for debugging
    console.log("Submitting form with data:", {
      category: formData.category,
      filename: formData.filename,
      title: formData.title,
      description: formData.description,
      keywords: formData.keywords,
      keywordsLength: formData.keywords.length
    });
    
    // Enhanced validation with better error messages
    const missingFields = [];
    if (!formData.category) missingFields.push('Category');
    if (!formData.filename) missingFields.push('Filename');
    if (!formData.title) missingFields.push('Title');
    if (!formData.description) missingFields.push('Description');
    if (!formData.keywords || formData.keywords.length === 0) missingFields.push('at least one Keyword');
    
    if (missingFields.length > 0) {
      setError(`Please fill in all required fields: ${missingFields.join(', ')}`);
      return;
    }
    
    // Ensure steps array exists
    const processData = {
      title: formData.title,
      description: formData.description,
      keywords: formData.keywords,
      steps: formData.steps || [],
      troubleshooting: formData.troubleshooting || []
    };
    
    try {
      const url = editMode 
        ? `/api/admin/processes/${formData.category}/${formData.filename}` 
        : '/api/admin/processes';
        
      const requestBody = editMode ? processData : {
        category: formData.category,
        filename: formData.filename,
        data: processData
      };
      
      console.log("Submitting request to:", url);
      console.log("Request body:", requestBody);
      
      const response = await fetch(url, {
        method: editMode ? 'PUT' : 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
      
      let responseData;
      try {
        responseData = await response.json();
      } catch (err) {
        throw new Error('Invalid response from server');
      }
      
      if (!response.ok) {
        throw new Error(responseData.error || `Server error: ${response.status}`);
      }
      
      console.log("Server response:", responseData);
      
      // Success! Refresh the process list
      const processesResponse = await fetch('/api/admin/processes');
      if (!processesResponse.ok) {
        throw new Error('Failed to refresh process list');
      }
      
      const newProcesses = await processesResponse.json();
      setProcesses(newProcesses);
      
      // Reset form and close
      setShowForm(false);
      setError(null);
      
      // Reset form data
      setFormData({
        category: '',
        filename: '',
        title: '',
        description: '',
        keywords: [],
        steps: [],
        troubleshooting: []
      });
      
    } catch (err) {
      console.error("Submission error:", err);
      setError(`Error: ${err.message}`);
    }
  };
  
  const handleCancel = () => {
    setShowForm(false);
    setError(null);
  };
  
  // Filter processes based on active tab
  const filteredProcesses = activeTab === 'all' ? processes : { [activeTab]: processes[activeTab] || [] };
  
  if (loading) {
    return (
      <AdminContainer>
        <Title>Process Management</Title>
        <div>Loading...</div>
      </AdminContainer>
    );
  }
  
  return (
    <AdminContainer>
      <Title>Process Management</Title>
      
      <TabsContainer>
        <Tab 
          active={activeTab === 'all'} 
          onClick={() => handleTabChange('all')}
        >
          All Categories
        </Tab>
        {categories.map(category => (
          <Tab 
            key={category}
            active={activeTab === category} 
            onClick={() => handleTabChange(category)}
          >
            {category.replace(/_/g, ' ')}
          </Tab>
        ))}
      </TabsContainer>
      
      {!showForm && (
        <AddButton onClick={handleAddProcess}>
          <FaPlus /> Add New Process
        </AddButton>
      )}
      
      {error && <Error>{error}</Error>}
      
      {showForm && (
        <FormContainer>
          <FormTitle>{editMode ? 'Edit Process' : 'Add New Process'}</FormTitle>
          
          <FormGroup>
            <Label>Category *</Label>
            <Select 
              name="category" 
              value={formData.category}
              onChange={handleInputChange}
              disabled={editMode}
            >
              <option value="" disabled>Select a category</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.replace(/_/g, ' ')}
                </option>
              ))}
            </Select>
            <small style={{ display: 'block', marginTop: '5px', color: 'var(--text-secondary)' }}>
              This is a dropdown - select from existing categories
            </small>
          </FormGroup>
          
          <FormGroup>
            <Label>Filename (without extension) *</Label>
            <Input 
              type="text" 
              name="filename" 
              value={formData.filename}
              onChange={handleInputChange}
              disabled={editMode}
              placeholder="e.g., upload_asset"
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Title *</Label>
            <Input 
              type="text" 
              name="title" 
              value={formData.title}
              onChange={handleInputChange}
              placeholder="e.g., Upload Asset"
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Description *</Label>
            <TextArea 
              name="description" 
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe the process..."
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Keywords * (Enter keyword and click Add or press Enter)</Label>
            <KeywordsContainer>
              {formData.keywords.map((keyword, index) => (
                <Keyword key={index}>
                  {keyword}
                  <button onClick={() => handleRemoveKeyword(keyword)}>
                    <FaTimes />
                  </button>
                </Keyword>
              ))}
            </KeywordsContainer>
            <div style={{ display: 'flex', gap: '10px' }}>
              <Input 
                type="text" 
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyPress={handleKeywordKeyPress}
                placeholder="Type keyword and press Enter or click Add"
              />
              <AddItemButton onClick={handleAddKeyword}>
                <FaPlus /> Add
              </AddItemButton>
            </div>
            {formData.keywords.length === 0 && (
              <small style={{ color: 'var(--text-secondary)', marginTop: '5px', display: 'block' }}>
                Add at least one keyword to save the process
              </small>
            )}
          </FormGroup>
          
          <FormGroup>
            <Label>Steps</Label>
            {formData.steps.map((step, index) => (
              <ListItem key={index}>
                {step}
                <button onClick={() => handleRemoveStep(index)}>
                  <FaTimes />
                </button>
              </ListItem>
            ))}
            <div style={{ display: 'flex', gap: '10px' }}>
              <TextArea 
                value={newStep}
                onChange={(e) => setNewStep(e.target.value)}
                placeholder="Add a step"
              />
              <AddItemButton onClick={handleAddStep}>
                <FaPlus /> Add
              </AddItemButton>
            </div>
          </FormGroup>
          
          <FormGroup>
            <Label>Troubleshooting</Label>
            {formData.troubleshooting.map((item, index) => (
              <ListItem key={index}>
                {item}
                <button onClick={() => handleRemoveTroubleshooting(index)}>
                  <FaTimes />
                </button>
              </ListItem>
            ))}
            <div style={{ display: 'flex', gap: '10px' }}>
              <TextArea 
                value={newTroubleshooting}
                onChange={(e) => setNewTroubleshooting(e.target.value)}
                placeholder="Add a troubleshooting tip"
              />
              <AddItemButton onClick={handleAddTroubleshooting}>
                <FaPlus /> Add
              </AddItemButton>
            </div>
          </FormGroup>
          
          <ButtonContainer>
            <SaveButton onClick={handleSubmit}>
              <FaSave /> Save Process
            </SaveButton>
            <CancelButton onClick={handleCancel}>
              <FaTimes /> Cancel
            </CancelButton>
          </ButtonContainer>
        </FormContainer>
      )}
      
      {Object.entries(filteredProcesses).map(([category, categoryProcesses]) => (
        <CategorySection key={category}>
          <CategoryTitle>{category.replace(/_/g, ' ')}</CategoryTitle>
          <ProcessList>
            {categoryProcesses && categoryProcesses.length > 0 ? (
              categoryProcesses.map((process, index) => (
                <ProcessItem key={index}>
                  <ProcessName>{process.data.title}</ProcessName>
                  <ButtonGroup>
                    <IconButton onClick={() => handleEditProcess(category, process)}>
                      <FaEdit />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteProcess(category, process.filename)}>
                      <FaTrash />
                    </IconButton>
                  </ButtonGroup>
                </ProcessItem>
              ))
            ) : (
              <div>No processes found in this category</div>
            )}
          </ProcessList>
        </CategorySection>
      ))}
    </AdminContainer>
  );
};

export default AdminPanel;
