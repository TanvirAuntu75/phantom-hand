import React from 'react';

const BrushModeBar = ({ activeMode }) => {
  const modes = ['PNC', 'NEO', 'LSR', 'AIR', 'MRK', 'CAL'];

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 flex gap-1 z-10 pointer-events-auto bg-bg p-1 border border-inactive">
      {modes.map((mode) => {
        const isActive = activeMode === mode;
        return (
          <div
            key={mode}
            className={`w-12 h-8 flex items-center justify-center text-xs tracking-widest cursor-pointer
              ${isActive ? 'bg-primary text-bg font-bold' : 'bg-inactive text-dim border border-transparent'}
            `}
          >
            {mode}
          </div>
        );
      })}
    </div>
  );
};

export default BrushModeBar;
