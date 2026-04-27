import React from 'react';

const ColorOrb = ({ color, index, total }) => {
  return (
    <div className="fixed bottom-6 right-6 flex items-center gap-3 z-10 bg-bg/80 p-2 border border-inactive hud-bracket pointer-events-auto">
      <div className="text-right">
        <div className="text-xs text-dim tracking-widest">COLOR</div>
        <div className="text-sm text-primary tracking-widest">{index}/{total}</div>
      </div>
      <div
        className="w-10 h-10 border border-primary shadow-[0_0_10px_rgba(0,229,255,0.3)]"
        style={{ backgroundColor: color }}
      ></div>
    </div>
  );
};

export default ColorOrb;
