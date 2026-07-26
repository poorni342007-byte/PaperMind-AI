import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, BookOpen, AlertCircle, CheckCircle2 } from 'lucide-react';
import { authAPI } from '../api';
import LiveLoader from '../components/LiveLoader';

const Signup = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setError('');
    setLoading(true);
    try {
      await authAPI.signup(name, email, password);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'An error occurred during registration.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexGrow: 1,
      padding: '2rem',
      position: 'relative',
      zIndex: 10
    }}>
      <div className="glass-card" style={{
        padding: '2.5rem',
        width: '100%',
        maxWidth: '440px',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        {/* Title */}
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
          <div style={{
            background: 'var(--primary-lavender)',
            color: 'var(--accent-purple)',
            width: '50px',
            height: '50px',
            borderRadius: '14px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '8px'
          }}>
            <BookOpen size={28} />
          </div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, color: 'var(--text-navy)', fontSize: '1.6rem' }}>
            Join PaperMind AI
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-navy-muted)' }}>
            Start simplifying heavy research reading lists today
          </p>
        </div>

        {/* Success Alert */}
        {success && (
          <div style={{
            background: 'var(--pastel-green)',
            color: 'green',
            border: '1px solid var(--pastel-green-border)',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <CheckCircle2 size={16} />
            <span>Registration successful! Redirecting to login...</span>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div style={{
            background: '#fee2e2',
            color: '#b91c1c',
            border: '1px solid #fca5a5',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSignupSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input 
              type="text" 
              className="form-input" 
              placeholder="e.g. Marie Curie"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading || success}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input 
              type="email" 
              className="form-input" 
              placeholder="e.g. marie@curie.org"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading || success}
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: '0.5rem' }}>
            <label className="form-label">Password</label>
            <input 
              type="password" 
              className="form-input" 
              placeholder="Min. 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading || success}
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', padding: '0.8rem', marginTop: '0.5rem' }}
            disabled={loading || success}
          >
            {loading ? (
              <LiveLoader text="Creating Account" inline={true} icon="sparkles" />
            ) : (
              <>
                <UserPlus size={18} /> Register
              </>
            )}
          </button>
        </form>

        {/* Redirect */}
        <p style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-navy-muted)', marginTop: '0.5rem' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent-purple)', fontWeight: 600, textDecoration: 'none' }}>Log In</Link>
        </p>
      </div>
    </div>
  );
};

export default Signup;
