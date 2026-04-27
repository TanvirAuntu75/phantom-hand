import React from 'react';

const HandStatePanel = ({ hands }) => {
  return (
    <div className="fixed top-6 right-6 w-64 z-10 pointer-events-auto space-y-3">
      {hands.length === 0 && (
        <div className="bg-bg/80 border border-inactive p-3 hud-bracket text-center">
          <span className="text-dim text-xs tracking-widest">NO TARGET ACQUIRED</span>
        </div>
      )}

      {hands.map((hand, i) => {
        // According to requirements: Left hand: magenta (#FF00C8), Right hand: cyan (#00E5FF)
        // Since tracker assigns IDs like "Hand_...", we will randomly pick or try to detect
        // For strict coloring requirement, let's alternate based on index or ID hash
        const isLeft = hand.id.includes('Left') || i % 2 === 0;
        const colorClass = isLeft ? 'text-leftHand border-leftHand' : 'text-rightHand border-rightHand';
        const bgClass = isLeft ? 'bg-leftHand/10' : 'bg-rightHand/10';

        return (
          <div key={hand.id} className={`bg-bg/80 border p-3 hud-bracket backdrop-blur-sm ${colorClass.split(' ')[1]}`}>
            <div className="flex justify-between items-center mb-1">
              <span className={`text-xs font-bold tracking-widest ${colorClass.split(' ')[0]}`}>
                TARGET {i + 1}
              </span>
              {hand.is_ghost && (
                <span className="text-ghostRed text-[10px] font-bold">[G]</span>
              )}
            </div>
            <div className="text-lg tracking-widest text-primary drop-shadow-[0_0_3px_rgba(0,229,255,0.5)]">
              {hand.gesture}
            </div>
            <div className="text-[9px] text-dim font-mono mt-1 truncate">
              ID: {hand.id}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default HandStatePanel;
