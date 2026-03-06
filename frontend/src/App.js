import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import LoginPage from './LoginPage';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [tables, setTables] = useState([]);
  const [sqlInput, setSqlInput] = useState('SELECT * FROM users LIMIT 10;');
  const [output, setOutput] = useState({
    type: 'info',
    message: 'Type your SQL query and press Ctrl+Enter',
    data: null
  });
  const [stats, setStats] = useState('Ready');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadTable, setUploadTable] = useState('');
  const [uploadSheet, setUploadSheet] = useState('');
  const [uploading, setUploading] = useState(false);
  
  const [terminalHeight, setTerminalHeight] = useState(60);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);
  
  // NEW: Hamburger menu state
  const [showCommandSidebar, setShowCommandSidebar] = useState(false);
  const [expandedSection, setExpandedSection] = useState('table');
  
  const backendUrl = 'https://litesql.onrender.com';

  // Command sections data
  const commandSections = {
    table: {
      title: '📋 Table Management',
      commands: [
        { name: 'CREATE TABLE', syntax: 'CREATE TABLE users (id INT, name STR)', hint: 'Add HASH/BTREE/NONE after type' },
        { name: 'DROP TABLE', syntax: 'DROP users' },
        { name: 'ADD COLUMNS', syntax: 'ADD COLUMNS INTO users (email STR HASH)' },
        { name: 'SHOW INDEXES', syntax: 'SHOW PICKLE FILE OF users' }
      ]
    },
    data: {
      title: '📊 Data Operations',
      commands: [
        { name: 'INSERT', syntax: "INSERT INTO users VALUES (1, 'Alice', 25)" },
        { name: 'SELECT', syntax: 'SELECT * FROM users' },
        { name: 'WHERE', syntax: 'SELECT * FROM users WHERE age > 25' },
        { name: 'UPDATE', syntax: "UPDATE users SET age = 26 WHERE name = 'Alice'" },
        { name: 'DELETE', syntax: 'DELETE FROM users WHERE id = 1' }
      ]
    },
    query: {
      title: '🔍 Query Features',
      commands: [
        { name: 'ORDER BY', syntax: 'SELECT * FROM users ORDER BY age DESC' },
        { name: 'LIMIT', syntax: 'SELECT * FROM users LIMIT 10' },
        { name: 'OFFSET', syntax: 'SELECT * FROM users LIMIT 10 OFFSET 5' },
        { name: 'GROUP BY', syntax: 'SELECT age, COUNT(*) FROM users GROUP BY age' },
        { name: 'DISTINCT', syntax: 'SELECT DISTINCT ON (age) * FROM users' }
      ]
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('session_token');
    const username = localStorage.getItem('username');
    
    if (token && username) {
      setIsLoggedIn(true);
      setCurrentUser({ username, session_token: token });
      loadTables(token);
    }
  }, []);

  const handleLogin = (loginData) => {
    localStorage.setItem('session_token', loginData.session_token);
    localStorage.setItem('username', loginData.username);
    setIsLoggedIn(true);
    setCurrentUser(loginData);
    loadTables(loginData.session_token);
  };

  const handleLogout = () => {
    localStorage.removeItem('session_token');
    localStorage.removeItem('username');
    setIsLoggedIn(false);
    setCurrentUser(null);
    setTables([]);
  };

  const loadTables = async (token) => {
    try {
      const response = await fetch(`${backendUrl}/api/query/tables`, {
        headers: { 'Authorization': token || localStorage.getItem('session_token') }
      });
      const result = await response.json();
      
      if (result.success && result.tables) {
        const tablesWithActive = result.tables.map((table, index) => ({
          ...table,
          active: index === 0
        }));
        setTables(tablesWithActive);
        setIsConnected(true);
      } else {
        setTables([]);
      }
    } catch (error) {
      console.error('Failed to load tables:', error);
      setIsConnected(false);
    }
  };

  const selectTable = (tableName) => {
    setTables(prevTables => 
      prevTables.map(table => ({
        ...table,
        active: table.name === tableName
      }))
    );
    setSqlInput(`SELECT * FROM ${tableName} LIMIT 100;`);
  };

  const executeQuery = async () => {
    const sql = sqlInput.trim();
    
    if (!sql) {
      showMessage('Please enter a SQL query', 'error');
      return;
    }
    
    setIsLoading(true);
    showMessage('Executing query...', 'info');
    
    try {
      const response = await fetch(`${backendUrl}/api/query`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': localStorage.getItem('session_token')
        },
        body: JSON.stringify({ sql })
      });
      
      const result = await response.json();
      
      if (result.error) {
        showMessage(result.error, 'error');
        setStats('Error');
      } else if (result.data) {
        if (Array.isArray(result.data)) {
          if (result.data.length > 0) {
            setOutput({ type: 'data', data: result.data, columns: result.columns });
            setStats(`${result.data.length} rows • ${result.executionTime}ms`);
          } else {
            showMessage('No data found', 'info');
            setStats(`Success • ${result.executionTime}ms`);
          }
        } else if (typeof result.data === 'object' && result.data !== null) {
          setOutput({ type: 'data', data: result.data });
          setStats(`Success • ${result.executionTime}ms`);
        }
      } else if (result.message) {
        showMessage(result.message, 'success');
        setStats(`Success • ${result.executionTime}ms`);
        
        if (sql.toUpperCase().includes('CREATE') || 
            sql.toUpperCase().includes('DROP') || 
            sql.toUpperCase().includes('ADD COLUMNS')) {
          setTimeout(() => loadTables(), 500);
        }
      } else {
        showMessage('Query executed successfully', 'success');
        setStats('Success');
      }
      
    } catch (error) {
      showMessage(`Connection error: ${error.message}`, 'error');
      setStats('Error');
    } finally {
      setIsLoading(false);
    }
  };

  const showMessage = (message, type = 'info') => {
    setOutput({ type, message, data: null });
  };

  const formatSQL = () => {
    let sql = sqlInput;
    const keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY'];
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      sql = sql.replace(regex, '\n' + keyword);
    });
    setSqlInput(sql.trim());
  };

  const clearTerminal = () => {
    setSqlInput('');
  };

  const toggleCommandSidebar = () => {
    setShowCommandSidebar(!showCommandSidebar);
  };

  const copyCommand = (syntax) => {
    navigator.clipboard.writeText(syntax);
    showMessage(`Copied: ${syntax}`, 'success');
    setShowCommandSidebar(false); // Close sidebar after copy
  };

  useEffect(() => {
    const handleKeyPress = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        executeQuery();
      }
    };
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sqlInput]);

  const handleFileUpload = async () => {
    if (!uploadFile || !uploadTable) {
      alert('Please select file and enter table name');
      return;
    }
    
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('table', uploadTable);
      
      if ((uploadFile.name.endsWith('.xlsx') || uploadFile.name.endsWith('.xls')) && uploadSheet) {
        formData.append('sheet', uploadSheet);
      }
      
      const response = await fetch(`${backendUrl}/api/upload`, {
        method: 'POST',
        headers: { 'Authorization': localStorage.getItem('session_token') },
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`✅ ${result.message}`);
        setUploadFile(null);
        setUploadTable('');
        setUploadSheet('');
        document.getElementById('fileInput').value = '';
        loadTables();
      } else {
        alert(`❌ ${result.error}`);
      }
    } catch (error) {
      alert(`❌ Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging || !containerRef.current) return;
      
      const container = containerRef.current;
      const containerRect = container.getBoundingClientRect();
      const containerHeight = containerRect.height;
      const mouseY = e.clientY - containerRect.top;
      
      let newHeight = (mouseY / containerHeight) * 100;
      newHeight = Math.max(30, Math.min(80, newHeight));
      
      setTerminalHeight(newHeight);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const renderIndexes = (data) => {
    return (
      <div style={{height: '100%', overflow: 'auto', padding: '16px'}}>
        <div style={{fontSize: '16px', fontWeight: '600', color: '#00ff88', marginBottom: '20px'}}>
          📦 Indexes for table: {data.table}
        </div>
        
        {data.hash_indexes && data.hash_indexes.length > 0 && (
          <div style={{marginBottom: '30px'}}>
            <div style={{fontSize: '14px', fontWeight: '600', color: '#6b9bd1', marginBottom: '12px'}}>
              🚀 Hash Indexes ({data.hash_indexes.length})
            </div>
            
            {data.hash_indexes.map((idx, i) => (
              <div key={i} style={{
                background: '#252525',
                border: '1px solid #333',
                borderRadius: '6px',
                padding: '12px',
                marginBottom: '12px'
              }}>
                <div style={{fontSize: '13px', fontWeight: '600', color: '#e0e0e0', marginBottom: '8px'}}>
                  Column: {idx.column} <span style={{color: '#888'}}>({idx.total} entries)</span>
                </div>
                
                <div style={{fontSize: '12px', fontFamily: 'JetBrains Mono, monospace'}}>
                  {idx.entries.map((entry, j) => (
                    <div key={j} style={{
                      padding: '6px 10px',
                      background: '#1a1a1a',
                      borderLeft: '3px solid #0066ff',
                      marginBottom: '4px',
                      color: '#aaa'
                    }}>
                      <span style={{color: '#00ff88'}}>{entry.key}</span> → <span style={{color: '#e0e0e0'}}>{entry.value}</span>
                    </div>
                  ))}
                  {idx.total > 10 && (
                    <div style={{color: '#666', fontSize: '11px', marginTop: '6px'}}>
                      ... and {idx.total - 10} more entries
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
        
        {data.btree_indexes && data.btree_indexes.length > 0 && (
          <div>
            <div style={{fontSize: '14px', fontWeight: '600', color: '#6b9bd1', marginBottom: '12px'}}>
              🌳 B-Tree Indexes ({data.btree_indexes.length})
            </div>
            
            {data.btree_indexes.map((idx, i) => (
              <div key={i} style={{
                background: '#252525',
                border: '1px solid #333',
                borderRadius: '6px',
                padding: '12px',
                marginBottom: '12px'
              }}>
                <div style={{fontSize: '13px', fontWeight: '600', color: '#e0e0e0', marginBottom: '8px'}}>
                  Column: {idx.column} <span style={{color: '#888'}}>({idx.total} keys)</span>
                </div>
                
                <div style={{fontSize: '12px', fontFamily: 'JetBrains Mono, monospace'}}>
                  {idx.entries.map((entry, j) => (
                    <div key={j} style={{
                      padding: '6px 10px',
                      background: '#1a1a1a',
                      borderLeft: '3px solid #00ff88',
                      marginBottom: '4px',
                      color: '#aaa'
                    }}>
                      <span style={{color: '#00ff88'}}>{entry.key}</span> → <span style={{color: '#e0e0e0'}}>{entry.value}</span>
                    </div>
                  ))}
                  {idx.total > 10 && (
                    <div style={{color: '#666', fontSize: '11px', marginTop: '6px'}}>
                      ... and {idx.total - 10} more entries
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderOutput = () => {
    const icons = { info: '💡', success: '✅', error: '❌' };
    
    if (output.type === 'data' && output.data) {
      if (output.data.hasOwnProperty('hash_indexes') || output.data.hasOwnProperty('btree_indexes')) {
        return renderIndexes(output.data);
      }
      
      if (Array.isArray(output.data) && output.data.length > 0) {
        const rowCount = output.data.length;
        const columnNames = output.columns || Object.keys(output.data[0]);
        const colCount = columnNames.length;
        
        return (
          <div style={{height: '100%', display: 'flex', flexDirection: 'column'}}>
            <div style={{
              padding: '8px 16px',
              background: '#252525',
              borderBottom: '1px solid #333',
              fontSize: '11px',
              color: '#888',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span>📊 {rowCount} rows × {colCount} columns</span>
              <span>💡 Scroll horizontally & vertically</span>
            </div>
            
            <div style={{flex: 1, overflow: 'auto'}}>
              <table className="data-table">
                <thead>
                  <tr>
                    {columnNames.map((key, index) => (
                      <th key={index}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {output.data.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {columnNames.map((key, colIndex) => (
                        <td key={colIndex}>
                          {row[key] === null ? <i style={{color: '#666'}}>NULL</i> : String(row[key])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      }
    }
    
    return (
      <div className={`message ${output.type}`}>
        <span className="message-icon">{icons[output.type]}</span>
        <span>{output.message}</span>
      </div>
    );
  };

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} backendUrl={backendUrl} />;
  }

  return (
    <div className="app">
      {/* Hamburger Button */}
      <button 
        className={`hamburger-btn ${showCommandSidebar ? 'active' : ''}`}
        onClick={toggleCommandSidebar}
      >
        <div className="hamburger-line"></div>
        <div className="hamburger-line"></div>
        <div className="hamburger-line"></div>
      </button>

      {/* Overlay */}
      <div 
        className={`command-sidebar-overlay ${showCommandSidebar ? 'active' : ''}`}
        onClick={toggleCommandSidebar}
      ></div>

      {/* Command Sidebar */}
      <div className={`command-sidebar ${showCommandSidebar ? 'active' : ''}`}>
        <div className="command-sidebar-header">
          <h3>📖 SQL Commands</h3>
          <p>Click to copy</p>
        </div>

        <div className="command-sections">
          {Object.entries(commandSections).map(([key, section]) => (
            <div key={key} className="command-section">
              <div 
                className="section-header"
                onClick={() => setExpandedSection(expandedSection === key ? null : key)}
              >
                <span>{section.title}</span>
                <span className="expand-icon">
                  {expandedSection === key ? '▼' : '▶'}
                </span>
              </div>

              {expandedSection === key && (
                <div className="section-content">
                  {section.commands.map((cmd, idx) => (
                    <div key={idx} className="command-item" onClick={() => copyCommand(cmd.syntax)}>
                      <div className="command-name">{cmd.name}</div>
                      <div className="command-syntax" title="Click to copy">
                        {cmd.syntax}
                      </div>
                      {cmd.hint && (
                        <div className="command-hint">💡 {cmd.hint}</div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="command-sidebar-footer">
          <div className="index-hint">
            <strong>🚀 Index Hints:</strong>
            <p><code>HASH</code> → O(1) lookups</p>
            <p><code>BTREE</code> → Range queries</p>
            <p><code>NONE</code> → No index</p>
          </div>
          
          <button className="sidebar-logout-btn" onClick={handleLogout}>
            🚪 Logout
          </button>
        </div>
      </div>

      {/* Tables Sidebar */}
      <div className="sidebar">
        <div className="sidebar-title">
          Tables ({tables.length})
          <div style={{fontSize: '10px', color: '#888', marginTop: '4px'}}>
            👤 {currentUser?.username}
          </div>
        </div>
        
        <div className="tables-list">
          {tables.length === 0 ? (
            <div className="empty-state">
              {isConnected ? 'No tables found' : 'Connecting...'}
            </div>
          ) : (
            tables.map((table, index) => (
              <div
                key={index}
                className={`table-item ${table.active ? 'active' : ''}`}
                onClick={() => selectTable(table.name)}
              >
                <span className="table-icon">{table.icon}</span>
                <div className="table-info">
                  <div className="table-name">{table.name}</div>
                  <div className="table-meta">
                    {table.columns} cols • {table.rows} rows
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div style={{
          padding: '12px',
          borderTop: '2px solid #333',
          marginTop: 'auto',
          background: '#1f1f1f'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#888',
            textTransform: 'uppercase',
            marginBottom: '10px',
            letterSpacing: '0.5px'
          }}>
            📁 Import Data
          </div>
          
          <input
            id="fileInput"
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={(e) => setUploadFile(e.target.files[0])}
            style={{
              fontSize: '10px',
              marginBottom: '8px',
              width: '100%',
              padding: '6px',
              background: '#2d2d2d',
              border: '1px solid #444',
              borderRadius: '4px',
              color: '#e0e0e0'
            }}
          />
          
          {uploadFile && (
            <div style={{fontSize: '10px', color: '#00ff88', marginBottom: '6px'}}>
              ✓ {uploadFile.name}
            </div>
          )}
          
          <input
            type="text"
            placeholder="Table name"
            value={uploadTable}
            onChange={(e) => setUploadTable(e.target.value)}
            style={{
              padding: '6px 8px',
              width: '100%',
              marginBottom: '8px',
              background: '#2d2d2d',
              border: '1px solid #444',
              borderRadius: '4px',
              color: '#e0e0e0',
              fontSize: '11px',
              fontFamily: 'JetBrains Mono, monospace'
            }}
          />
          
          {uploadFile && (uploadFile.name.endsWith('.xlsx') || uploadFile.name.endsWith('.xls')) && (
            <input
              type="text"
              placeholder="Sheet name (optional)"
              value={uploadSheet}
              onChange={(e) => setUploadSheet(e.target.value)}
              style={{
                padding: '6px 8px',
                width: '100%',
                marginBottom: '8px',
                background: '#2d2d2d',
                border: '1px solid #444',
                borderRadius: '4px',
                color: '#e0e0e0',
                fontSize: '11px',
                fontFamily: 'JetBrains Mono, monospace'
              }}
            />
          )}
          
          <button
            onClick={handleFileUpload}
            disabled={!uploadFile || !uploadTable || uploading}
            style={{
              padding: '8px',
              width: '100%',
              background: uploading ? '#666' : '#0066ff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '11px',
              fontWeight: '600',
              cursor: uploading ? 'not-allowed' : 'pointer'
            }}
          >
            {uploading ? '⏳ Uploading...' : '📤 Upload'}
          </button>
        </div>
      </div>

      {/* Main Area */}
      <div className="main-area" ref={containerRef}>
        <div className="top-bar">
          <div className="db-name"><span>🗄️</span> LiteSQL</div>
          <div className="db-status">
            <span className={`status-dot ${isConnected ? 'connected' : ''}`}></span>
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>

        <div className="terminal-section" style={{height: `${terminalHeight}%`}}>
          <div className="terminal-header">
            <div className="terminal-title">$ SQL Terminal</div>
            <div className="terminal-actions">
              <button className="btn" onClick={clearTerminal}>Clear</button>
              <button className="btn" onClick={formatSQL}>Format</button>
              
              <button 
                className="btn" 
                onClick={() => {
                  const selectedTable = tables.find(t => t.active);
                  if (selectedTable) {
                    setSqlInput(`show pickle file of ${selectedTable.name}`);
                    setTimeout(() => executeQuery(), 100);
                  } else {
                    alert('Select a table first!');
                  }
                }}
                disabled={tables.length === 0}
                title="Show indexes for selected table"
              >
                📦 Indexes
              </button>
              
              <button className="btn btn-primary" onClick={executeQuery} disabled={isLoading}>
                {isLoading ? 'Executing...' : 'Execute (Ctrl+Enter)'}
              </button>
            </div>
          </div>
          
          <div className="terminal-body">
            <div className="prompt">litesql&gt;</div>
            <textarea
              className="terminal-input"
              value={sqlInput}
              onChange={(e) => setSqlInput(e.target.value)}
              placeholder="SELECT * FROM users LIMIT 10;"
              spellCheck={false}
            />
          </div>
        </div>

        <div 
          className="splitter"
          onMouseDown={handleMouseDown}
          style={{
            height: '4px',
            background: isDragging ? '#0066ff' : '#333',
            cursor: 'ns-resize',
            position: 'relative',
            zIndex: 100,
            transition: isDragging ? 'none' : 'background 0.2s'
          }}
        >
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '40px',
            height: '3px',
            background: isDragging ? '#0066ff' : '#555',
            borderRadius: '2px',
            transition: isDragging ? 'none' : 'background 0.2s'
          }} />
        </div>

        <div className="output-section" style={{height: `${100 - terminalHeight}%`}}>
          <div className="output-header">
            <div className="output-title">Output</div>
            <div className="output-stats">{stats}</div>
          </div>
          
          <div className="output-body">{renderOutput()}</div>
        </div>
      </div>
    </div>
  );
}

export default App;
