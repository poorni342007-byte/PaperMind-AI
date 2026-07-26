import React from 'react';
import { Sparkles, Cpu, Search, Brain } from 'lucide-react';

/**
 * LiveLoader Component
 * Replaces generic static spinners with an interactive, live AI pulsating orb,
 * orbiting glow ring, and animated wave dots.
 */
const LiveLoader = ({ 
  text = "Processing...", 
  size = "medium", 
  icon = "sparkles", // "sparkles" | "brain" | "cpu" | "search"
  inline = false,
  style = {}
}) => {
  // Render chosen central live icon
  const renderIcon = (iconSize) => {
    switch (icon) {
      case "brain":
        return <Brain size={iconSize} className="live-icon-pulse" />;
      case "cpu":
        return <Cpu size={iconSize} className="live-icon-pulse" />;
      case "search":
        return <Search size={iconSize} className="live-icon-pulse" />;
      case "sparkles":
      default:
        return <Sparkles size={iconSize} className="live-icon-pulse" />;
    }
  };

  if (inline) {
    return (
      <span className="live-loader-inline" style={style}>
        <span className="live-loader-orb inline-orb">
          {renderIcon(14)}
        </span>
        {text && <span className="live-loader-text-inline">{text}</span>}
        <span className="live-wave-dots-inline">
          <span className="wave-dot d1" />
          <span className="wave-dot d2" />
          <span className="wave-dot d3" />
        </span>
      </span>
    );
  }

  const iconSizes = {
    small: 18,
    medium: 26,
    large: 36
  };

  const containerPadding = {
    small: '0.5rem',
    medium: '1.5rem',
    large: '3rem'
  };

  return (
    <div className={`live-loader-container ${size}`} style={{ padding: containerPadding[size] || '1rem', ...style }}>
      {/* Central Pulsing Live AI Orb */}
      <div className={`live-loader-orb-wrapper ${size}`}>
        <div className="live-orb-aura" />
        <div className="live-orbit-ring" />
        <div className="live-orb-core">
          {renderIcon(iconSizes[size] || 24)}
        </div>
      </div>

      {/* Live Status Text with Wave Dots */}
      {text && (
        <div className="live-loader-status">
          <span className="live-loader-text">{text}</span>
          <span className="live-wave-dots">
            <span className="wave-dot d1" />
            <span className="wave-dot d2" />
            <span className="wave-dot d3" />
          </span>
        </div>
      )}
    </div>
  );
};

export default LiveLoader;
