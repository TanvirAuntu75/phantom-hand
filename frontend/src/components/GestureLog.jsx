import React from 'react';

const GestureLog = ({ log }) => {
  const entries = Array.isArray(log) ? log.slice(0, 5) : [];

  if (entries.length === 0) return null;

  return (
    <div className="flex flex-col-reverse space-y-reverse space-y-2 pointer-events-none">
      {entries.map((entry, index) => {
        const isCommand = typeof entry === 'string' && (
          entry.includes('CLEAR') || entry.includes('UNDO') || entry.includes('REDO') || entry.includes('SAVE') || entry.includes('CONFIRM')
        );

        // Only show commands as prominent toasts, hide basic tracking noise
        if (!isCommand && index !== 0) return null;

        const opacity = Math.max(0.4, 1 - (index * 0.25));
        const scale = Math.max(0.85, 1 - (index * 0.05));

        return (
          <div
            key={index}
            className={`studio-pill px-4 py-2 flex items-center space-x-2 w-max origin-left transition-all duration-300 ${isCommand ? 'bg-white/10 border-white/20' : 'bg-studio-glass'}`}
            style={{ opacity, transform: `scale(${scale})` }}
          >
            {isCommand ? (
              <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
            ) : null}
            <span className={`text-xs font-medium tracking-wide ${isCommand ? 'text-white' : 'text-studio-muted'} capitalize`}>
              {entry.replace(/_/g, ' ').toLowerCase()}
            </span>
          </div>
        );
      })}
    </div>
  );
};

export default GestureLog;
