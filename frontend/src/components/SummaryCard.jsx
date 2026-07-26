import React from 'react';
import { BookOpen, Award, CheckCircle } from 'lucide-react';

const SummaryCard = ({ summary, notes }) => {
  return (
    <div className="lined-paper" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h2 style={{ 
        fontFamily: 'var(--font-display)', 
        fontWeight: 800, 
        color: 'var(--text-navy)', 
        borderBottom: '2px dashed var(--primary-lavender-dark)', 
        paddingBottom: '10px',
        marginBottom: '20px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <BookOpen style={{ color: 'var(--accent-purple)' }} /> Simplified Study Notes
      </h2>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ 
          fontFamily: 'var(--font-display)', 
          fontWeight: 600, 
          color: 'var(--accent-purple)',
          fontSize: '1.1rem',
          marginBottom: '8px'
        }}>
          Executive Summary
        </h3>
        <p style={{ 
          fontFamily: 'var(--font-sans)', 
          fontSize: '0.95rem', 
          lineHeight: '1.6', 
          color: 'var(--text-navy-muted)',
          textAlign: 'justify'
        }}>
          {summary || "No summary available yet. Please select or upload a document."}
        </p>
      </div>

      <div>
        <h3 style={{ 
          fontFamily: 'var(--font-display)', 
          fontWeight: 600, 
          color: 'var(--accent-purple)',
          fontSize: '1.1rem',
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <Award size={18} /> Core Takeaways
        </h3>
        
        {notes && notes.length > 0 ? (
          <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {notes.map((note, index) => (
              <li 
                key={index}
                style={{ 
                  display: 'flex', 
                  alignItems: 'flex-start', 
                  gap: '10px',
                  fontSize: '0.95rem',
                  lineHeight: '1.5',
                  color: 'var(--text-navy-muted)'
                }}
              >
                <CheckCircle 
                  size={16} 
                  style={{ 
                    color: 'var(--accent-purple)', 
                    marginTop: '4px', 
                    flexShrink: 0 
                  }} 
                />
                <span>{note}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ fontStyle: 'italic', color: 'var(--text-navy-muted)' }}>No study notes generated yet.</p>
        )}
      </div>
    </div>
  );
};

export default SummaryCard;
