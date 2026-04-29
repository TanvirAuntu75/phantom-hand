import React from 'react';

/**
 * PHANTOM SYSTEM DIAGNOSTICS
 * High-fidelity system health and vision pipeline status.
 * Visualizes real-time performance telemetry.
 */
// Normalize landmark: handles both [x,y,z] arrays and {x,y,z} objects
const getLM = (lm) => Array.isArray(lm) ? { x: lm[0], y: lm[1], z: lm[2] || 0 } : (lm || { x: 0, y: 0, z: 0 });
const SystemPanel = ({ isConnected, telemetry, systemState }) => {
  const { fps = 0, latency = { total: 0 }, system = { cpu: 0, mem: 0 } } = telemetry || {};
  
  // Progress bar component for metrics
  const ProgressBar = ({ label, value, max = 100, color = "var(--color-phantom-cyan)" }) => {
    const percent = Math.min((value / max) * 100, 100);
    return (
      <div className="flex flex-col space-y-1 mb-2">
        <div className="flex justify-between text-[10px] text-phantom-accent uppercase">
          <span>{label}</span>
          <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-phantom-accent bg-opacity-30 relative overflow-hidden">
          <div 
            className="h-full transition-all duration-500 ease-out"
            style={{ 
              width: `${percent}%`, 
              backgroundColor: color,
              boxShadow: `0 0 8px ${color}`
            }} 
          />
        </div>
      </div>
    );
  };

  return (
    <div className="phantom-panel phantom-bracket p-4 w-72 pointer-events-auto">
      {/* ── HEADER ─────────────────────────────────────────────────────── */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-lg font-bold leading-none glow-text">PHANTOM_OS</h2>
          <span className="text-[10px] text-phantom-accent tracking-[0.3em]">VERSION_4.6.2_STABLE</span>
        </div>
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-phantom-cyan animate-pulse shadow-[0_0_10px_#00E5FF]' : 'bg-phantom-alert'}`} />
      </div>

      {/* ── STATUS_STRIP ────────────────────────────────────────────────── */}
      <div className="flex items-center space-x-2 mb-6 p-2 bg-phantom-cyan bg-opacity-5 border-l-2 border-phantom-cyan">
        <div className="text-[10px] text-phantom-cyan animate-data">
          {isConnected ? 'VISION_KERNEL_ONLINE' : 'CORE_DISCONNECTED'}
        </div>
      </div>

      {/* ── PERFORMANCE_METRICS ─────────────────────────────────────────── */}
      <div className="space-y-4">
        <div className="flex justify-between items-end border-b border-phantom-accent pb-1">
          <span className="text-[10px] text-phantom-accent">PIPELINE_FPS</span>
          <span className="text-xl leading-none font-bold">{(fps || 0).toFixed(1)}</span>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col">
            <span className="text-[8px] text-phantom-accent">LATENCY_MS</span>
            <span className="text-sm">{(latency.total || 0).toFixed(1)}</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-[8px] text-phantom-accent">THREADS</span>
            <span className="text-sm">08_ACTIVE</span>
          </div>
        </div>

        <ProgressBar label="CPU_LOAD" value={system.cpu || 0} />
        <ProgressBar label="MEM_RESERVE" value={system.mem || 0} />
      </div>

      {/* ── FOOTER_READOUT ─────────────────────────────────────────────── */}
      <div className="mt-4 pt-4 border-t border-phantom-accent flex justify-between text-[9px] font-mono opacity-50">
        <span>0x00FF_ADR_PHTM</span>
        <span className="animate-pulse">_READING_</span>
      </div>
    </div>
  );
};

export default SystemPanel;
