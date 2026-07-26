import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Sparkles, MessageSquare, BookOpenCheck, History, ArrowRight } from 'lucide-react';

const Landing = ({ user }) => {
  const navigate = useNavigate();

  // Redirect to Dashboard if logged in, otherwise go to Signup
  const handleGetStarted = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      navigate('/signup');
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '3rem 2rem',
      flexGrow: 1,
      zIndex: 10,
      position: 'relative'
    }}>
      {/* Hero Section */}
      <header style={{
        textAlign: 'center',
        maxWidth: '800px',
        margin: '2rem auto 4rem auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '1.5rem'
      }}>
        {/* Sparkle badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'var(--primary-lavender)',
          color: 'var(--accent-purple)',
          padding: '6px 16px',
          borderRadius: '50px',
          fontSize: '0.85rem',
          fontWeight: 600,
          fontFamily: 'var(--font-display)',
          border: '1px solid var(--primary-lavender-dark)'
        }}>
          <Sparkles size={14} /> Meet PaperMind AI Workspace
        </div>

        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontWeight: 900,
          fontSize: '3.5rem',
          lineHeight: 1.15,
          color: 'var(--text-navy)',
          letterSpacing: '-0.02em',
          marginTop: '0.5rem'
        }}>
          Your Personal AI <br />
          <span style={{
            backgroundImage: 'linear-gradient(135deg, var(--accent-purple), #ec4899)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Digital Study Desk
          </span>
        </h1>

        <p style={{
          fontSize: '1.1rem',
          color: 'var(--text-navy-muted)',
          lineHeight: 1.6,
          maxWidth: '600px'
        }}>
          Upload complex academic PDFs, index papers instantly via semantic vector search, ask deep AI questions, generate simplified learning notes, and study with custom interactive quizzes.
        </p>

        {/* CTA Buttons */}
        <div style={{
          display: 'flex',
          gap: '16px',
          marginTop: '1.5rem',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          <button onClick={handleGetStarted} className="btn btn-primary" style={{ padding: '0.9rem 2.2rem', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px', boxShadow: '0 4px 14px rgba(124, 58, 237, 0.3)' }}>
            Get Started <ArrowRight size={18} />
          </button>
          {!user && (
            <button onClick={() => navigate('/login')} className="btn btn-secondary" style={{ padding: '0.9rem 2.2rem', fontSize: '1rem' }}>
              Sign In to Desk
            </button>
          )}
        </div>
      </header>

      {/* Grid Features Section */}
      <section style={{
        width: '100%',
        maxWidth: '1100px',
        margin: '0 auto'
      }}>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontWeight: 800,
          textAlign: 'center',
          fontSize: '2rem',
          color: 'var(--text-navy)',
          marginBottom: '2.5rem'
        }}>
          Everything You Need to Master Research
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '2rem'
        }}>
          {/* Card 1: RAG Search */}
          <div className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{
              background: 'var(--primary-lavender)',
              color: 'var(--accent-purple)',
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <MessageSquare size={22} />
            </div>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.25rem', color: 'var(--text-navy)' }}>
              Ask Questions from PDFs
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-navy-muted)', lineHeight: 1.5 }}>
              Use custom Retrieval-Augmented Generation to scan your uploaded PDFs and answer complicated questions with clean page sources and citations.
            </p>
          </div>

          {/* Card 2: Notes Generator */}
          <div className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{
              background: 'rgba(251, 191, 36, 0.15)',
              color: '#d97706',
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <BookOpen size={22} />
            </div>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.25rem', color: 'var(--text-navy)' }}>
              Aesthetic Student Notes
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-navy-muted)', lineHeight: 1.5 }}>
              Automatically convert complex terminology into beginner-friendly simple notes, key concepts glossaries, and comprehensive revision summaries.
            </p>
          </div>

          {/* Card 3: Quiz Generator */}
          <div className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{
              background: 'rgba(139, 92, 246, 0.15)',
              color: 'var(--accent-purple)',
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <BookOpenCheck size={22} />
            </div>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.25rem', color: 'var(--text-navy)' }}>
              Self-Study MCQ Quizzes
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-navy-muted)', lineHeight: 1.5 }}>
              Test your understanding instantly with custom generated multiple-choice and true/false questions complete with detailed explanations and instant grading.
            </p>
          </div>
        </div>
      </section>

      {/* Footer info */}
      <footer style={{
        marginTop: '6rem',
        fontSize: '0.85rem',
        color: 'var(--text-navy-muted)',
        textAlign: 'center',
        borderTop: '1px solid var(--primary-lavender-dark)',
        paddingTop: '2rem',
        width: '100%',
        maxWidth: '1100px'
      }}>
        PaperMind AI © 2026. Designed for modern student workflows.
      </footer>
    </div>
  );
};

export default Landing;
