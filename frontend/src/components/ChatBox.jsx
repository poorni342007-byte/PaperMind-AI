import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, BookOpen, User } from 'lucide-react';
import FormattedText from './FormattedText';
import LiveLoader from './LiveLoader';

const CollapsibleSources = ({ sources }) => {
  const [open, setOpen] = useState(false);
  
  return (
    <div className="sources-box" style={{ marginTop: '12px' }}>
      <button 
        type="button"
        onClick={() => setOpen(!open)}
        style={{
          background: 'none',
          border: 'none',
          padding: 0,
          color: 'var(--accent-purple)',
          fontWeight: 600,
          fontSize: '0.8rem',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}
      >
        <BookOpen size={12} style={{ flexShrink: 0 }} /> 
        {open ? 'Hide Citing Sources' : `Show Citing Sources (${sources.length})`}
      </button>
      
      {open && (
        <ul style={{ 
          paddingLeft: '16px', 
          margin: '8px 0 0 0', 
          fontSize: '0.75rem', 
          color: 'var(--text-navy-muted)', 
          listStyleType: 'disc',
          textAlign: 'left'
        }}>
          {sources.map((src, sIdx) => {
            let displayText = '';
            if (typeof src === 'object' && src !== null) {
              displayText = `Page ${src.page}${src.chunk_id !== undefined ? ` (Chunk ${src.chunk_id})` : ''}: ${src.preview || ''}`;
            } else {
              displayText = String(src);
            }
            return (
              <li key={sIdx} style={{ marginBottom: '8px', lineHeight: '1.25rem' }}>
                {displayText}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

const ChatBox = ({ messages, onSendMessage, loading }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1rem' }}>
      <div className="chat-messages-box">
        {messages.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: 'var(--text-navy-muted)',
            gap: '12px',
            textAlign: 'center',
            padding: '2rem'
          }}>
            <Sparkles size={40} style={{ color: 'var(--accent-purple)' }} />
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600 }}>Ask your PDF Research Paper Anything</h3>
            <p style={{ fontSize: '0.9rem', maxWidth: '400px' }}>
              Ask questions about math equations, methods, results, or request simple explanations of complex jargon.
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div 
              key={msg.id || index} 
              className={`chat-message ${msg.sender === 'user' ? 'user' : 'ai'}`}
            >
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: msg.sender === 'user' ? 'var(--pastel-pink)' : 'var(--accent-purple)',
                color: msg.sender === 'user' ? 'var(--text-navy)' : 'white',
                fontSize: '0.8rem',
                fontWeight: 'bold',
                flexShrink: 0
              }}>
                {msg.sender === 'user' ? <User size={16} /> : <Sparkles size={16} />}
              </div>

              <div className="chat-bubble">
                <FormattedText text={msg.text} />
                
                {msg.sender === 'ai' && msg.sources && msg.sources.length > 0 && (
                  <CollapsibleSources sources={msg.sources} />
                )}
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="chat-message ai">
            <div className="chat-bubble" style={{ background: 'var(--primary-lavender)', padding: '10px 16px' }}>
              <LiveLoader text="Thinking and searching paper contents" inline={true} icon="search" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-bar">
        <input
          type="text"
          className="form-input"
          placeholder="Ask a question (e.g., 'What is self-attention and how does it speed up training?')..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          style={{ flexGrow: 1 }}
        />
        <button 
          type="submit" 
          className="btn btn-primary" 
          disabled={loading || !input.trim()}
          style={{ padding: '0.75rem 1.25rem' }}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
};

export default ChatBox;
