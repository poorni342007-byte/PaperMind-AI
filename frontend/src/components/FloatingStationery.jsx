import React from 'react';

const FloatingStationery = () => {
  return (
    <div className="floating-container">
      {/* 1. Book SVG */}
      <div className="floating-item float-1" title="Research Book">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-purple-hover)', opacity: 0.6 }}>
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
      </div>

      {/* 2. Cozy Sticky Note */}
      <div className="floating-item float-2">
        <div className="sticky-note" style={{ backgroundColor: 'var(--pastel-yellow)', fontSize: '0.75rem', fontWeight: 600 }}>
          Study Tip:<br/>RAG = Vector DB + LLM! 🚀
        </div>
      </div>

      {/* 3. Pencil SVG */}
      <div className="floating-item float-3" title="Drawing Pencil">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--pastel-pink)', stroke: '#ec4899', opacity: 0.8 }}>
          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
        </svg>
      </div>

      {/* 4. Paper Clip SVG */}
      <div className="floating-item float-4" title="Paper Clip">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-navy-muted)', opacity: 0.5 }}>
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
        </svg>
      </div>

      {/* 5. Golden Star SVG */}
      <div className="floating-item float-5" title="Idea Spark">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="currentColor" style={{ color: 'var(--pastel-yellow-hover)', filter: 'drop-shadow(0 2px 4px rgba(253, 224, 71, 0.4))' }}>
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      </div>

      {/* 6. Coffee Cup SVG */}
      <div className="floating-item float-6" title="Fresh Coffee">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#854d0e', opacity: 0.6 }}>
          <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
          <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" />
          <line x1="6" y1="2" x2="6" y2="4" />
          <line x1="10" y1="2" x2="10" y2="4" />
          <line x1="14" y1="2" x2="14" y2="4" />
        </svg>
      </div>

      {/* 7. Mini Notebook */}
      <div className="floating-item float-7" title="My Notes">
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-purple)', opacity: 0.5 }}>
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <line x1="3" y1="9" x2="21" y2="9" />
          <line x1="9" y1="21" x2="9" y2="9" />
        </svg>
      </div>

      {/* 8. Extra Sticky Note (Pink/lavender) */}
      <div className="floating-item float-8">
        <div className="sticky-note" style={{ backgroundColor: 'var(--pastel-pink)', fontSize: '0.7rem', fontWeight: 500, transform: 'rotate(5deg)' }}>
          Research Goal:<br/>Simplify PDFs for students! 🎓
        </div>
      </div>
    </div>
  );
};

export default FloatingStationery;
