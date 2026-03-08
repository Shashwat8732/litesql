import React, { useState } from 'react';
import './LoginPage.css';

function LoginPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const backendUrl = 'https://litesql.onrender.com';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const payload = isLogin 
        ? { username, password }
        : { username, password, email };

      const response = await fetch(`${backendUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (result.success) {
        if (isLogin) {
          localStorage.setItem('session_token', result.session_token);
          localStorage.setItem('username', result.username);
          onLogin(result);
        } else {
          setIsLogin(true);
          setError('');
          alert('✅ Registration successful! Please login.');
        }
      } else {
        setError(result.error || 'An error occurred');
      }
    } catch (err) {
      setError('Connection failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>
            <span className="login-logo">
              {/* Modern Database Icon with Rounded Corners + Data Flow */}
              <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                {/* Data particles floating */}
                <circle cx="25" cy="15" r="3" fill="#0f0f1e" opacity="0.6">
                  <animate attributeName="cy" values="15;10;15" dur="2s" repeatCount="indefinite"/>
                </circle>
                <circle cx="40" cy="12" r="2.5" fill="#0f0f1e" opacity="0.5">
                  <animate attributeName="cy" values="12;8;12" dur="2.5s" repeatCount="indefinite"/>
                </circle>
                <circle cx="60" cy="18" r="3.5" fill="#0f0f1e" opacity="0.7">
                  <animate attributeName="cy" values="18;12;18" dur="1.8s" repeatCount="indefinite"/>
                </circle>
                <circle cx="75" cy="14" r="2" fill="#0f0f1e" opacity="0.5">
                  <animate attributeName="cy" values="14;10;14" dur="2.2s" repeatCount="indefinite"/>
                </circle>
                
                {/* Database cylinder - bottom layer */}
                <ellipse cx="50" cy="75" rx="32" ry="10" fill="#0f0f1e"/>
                <rect x="18" y="75" width="64" height="15" fill="#0f0f1e"/>
                <ellipse cx="50" cy="90" rx="32" ry="10" fill="#001a33"/>
                
                {/* Database cylinder - middle layer */}
                <ellipse cx="50" cy="55" rx="32" ry="10" fill="#0f0f1e"/>
                <rect x="18" y="55" width="64" height="15" fill="#0f0f1e"/>
                <ellipse cx="50" cy="70" rx="32" ry="10" fill="#002244"/>
                
                {/* Database cylinder - top layer */}
                <ellipse cx="50" cy="35" rx="32" ry="10" fill="#0f0f1e"/>
                <rect x="18" y="35" width="64" height="15" fill="#0f0f1e"/>
                <ellipse cx="50" cy="50" rx="32" ry="10" fill="#003355"/>
                
                {/* Top lid with glow */}
                <ellipse cx="50" cy="35" rx="32" ry="10" fill="#0f0f1e"/>
              </svg>
            </span>
            LiteSQL
          </h1>
          <p>Lightweight SQL Database Engine</p>
        </div>

        {/* Backend Loading Notice */}
        <div className="backend-notice">
          <div className="backend-notice-icon">⏳</div>
          <div className="backend-notice-content">
            <strong>⚡ First Request? Please Wait!</strong>
            <p>
              Backend hosted on <span className="notice-highlight">free tier</span> takes 
              <span className="notice-highlight"> 1-2 minutes</span> to wake up on first request.
            </p>
            <p style={{fontSize: '12px', opacity: 0.9, marginTop: '6px'}}>
              ✅ Subsequent requests will be instant!
            </p>
          </div>
        </div>

        <div className="login-tabs">
          <button 
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => { setIsLogin(true); setError(''); }}
          >
            Login
          </button>
          <button 
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => { setIsLogin(false); setError(''); }}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username (min 3 chars)"
              required
              minLength={3}
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>Email (optional)</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter email"
              />
            </div>
          )}

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password (min 6 chars)"
              required
              minLength={6}
            />
          </div>

          {error && (
            <div className="error-message">
              ❌ {error}
            </div>
          )}

          <button 
            type="submit" 
            className="submit-btn"
            disabled={loading}
          >
            {loading ? (isLogin ? '⏳ Logging in...' : '⏳ Registering...') : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>

        <div className="login-footer">
          <p>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <span 
              className="link"
              onClick={() => { setIsLogin(!isLogin); setError(''); }}
            >
              {isLogin ? 'Register' : 'Login'}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
