import React, { useState } from 'react';
import { HelpCircle, Sparkles, Check, X, RefreshCw, ChevronRight } from 'lucide-react';

const QuizCard = ({ quiz, onReset }) => {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedOption, setSelectedOption] = useState(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [quizFinished, setQuizFinished] = useState(false);

  if (!quiz || quiz.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-navy-muted)' }}>
        <HelpCircle size={40} style={{ color: 'var(--accent-purple)', marginBottom: '8px' }} />
        <p>No quiz questions available. Select or upload a document to get started.</p>
      </div>
    );
  }

  const currentQuestion = quiz[currentIdx];

  const handleOptionClick = (optionIdx) => {
    if (isAnswered) return;
    setSelectedOption(optionIdx);
  };

  const handleSubmit = () => {
    if (selectedOption === null || isAnswered) return;
    
    setIsAnswered(true);
    if (selectedOption === currentQuestion.correct_option_index) {
      setScore(score + 1);
    }
  };

  const handleNext = () => {
    if (currentIdx + 1 < quiz.length) {
      setCurrentIdx(currentIdx + 1);
      setSelectedOption(null);
      setIsAnswered(false);
    } else {
      setQuizFinished(true);
    }
  };

  const handleRetakeSame = () => {
    setCurrentIdx(0);
    setSelectedOption(null);
    setIsAnswered(false);
    setScore(0);
    setQuizFinished(false);
  };

  const handleGenerateNew = () => {
    setCurrentIdx(0);
    setSelectedOption(null);
    setIsAnswered(false);
    setScore(0);
    setQuizFinished(false);
    if (onReset) onReset();
  };

  if (quizFinished) {
    const passed = score >= quiz.length / 2;
    return (
      <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', maxWidth: '550px', margin: '0 auto' }}>
        <Sparkles size={48} style={{ color: passed ? 'var(--pastel-yellow-hover)' : 'var(--text-navy-muted)', marginBottom: '1rem' }} />
        <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, marginBottom: '0.5rem' }}>Quiz Completed!</h2>
        <p style={{ fontSize: '1.1rem', marginBottom: '1.5rem', color: 'var(--text-navy-muted)' }}>
          You scored <strong style={{ color: 'var(--accent-purple)' }}>{score}</strong> out of <strong style={{ color: 'var(--text-navy)' }}>{quiz.length}</strong> questions!
        </p>
        
        <div style={{
          padding: '12px 24px',
          borderRadius: '12px',
          background: passed ? 'var(--pastel-green)' : 'rgba(239, 68, 68, 0.1)',
          color: passed ? 'green' : '#b91c1c',
          display: 'inline-block',
          fontWeight: 600,
          marginBottom: '2rem'
        }}>
          {passed ? "Excellent Job! You understood the material." : "Keep studying and try again!"}
        </div>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button onClick={handleRetakeSame} className="btn btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <RefreshCw size={16} /> Retake Same Quiz
          </button>
          <button onClick={handleGenerateNew} className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={16} /> Generate New Quiz
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: '2.5rem', maxWidth: '650px', margin: '0 auto' }}>
      {/* Header and Progress */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--primary-lavender-dark)', paddingBottom: '12px', marginBottom: '1.5rem' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-purple)', background: 'var(--primary-lavender)', padding: '4px 10px', borderRadius: '20px' }}>
          Question {currentIdx + 1} of {quiz.length}
        </span>
        <span style={{ fontSize: '0.9rem', color: 'var(--text-navy-muted)' }}>
          Score: {score}/{currentIdx + (isAnswered ? 1 : 0)}
        </span>
      </div>

      {/* Question */}
      <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.2rem', marginBottom: '1.5rem', lineHeight: '1.4' }}>
        {currentQuestion.question}
      </h3>

      {/* Options */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '2rem' }}>
        {currentQuestion.options.map((option, idx) => {
          let optionClass = "quiz-option";
          let icon = null;

          if (isAnswered) {
            if (idx === currentQuestion.correct_option_index) {
              optionClass += " correct";
              icon = <Check size={18} style={{ color: 'green' }} />;
            } else if (idx === selectedOption) {
              optionClass += " incorrect";
              icon = <X size={18} style={{ color: '#b91c1c' }} />;
            }
          } else if (idx === selectedOption) {
            optionClass += " active";
          }

          return (
            <div 
              key={idx}
              className={optionClass}
              onClick={() => handleOptionClick(idx)}
              style={{
                borderColor: idx === selectedOption && !isAnswered ? 'var(--accent-purple)' : undefined,
                background: idx === selectedOption && !isAnswered ? 'var(--primary-lavender)' : undefined,
                cursor: isAnswered ? 'default' : 'pointer'
              }}
            >
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                border: '2px solid var(--primary-lavender-dark)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.85rem',
                fontWeight: 'bold',
                color: 'var(--text-navy-muted)',
                flexShrink: 0
              }}>
                {String.fromCharCode(65 + idx)}
              </div>
              <div style={{ flexGrow: 1, fontSize: '0.95rem' }}>{option}</div>
              {icon}
            </div>
          );
        })}
      </div>

      {/* Explanation Box */}
      {isAnswered && (
        <div style={{
          padding: '1rem',
          borderRadius: '12px',
          background: 'rgba(255, 255, 255, 0.7)',
          borderLeft: '4px solid var(--accent-purple)',
          marginBottom: '2rem',
          fontSize: '0.9rem',
          lineHeight: '1.5'
        }}>
          <p style={{ fontWeight: 700, color: 'var(--text-navy)', marginBottom: '4px' }}>Explanation:</p>
          <p style={{ color: 'var(--text-navy-muted)' }}>{currentQuestion.explanation}</p>
        </div>
      )}

      {/* Action Footer */}
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        {!isAnswered ? (
          <button 
            className="btn btn-primary" 
            disabled={selectedOption === null}
            onClick={handleSubmit}
          >
            Submit Answer
          </button>
        ) : (
          <button 
            className="btn btn-primary" 
            onClick={handleNext}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
          >
            {currentIdx + 1 < quiz.length ? "Next Question" : "Finish Quiz"} <ChevronRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
};

export default QuizCard;
