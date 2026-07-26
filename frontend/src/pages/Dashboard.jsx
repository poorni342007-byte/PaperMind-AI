import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, 
  MessageSquare, 
  BookOpen, 
  HelpCircle, 
  History, 
  BookMarked, 
  Sparkles, 
  ArrowRight,
  Clock,
  UserCheck
} from 'lucide-react';
import { pdfAPI, historyAPI } from '../api';

const Dashboard = ({ user }) => {
  const navigate = useNavigate();
  
  // State for tracking dynamic API metrics
  const [documents, setDocuments] = useState([]);
  const [recentChats, setRecentChats] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load document metrics and recent actions from backend APIs
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        
        // 1. Fetch document list
        const docs = await pdfAPI.list();
        setDocuments(docs || []);
        
        // 2. Fetch user chat history
        const chats = await historyAPI.getAllHistory();
        setRecentChats(chats || []);
        
      } catch (err) {
        console.error('Failed to load dashboard state data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadDashboardData();
  }, []);

  // Quick Action card metadata mapping
  const quickActions = [
    {
      title: "Upload PDF",
      desc: "Index research paper",
      icon: <UploadCloud size={20} />,
      link: "/upload",
      bgColor: "var(--primary-lavender)",
      textColor: "var(--accent-purple)"
    },
    {
      title: "Ask AI",
      desc: "Ask questions on text",
      icon: <MessageSquare size={20} />,
      link: "/chat",
      bgColor: "var(--pastel-yellow)",
      textColor: "#d97706"
    },
    {
      title: "Study Notes",
      desc: "Generate exam outlines",
      icon: <BookOpen size={20} />,
      link: "/chat?tab=notes",
      bgColor: "var(--pastel-pink)",
      textColor: "#db2777"
    },
    {
      title: "Solve Quizzes",
      desc: "Test comprehension",
      icon: <HelpCircle size={20} />,
      link: "/chat?tab=quiz",
      bgColor: "var(--pastel-green)",
      textColor: "#15803d"
    }
  ];

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '2.5rem 1.5rem',
      position: 'relative',
      zIndex: 10,
      display: 'flex',
      flexDirection: 'column',
      gap: '2.5rem'
    }}>
      {/* Banner & Welcome Header */}
      <div className="glass-card" style={{
        padding: '2.5rem',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.85) 0%, rgba(236,229,252,0.8) 100%)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '2rem',
        border: '1px solid var(--card-border)'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxWidth: '650px' }}>
          <span style={{ 
            fontSize: '0.8rem', 
            fontWeight: 700, 
            textTransform: 'uppercase', 
            letterSpacing: '1.5px', 
            color: 'var(--accent-purple)', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '6px' 
          }}>
            <Sparkles size={14} /> Aesthetic AI Research Workspace
          </span>
          <h1 style={{ 
            fontFamily: 'var(--font-display)', 
            fontWeight: 800, 
            fontSize: '2.2rem', 
            color: 'var(--text-navy)', 
            lineHeight: 1.2 
          }}>
            Welcome to Your Study Desk, {user?.name || 'Scholar'}!
          </h1>
          <p style={{ color: 'var(--text-navy-muted)', fontSize: '1rem', lineHeight: '1.5' }}>
            Simplifying complex papers starts here. Click a quick action below, drop research PDF documents, or pick up where you left off.
          </p>
        </div>

        {/* Statistics Cards */}
        <div style={{ 
          display: 'flex', 
          gap: '1.25rem', 
          flexWrap: 'wrap', 
          justifyContent: 'flex-start' 
        }}>
          {/* Stat 1: Uploaded Papers */}
          <div style={{
            background: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '16px',
            border: '1px solid var(--primary-lavender-dark)',
            textAlign: 'center',
            minWidth: '120px',
            boxShadow: '0 4px 10px rgba(0,0,0,0.01)'
          }}>
            <BookMarked size={18} style={{ color: 'var(--accent-purple)', marginBottom: '4px' }} />
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-navy)' }}>
              {loading ? '...' : documents.length}
            </div>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-navy-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Papers Indexed
            </div>
          </div>

          {/* Stat 2: Questions asked */}
          <div style={{
            background: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '16px',
            border: '1px solid var(--primary-lavender-dark)',
            textAlign: 'center',
            minWidth: '120px',
            boxShadow: '0 4px 10px rgba(0,0,0,0.01)'
          }}>
            <MessageSquare size={18} style={{ color: 'var(--accent-purple)', marginBottom: '4px' }} />
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-navy)' }}>
              {loading ? '...' : recentChats.length}
            </div>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-navy-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Questions Asked
            </div>
          </div>

          {/* Stat 3: Quiz Attempts */}
          <div style={{
            background: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '16px',
            border: '1px solid var(--primary-lavender-dark)',
            textAlign: 'center',
            minWidth: '120px',
            boxShadow: '0 4px 10px rgba(0,0,0,0.01)'
          }}>
            <UserCheck size={18} style={{ color: 'var(--accent-purple)', marginBottom: '4px' }} />
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-navy)' }}>
              2
            </div>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-navy-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Quiz Attempts
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions Panel */}
      <div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--text-navy)', marginBottom: '1.25rem', fontSize: '1.3rem' }}>
          Quick Study Actions
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1.25rem'
        }}>
          {quickActions.map((action, idx) => (
            <div 
              key={idx}
              className="glass-card"
              onClick={() => navigate(action.link)}
              style={{
                padding: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                cursor: 'pointer',
                borderRadius: '16px'
              }}
            >
              <div style={{
                backgroundColor: action.bgColor,
                color: action.textColor,
                padding: '10px',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                {action.icon}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 700, color: 'var(--text-navy)', fontSize: '0.95rem' }}>{action.title}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-navy-muted)' }}>{action.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Split Activity Boards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '2rem'
      }}>
        {/* Left Board: Recent Uploads */}
        <div className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--text-navy)', fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BookMarked size={18} style={{ color: 'var(--accent-purple)' }} /> Recent Uploads
            </h3>
            {documents.length > 0 && (
              <button 
                onClick={() => navigate('/chat')} 
                style={{ background: 'transparent', border: 'none', color: 'var(--accent-purple)', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                View All <ArrowRight size={12} />
              </button>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flexGrow: 1 }}>
            {loading ? (
              <span style={{ fontSize: '0.9rem', color: 'var(--text-navy-muted)' }}>Updating study board...</span>
            ) : documents.length === 0 ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                flexGrow: 1,
                padding: '2rem',
                textAlign: 'center',
                background: 'rgba(0,0,0,0.01)',
                borderRadius: '12px',
                border: '1px dashed var(--primary-lavender-dark)'
              }}>
                <UploadCloud size={32} style={{ color: 'var(--primary-lavender-dark)', marginBottom: '8px' }} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-navy)' }}>No documents uploaded yet</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-navy-muted)', marginTop: '4px' }}>Click "Upload PDF" above to index your first paper.</span>
              </div>
            ) : (
              documents.slice(0, 3).map((doc) => (
                <div 
                  key={doc.id}
                  onClick={() => navigate('/chat')}
                  style={{
                    padding: '12px 16px',
                    borderRadius: '12px',
                    border: '1px solid var(--primary-lavender-dark)',
                    background: 'white',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  className="activity-item-hover"
                >
                  <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '80%', gap: '4px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-navy)', fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {doc.filename}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-navy-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={12} /> {new Date(doc.uploaded_at).toLocaleDateString()}
                    </span>
                  </div>
                  <ArrowRight size={16} style={{ color: 'var(--primary-lavender-dark)' }} />
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Board: Recent Chat Queries */}
        <div className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--text-navy)', fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <History size={18} style={{ color: 'var(--accent-purple)' }} /> Recent Chats
            </h3>
            {recentChats.length > 0 && (
              <button 
                onClick={() => navigate('/history')} 
                style={{ background: 'transparent', border: 'none', color: 'var(--accent-purple)', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                View History <ArrowRight size={12} />
              </button>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flexGrow: 1 }}>
            {loading ? (
              <span style={{ fontSize: '0.9rem', color: 'var(--text-navy-muted)' }}>Updating study board...</span>
            ) : recentChats.length === 0 ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                flexGrow: 1,
                padding: '2rem',
                textAlign: 'center',
                background: 'rgba(0,0,0,0.01)',
                borderRadius: '12px',
                border: '1px dashed var(--primary-lavender-dark)'
              }}>
                <MessageSquare size={32} style={{ color: 'var(--primary-lavender-dark)', marginBottom: '8px' }} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-navy)' }}>No conversations yet</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-navy-muted)', marginTop: '4px' }}>Click "Ask AI" to have your first research discussion.</span>
              </div>
            ) : (
              recentChats.slice(0, 3).map((chat) => (
                <div 
                  key={chat.id}
                  onClick={() => navigate('/chat')}
                  style={{
                    padding: '12px 16px',
                    borderRadius: '12px',
                    border: '1px solid var(--primary-lavender-dark)',
                    background: 'white',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  className="activity-item-hover"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, color: 'var(--accent-purple)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Question</span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-navy-muted)' }}>{new Date(chat.created_at).toLocaleDateString()}</span>
                  </div>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-navy)', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    "{chat.question}"
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
