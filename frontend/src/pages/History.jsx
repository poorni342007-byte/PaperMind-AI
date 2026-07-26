import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { History, MessageSquare, FileText, Calendar, BookOpen, ChevronLeft } from 'lucide-react';
import { historyAPI, pdfAPI } from '../api';
import FormattedText from '../components/FormattedText';

const ChatHistoryPage = () => {
  const navigate = useNavigate();
  const [historyItems, setHistoryItems] = useState([]);
  const [documents, setDocuments] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHistoryAndDocs = async () => {
      try {
        // Fetch user documents first to map document IDs to filenames
        const docList = await pdfAPI.list();
        const docMap = {};
        docList.forEach(d => {
          docMap[d.id] = d.filename;
        });
        setDocuments(docMap);

        // Fetch all history logs
        const logs = await historyAPI.getAllHistory();
        setHistoryItems(logs);
      } catch (err) {
        console.error('Failed to load history metrics:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadHistoryAndDocs();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flexGrow: 1 }}>
        <LiveLoader text="Loading history journals..." size="medium" icon="search" />
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '2.5rem 1.5rem',
      position: 'relative',
      zIndex: 10,
      display: 'flex',
      flexDirection: 'column',
      gap: '2rem'
    }}>
      {/* Navigation */}
      <div>
        <button 
          onClick={() => navigate('/dashboard')} 
          className="btn btn-secondary"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '6px 12px' }}
        >
          <ChevronLeft size={16} /> Back to Dashboard
        </button>
      </div>

      {/* Header */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '2.2rem', color: 'var(--text-navy)', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <History size={36} style={{ color: 'var(--accent-purple)' }} /> Study History Journals
        </h1>
        <p style={{ color: 'var(--text-navy-muted)', fontSize: '1.05rem', lineHeight: '1.5' }}>
          Review explanations, references, and papers you asked about in previous research sessions.
        </p>
      </div>

      {/* Main List */}
      {historyItems.length === 0 ? (
        <div className="glass-card" style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-navy-muted)' }}>
          <MessageSquare size={48} style={{ color: 'var(--accent-purple)', marginBottom: '1rem', opacity: 0.5 }} />
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, color: 'var(--text-navy)' }}>No Query History Found</h3>
          <p style={{ fontSize: '0.9rem', marginTop: '4px' }}>Questions you ask in Chat will be recorded here for quick revision.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {historyItems.map((item) => (
            <div key={item.id} className="glass-card" style={{ padding: '1.5rem 2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {/* Paper metadata */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--primary-lavender-dark)', paddingBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-purple)' }}>
                  <FileText size={14} /> {documents[item.document_id] || "Unknown Research Paper"}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: 'var(--text-navy-muted)' }}>
                  <Calendar size={12} /> {new Date(item.created_at).toLocaleString()}
                </span>
              </div>

              {/* Q&A */}
              <div>
                <p style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-navy)', marginBottom: '6px' }}>
                  Q: {item.question}
                </p>
                <div style={{ fontSize: '0.95rem', color: 'var(--text-navy-muted)', background: 'rgba(255,255,255,0.4)', padding: '10px 14px', borderRadius: '8px' }}>
                  <FormattedText text={item.answer} />
                </div>
              </div>

              {/* Citations */}
              {item.sources && item.sources.length > 0 && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-navy-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <BookOpen size={12} /> Cited references:
                  </span>
                  <ul style={{ paddingLeft: '16px', margin: 0 }}>
                    {item.sources.map((src, sIdx) => {
                      let displayText = '';
                      if (typeof src === 'object' && src !== null) {
                        displayText = `Page ${src.page}${src.chunk_id !== undefined ? ` (Chunk ${src.chunk_id})` : ''}: ${src.preview || ''}`;
                      } else {
                        displayText = String(src);
                      }
                      return (
                        <li key={sIdx} style={{ marginBottom: '4px', lineHeight: '1.3' }}>
                          {displayText}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatHistoryPage;
