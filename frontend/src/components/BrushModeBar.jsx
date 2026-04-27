import React from 'react';

const BrushModeBar = ({ activeMode, mode3d }) => {
  const modes = ['PNC', 'NEO', 'LSR', 'AIR', 'MRK', 'CAL', '3D'];

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 flex gap-1 z-10 pointer-events-auto bg-bg p-1 border border-inactive">
      {modes.map((mode) => {
                // Note: systemState.mode_3d is passed as a separate boolean, but the UI expects activeMode string
        // We'll fix this in HUDOverlay or here by checking a prop if mode === '3D'
        // Let's assume BrushModeBar receives mode3d boolean as well.
        const isActive = (mode === '3D' && mode3d) || (!mode3d && activeMode === mode);
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
