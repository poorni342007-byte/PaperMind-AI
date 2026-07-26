import React from 'react';

/**
 * Parses inline **bold** formatting into React nodes.
 */
const parseInlineFormatting = (text) => {
  if (!text) return text;
  // Regex to match **bold** text
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
      return (
        <strong key={index} style={{ fontWeight: 700, color: 'var(--text-navy)' }}>
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
};

/**
 * FormattedText component to cleanly render Markdown-style AI responses
 * without showing raw '###', '---', or '*' symbols.
 */
const FormattedText = ({ text, style = {} }) => {
  if (!text) return null;

  const lines = text.split('\n');
  const elements = [];

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    // Empty lines -> spacing
    if (!trimmed) {
      elements.push(<div key={`space-${index}`} style={{ height: '6px' }} />);
      return;
    }

    // Horizontal divider lines (e.g., '---' or '***')
    if (/^[\-\*_]{3,}$/.test(trimmed)) {
      elements.push(
        <hr 
          key={`hr-${index}`} 
          style={{ 
            border: 'none', 
            borderTop: '1px solid var(--primary-lavender-dark)', 
            margin: '12px 0',
            opacity: 0.6 
          }} 
        />
      );
      return;
    }

    // Header lines (e.g., '### Title', '## Title', '# Title')
    const headerMatch = trimmed.match(/^(#{1,6})\s+(.*)/);
    if (headerMatch) {
      let headerText = headerMatch[2].trim();
      // Remove enclosing bold markers if present e.g. **Title**
      if (headerText.startsWith('**') && headerText.endsWith('**')) {
        headerText = headerText.slice(2, -2);
      }
      elements.push(
        <h4 
          key={`header-${index}`} 
          style={{ 
            fontFamily: 'var(--font-display)', 
            fontWeight: 700, 
            fontSize: '1rem', 
            color: 'var(--text-navy)', 
            marginTop: index === 0 ? '0' : '14px', 
            marginBottom: '6px',
            lineHeight: '1.4'
          }}
        >
          {parseInlineFormatting(headerText)}
        </h4>
      );
      return;
    }

    // Nested or standard bullet points (e.g., '* ', '- ', '  * ')
    const bulletMatch = line.match(/^(\s*)[\*\-]\s+(.*)/);
    if (bulletMatch) {
      const indentLevel = Math.floor(bulletMatch[1].length / 2);
      const bulletText = bulletMatch[2].trim();
      elements.push(
        <div 
          key={`bullet-${index}`} 
          style={{ 
            display: 'flex', 
            alignItems: 'flex-start', 
            gap: '8px', 
            marginLeft: `${12 + indentLevel * 16}px`, 
            marginTop: '4px',
            marginBottom: '4px',
            lineHeight: '1.5'
          }}
        >
          <span style={{ color: 'var(--accent-purple)', fontWeight: 'bold', lineHeight: '1.4', flexShrink: 0 }}>
            {indentLevel > 0 ? '◦' : '•'}
          </span>
          <div style={{ flexGrow: 1 }}>
            {parseInlineFormatting(bulletText)}
          </div>
        </div>
      );
      return;
    }

    // Standard text paragraph
    elements.push(
      <div key={`p-${index}`} style={{ margin: '4px 0', lineHeight: '1.5' }}>
        {parseInlineFormatting(line)}
      </div>
    );
  });

  return (
    <div className="formatted-text" style={{ textAlign: 'left', ...style }}>
      {elements}
    </div>
  );
};

export default FormattedText;
