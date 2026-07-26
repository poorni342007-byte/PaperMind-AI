import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  FileText, MessageSquare, BookOpen, HelpCircle, 
  ChevronRight, Library, Sparkles, Upload, Trash2 
} from 'lucide-react';
import { pdfAPI, chatAPI, historyAPI } from '../api';
import ChatBox from '../components/ChatBox';
import SummaryCard from '../components/SummaryCard';
import QuizCard from '../components/QuizCard';
import LiveLoader from '../components/LiveLoader';

const Chat = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [activeDoc, setActiveDoc] = useState(null);
  
  // Tab states: 'chat' | 'notes' | 'quiz'
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'chat');
  
  // Data states
  const [messages, setMessages] = useState([]);
  const [summaryData, setSummaryData] = useState({ summary: '', notes: [] });
  const [quizData, setQuizData] = useState([]);
  
  // Loading & error states
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [loadingChat, setLoadingChat] = useState(false);
  const [loadingNotes, setLoadingNotes] = useState(false);
  const [loadingQuiz, setLoadingQuiz] = useState(false);

  // Sync tab from URL query params
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam && ['chat', 'notes', 'quiz'].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  // Load documents on mount
  useEffect(() => {
    const loadDocs = async () => {
      try {
        const docList = await pdfAPI.list();
        setDocuments(docList);
        if (docList.length > 0) {
          // Default to the first document
          setActiveDoc(docList[0]);
        }
      } catch (err) {
        console.error('Failed to load documents:', err);
      } finally {
        setLoadingDocs(false);
      }
    };
    loadDocs();
  }, []);

  // Fetch document-specific data when activeDoc or activeTab changes
  useEffect(() => {
    if (!activeDoc) return;

    if (activeTab === 'chat') {
      loadChatHistory(activeDoc.id);
    } else if (activeTab === 'notes') {
      loadSummaryAndNotes(activeDoc.id);
    } else if (activeTab === 'quiz') {
      loadQuiz(activeDoc.id);
    }
  }, [activeDoc, activeTab]);

  const loadChatHistory = async (docId) => {
    try {
      setLoadingChat(true);
      const history = await historyAPI.getChatsForDoc(docId);
      // Flatten DB format (question & answer) into single messages list
      const formattedMsgs = [];
      history.forEach((chat) => {
        formattedMsgs.push({
          id: chat.id + '_q',
          text: chat.question,
          sender: 'user',
          created_at: chat.created_at
        });
        formattedMsgs.push({
          id: chat.id + '_a',
          text: chat.answer,
          sender: 'ai',
          sources: chat.sources,
          created_at: chat.created_at
        });
      });
      setMessages(formattedMsgs);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    } finally {
      setLoadingChat(false);
    }
  };

  const loadSummaryAndNotes = async (docId) => {
    try {
      setLoadingNotes(true);
      const summary = await pdfAPI.getSummary(docId);
      setSummaryData(summary);
    } catch (err) {
      console.error('Failed to load notes:', err);
    } finally {
      setLoadingNotes(false);
    }
  };

  const loadQuiz = async (docId) => {
    try {
      setLoadingQuiz(true);
      const response = await chatAPI.getQuiz(docId);
      setQuizData(response.quiz);
    } catch (err) {
      console.error('Failed to load quiz:', err);
    } finally {
      setLoadingQuiz(false);
    }
  };

  const handleDeleteDoc = async (e, docId) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this document and all its chat history?")) {
      return;
    }
    
    try {
      await pdfAPI.delete(docId);
      setDocuments((prevDocs) => {
        const updated = prevDocs.filter((d) => d.id !== docId);
        if (activeDoc?.id === docId) {
          setActiveDoc(updated.length > 0 ? updated[0] : null);
        }
        return updated;
      });
    } catch (err) {
      console.error("Failed to delete document", err);
      alert("Failed to delete document. Please try again.");
    }
  };

  const handleSendMessage = async (text) => {
    if (!activeDoc) return;
    
    // Add user message locally
    const userMsg = {
      id: Date.now() + '_q',
      text,
      sender: 'user'
    };
    setMessages((prev) => [...prev, userMsg]);
    
    setLoadingChat(true);
    try {
      const response = await chatAPI.ask(activeDoc.id, text);
      const aiMsg = {
        id: response.id,
        text: response.answer,
        sender: 'ai',
        sources: response.sources
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error(err);
      const errorMsg = {
        id: Date.now() + '_error',
        text: 'Failed to retrieve answer. Please try again.',
        sender: 'ai',
        sources: []
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoadingChat(false);
    }
  };

  const handleTabChange = (tabName) => {
    setActiveTab(tabName);
    setSearchParams({ tab: tabName });
  };

  if (loadingDocs) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flexGrow: 1 }}>
        <LiveLoader text="Loading your bookshelf..." size="medium" icon="search" />
      </div>
    );
  }

  return (
    <div className="chat-container">
      {/* Sidebar: Documents list */}
      <aside className="chat-sidebar">
        <h3 style={{ 
          fontFamily: 'var(--font-display)', 
          fontWeight: 700, 
          fontSize: '1.1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          paddingBottom: '12px',
          borderBottom: '1px solid var(--primary-lavender-dark)'
        }}>
          <Library size={18} style={{ color: 'var(--accent-purple)' }} /> Bookshelf
        </h3>
        
        {documents.length === 0 ? (
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            flexGrow: 1, 
            gap: '12px',
            textAlign: 'center',
            padding: '1rem' 
          }}>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-navy-muted)' }}>
              No research papers uploaded yet.
            </p>
            <button 
              onClick={() => navigate('/upload')} 
              className="btn btn-secondary"
              style={{ fontSize: '0.8rem', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <Upload size={14} /> Upload PDF
            </button>
          </div>
        ) : (
          <div className="chat-history-list">
            {documents.map((doc) => (
              <div 
                key={doc.id}
                className={`chat-history-item ${activeDoc?.id === doc.id ? 'active' : ''}`}
                onClick={() => setActiveDoc(doc)}
                style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', paddingRight: '8px' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexGrow: 1, minWidth: 0 }}>
                  <FileText size={18} style={{ color: activeDoc?.id === doc.id ? 'var(--accent-purple)' : 'var(--text-navy-muted)', flexShrink: 0 }} />
                  <span style={{ 
                    fontSize: '0.85rem', 
                    fontWeight: activeDoc?.id === doc.id ? 600 : 400,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {doc.filename}
                  </span>
                </div>
                <button
                  onClick={(e) => handleDeleteDoc(e, doc.id)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    padding: '4px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '4px',
                    transition: 'all 0.2s ease',
                  }}
                  className="delete-doc-btn"
                  title="Delete Document"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Main Workspace */}
      <main className="chat-workspace">
        {!activeDoc ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: 'var(--text-navy-muted)',
            gap: '12px'
          }}>
            <Library size={48} />
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600 }}>Your Study Workspace is Empty</h3>
            <p style={{ fontSize: '0.9rem' }}>Please upload a PDF document first to begin studying.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Active Document Header */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              borderBottom: '1px solid var(--primary-lavender-dark)',
              paddingBottom: '1rem',
              marginBottom: '1rem',
              flexWrap: 'wrap',
              gap: '12px'
            }}>
              <div>
                <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.25rem' }}>
                  {activeDoc.filename}
                </h2>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-navy-muted)' }}>
                  Indexed on {new Date(activeDoc.uploaded_at).toLocaleDateString()}
                </p>
              </div>

              {/* Study Mode Navigation Tabs */}
              <div style={{ display: 'flex', gap: '8px', background: 'var(--bg-cream-dark)', padding: '4px', borderRadius: '10px' }}>
                <button 
                  onClick={() => handleTabChange('chat')}
                  className="btn"
                  style={{
                    padding: '6px 12px',
                    fontSize: '0.85rem',
                    background: activeTab === 'chat' ? 'white' : 'transparent',
                    color: activeTab === 'chat' ? 'var(--accent-purple)' : 'var(--text-navy-muted)',
                    boxShadow: activeTab === 'chat' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
                    borderRadius: '8px'
                  }}
                >
                  <MessageSquare size={14} /> Q&A Chat
                </button>
                <button 
                  onClick={() => handleTabChange('notes')}
                  className="btn"
                  style={{
                    padding: '6px 12px',
                    fontSize: '0.85rem',
                    background: activeTab === 'notes' ? 'white' : 'transparent',
                    color: activeTab === 'notes' ? 'var(--accent-purple)' : 'var(--text-navy-muted)',
                    boxShadow: activeTab === 'notes' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
                    borderRadius: '8px'
                  }}
                >
                  <BookOpen size={14} /> Study Notes
                </button>
                <button 
                  onClick={() => handleTabChange('quiz')}
                  className="btn"
                  style={{
                    padding: '6px 12px',
                    fontSize: '0.85rem',
                    background: activeTab === 'quiz' ? 'white' : 'transparent',
                    color: activeTab === 'quiz' ? 'var(--accent-purple)' : 'var(--text-navy-muted)',
                    boxShadow: activeTab === 'quiz' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
                    borderRadius: '8px'
                  }}
                >
                  <HelpCircle size={14} /> Practice Quiz
                </button>
              </div>
            </div>

            {/* Tab Workspaces */}
            <div style={{ flexGrow: 1, overflowY: 'auto' }}>
              {activeTab === 'chat' && (
                <ChatBox 
                  messages={messages} 
                  onSendMessage={handleSendMessage} 
                  loading={loadingChat} 
                />
              )}

              {activeTab === 'notes' && (
                loadingNotes ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                    <LiveLoader text="Synthesizing beginner notes..." size="medium" icon="brain" />
                  </div>
                ) : (
                  <SummaryCard 
                    summary={summaryData.summary} 
                    notes={summaryData.notes} 
                  />
                )
              )}

              {activeTab === 'quiz' && (
                loadingQuiz ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                    <LiveLoader text="Generating custom quiz questions..." size="medium" icon="sparkles" />
                  </div>
                ) : (
                  <QuizCard 
                    quiz={quizData} 
                    onReset={() => loadQuiz(activeDoc.id)}
                  />
                )
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Chat;
