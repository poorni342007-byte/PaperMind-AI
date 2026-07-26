import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import LiveLoader from './components/LiveLoader';
import FloatingStationery from './components/FloatingStationery';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import UploadPDF from './pages/UploadPDF';
import Chat from './pages/Chat';
import History from './pages/History';
import { authAPI } from './api';

const App = () => {
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);

  // Validate existing JWT token on startup to resume sessions
  useEffect(() => {
    const resumeSession = async () => {
      const token = localStorage.getItem('paperpal_token');
      if (token) {
        try {
          const userData = await authAPI.getMe();
          setUser(userData);
        } catch (err) {
          console.error("Expired or invalid session token", err);
          authAPI.logout();
        }
      }
      setInitializing(false);
    };
    resumeSession();
  }, []);

  if (initializing) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: 'var(--bg-cream)'
      }}>
        <LiveLoader text="Preparing PaperMind Desk..." size="large" icon="sparkles" />
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="app-container">
        {/* Floating background elements */}
        <FloatingStationery />

        {/* Global header bar */}
        <Navbar user={user} setUser={setUser} />

        {/* Page content routers */}
        <main className="main-content">
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/" 
              element={<Landing user={user} />} 
            />
            <Route 
              path="/login" 
              element={!user ? <Login setUser={setUser} /> : <Navigate to="/dashboard" replace />} 
            />
            <Route 
              path="/signup" 
              element={!user ? <Signup /> : <Navigate to="/dashboard" replace />} 
            />

            {/* Protected Routes */}
            <Route 
              path="/dashboard" 
              element={user ? <Dashboard user={user} /> : <Navigate to="/login" replace />} 
            />
            <Route 
              path="/upload" 
              element={user ? <UploadPDF /> : <Navigate to="/login" replace />} 
            />
            <Route 
              path="/chat" 
              element={user ? <Chat /> : <Navigate to="/login" replace />} 
            />
            <Route 
              path="/history" 
              element={user ? <History /> : <Navigate to="/login" replace />} 
            />

            {/* Catch-all fallback */}
            <Route 
              path="*" 
              element={<Navigate to={user ? "/dashboard" : "/"} replace />} 
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
