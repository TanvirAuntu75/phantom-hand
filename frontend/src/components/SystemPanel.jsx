import React from 'react';

// Normalize landmark: handles both [x,y,z] arrays and {x,y,z} objects
const getLM = (lm) => Array.isArray(lm) ? { x: lm[0], y: lm[1], z: lm[2] || 0 } : (lm || { x: 0, y: 0, z: 0 });
const SystemPanel = ({ isConnected, telemetry, systemState }) => {
  const { fps = 0, latency = { total: 0 }, system = { cpu: 0, mem: 0 } } = telemetry || {};
  
  // Progress bar component for metrics
  const ProgressBar = ({ label, value, max = 100, color = "var(--color-phantom-cyan)" }) => {
    const percent = Math.min((value / max) * 100, 100);
    return (
      <div className="flex flex-col space-y-1 mb-2">
        <div className="flex justify-between text-[10px] text-phantom-cyan/70 uppercase font-mono">
          <span>{label}</span>
          <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-phantom-accent/40 relative overflow-hidden">
          <div 
            className="h-full transition-all duration-500 ease-out"
            style={{ 
              width: `${percent}%`, 
              backgroundColor: color,
              boxShadow: `0 0 10px ${color}`
            }} 
          />
        </div>
      </div>
    );
  };

  return (
    <div className="bg-black/60 border border-phantom-cyan p-4 w-72 pointer-events-auto backdrop-blur-md shadow-[0_0_15px_rgba(0,229,255,0.15)] relative">
      {/* Corner Brackets */}
      <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-phantom-cyan"></div>
      <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-phantom-cyan"></div>
      <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-phantom-cyan"></div>
      <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-phantom-cyan"></div>

      {/* ── HEADER ─────────────────────────────────────────────────────── */}
      <div className="flex justify-between items-start mb-4 border-b border-phantom-cyan/30 pb-2">
        <div>
          <h2 className="text-xl font-bold leading-none text-phantom-cyan tracking-widest font-mono glow-text">SYSTEM_OS</h2>
          <span className="text-[10px] text-phantom-cyan/50 tracking-[0.3em] font-mono">V.4.6.2_STABLE</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[8px] tracking-widest font-mono text-phantom-cyan">{isConnected ? 'ON' : 'OFF'}</span>
          <div className={`w-2 h-2 rounded-none ${isConnected ? 'bg-phantom-cyan animate-pulse shadow-[0_0_8px_#00E5FF]' : 'bg-phantom-alert'}`} />
        </div>
      </div>

      {/* ── PERFORMANCE_METRICS ─────────────────────────────────────────── */}
      <div className="space-y-4">
        <div className="flex justify-between items-end border-b border-phantom-cyan/20 pb-1">
          <span className="text-[10px] text-phantom-cyan/70 font-mono tracking-widest">PIPELINE_FPS</span>
          <span className="text-xl leading-none font-bold text-white font-mono drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]">{(fps || 0).toFixed(1)}</span>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col bg-phantom-cyan/5 p-2 border border-phantom-cyan/20">
            <span className="text-[8px] text-phantom-cyan/70 font-mono tracking-widest">LATENCY_MS</span>
            <span className="text-sm font-mono text-white">{(latency.total || 0).toFixed(1)}</span>
          </div>
          <div className="flex flex-col items-end bg-phantom-cyan/5 p-2 border border-phantom-cyan/20">
            <span className="text-[8px] text-phantom-cyan/70 font-mono tracking-widest">THREADS</span>
            <span className="text-sm font-mono text-white">08_ACT</span>
          </div>
        </div>

        <ProgressBar label="CPU_LOAD" value={system.cpu || 0} />
        <ProgressBar label="MEM_RESERVE" value={system.mem || 0} />
      </div>

      {/* ── FOOTER_READOUT ─────────────────────────────────────────────── */}
      <div className="mt-4 pt-2 border-t border-phantom-cyan/30 flex justify-between text-[8px] font-mono opacity-60 text-phantom-cyan">
        <span>0x00FF_ADR_PHTM</span>
        <span className="animate-pulse">_READING_</span>
      </div>
    </div>
  );
};

export default SystemPanel;
