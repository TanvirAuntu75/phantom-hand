import React from 'react';

const SystemPanel = ({ isConnected, fps, systemState }) => {
  const pad = (num, len = 2) => String(num).padStart(len, '0');

  return (
    <div className="fixed top-6 left-6 w-72 bg-bg/80 border border-inactive hud-bracket p-4 z-10 backdrop-blur-sm pointer-events-auto">
      <div className="text-primary text-xl font-bold tracking-widest mb-1 shadow-primary drop-shadow-[0_0_5px_rgba(0,229,255,0.5)]">
        PHANTOM HAND
      </div>

      <div className="flex items-center gap-2 mb-4 text-xs">
        <div className={`w-2 h-2 ${isConnected ? 'bg-primary' : 'bg-ghostRed'} animate-pulse`}></div>
        <span className={isConnected ? 'text-primary' : 'text-ghostRed'}>
          {isConnected ? 'SYSTEM ONLINE' : 'CONNECTION LOST'}
        </span>
      </div>

      <div className="space-y-1 text-sm tracking-wider">
        <div className="flex justify-between">
          <span className="text-dim">FPS</span>
          <span className="text-primary">{pad(Math.round(fps), 3)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dim">BRUSH MODE</span>
          <span className="text-primary">{systemState.brushMode}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dim">ACTIVE LAYER</span>
          <span className="text-primary">{systemState.activeLayer}/{systemState.totalLayers}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dim">BRUSH SIZE</span>
          <span className="text-primary">{pad(systemState.brushSize)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dim">MIRROR</span>
          <span className="text-primary">
            H:{systemState.mirrorH ? '1' : '0'} V:{systemState.mirrorV ? '1' : '0'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SystemPanel;
