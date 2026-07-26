import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { BookOpen, UploadCloud, MessageSquare, History, LogOut, User } from 'lucide-react';
import { authAPI } from '../api';

const Navbar = ({ user, setUser }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    authAPI.logout();
    setUser(null);
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="logo" onClick={() => navigate(user ? '/dashboard' : '/')}>
        <BookOpen className="logo-icon" size={28} />
        <span>PaperMind</span> AI
      </div>

      <div className="nav-links">
        {user ? (
          <>
            <Link 
              to="/dashboard" 
              className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
            >
              Dashboard
            </Link>
            <Link 
              to="/upload" 
              className={`nav-link ${isActive('/upload') ? 'active' : ''}`}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <UploadCloud size={16} /> Upload
            </Link>
            <Link 
              to="/chat" 
              className={`nav-link ${isActive('/chat') ? 'active' : ''}`}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <MessageSquare size={16} /> Chat
            </Link>
            <Link 
              to="/history" 
              className={`nav-link ${isActive('/history') ? 'active' : ''}`}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <History size={16} /> History
            </Link>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: '12px' }}>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-navy-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <User size={14} /> {user.name}
              </span>
              <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
                <LogOut size={14} /> Logout
              </button>
            </div>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/signup" className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '0.9rem' }}>
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
