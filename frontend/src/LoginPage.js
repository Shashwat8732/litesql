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
          <h1>🗄️ LiteSQL</h1>
          <p>Your Personal Database in the Cloud</p>
        </div>

        {/* Backend Loading Notice */}
        <div className="backend-notice">
          <div className="backend-notice-icon">⏳</div>
          <div className="backend-notice-content">
            <strong>⚡ First Request? Please Wait!</strong>
            <p>
              Backend hosted on <span className="notice-highlight">free tier</span> takes 
              <span className="notice-highlight"> 30-60 seconds</span> to wake up on first request.
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
