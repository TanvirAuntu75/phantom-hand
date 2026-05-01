import React from 'react';

const HandStatePanel = ({ hands }) => {
  if (!hands || hands.length === 0) return null;

  return (
    <div className="flex space-x-3">
      {hands.map((hand, i) => {
        const isGhost = hand.is_ghost;

        return (
          <div
            key={hand.id}
            className="studio-pill px-4 py-2 flex items-center space-x-3 transition-colors duration-300"
            style={{
              backgroundColor: isGhost ? 'rgba(255, 113, 91, 0.1)' : 'rgba(255, 255, 255, 0.05)',
              borderColor: isGhost ? 'rgba(255, 113, 91, 0.3)' : 'rgba(255, 255, 255, 0.1)'
            }}
          >
            {/* Identity/Status */}
            <div className={`w-2 h-2 rounded-full ${isGhost ? 'bg-studio-accent animate-pulse' : 'bg-studio-secondary'}`} />

            <div className="flex flex-col">
              <span className="text-[10px] text-studio-muted uppercase tracking-wider font-semibold">
                Hand 0{i + 1}
              </span>
              <span className="text-sm font-semibold text-white capitalize leading-tight">
                {hand.gesture ? hand.gesture.replace(/_/g, ' ').toLowerCase() : 'Hover'}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default HandStatePanel;
