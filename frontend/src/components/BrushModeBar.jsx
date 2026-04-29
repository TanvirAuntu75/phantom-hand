import React from 'react';

/**
 * PHANTOM BRUSH SELECTOR
 * Tactical segmented control for switching drawing modes and 3D states.
 */
const BrushModeBar = ({ activeMode, mode3d }) => {
  const modes = [
    { id: 'PNC', label: 'PNC', desc: 'PENCIL' },
    { id: 'NEO', label: 'NEO', desc: 'NEON_GLOW' },
    { id: 'LSR', label: 'LSR', desc: 'LASER_BEAM' },
    { id: 'AIR', label: 'AIR', desc: 'MIST_SPRAY' },
    { id: 'CHK', label: 'CHK', desc: 'CHALK_DUST' },
    { id: '3D',  label: '3D',  desc: 'Z_SPATIAL'  }
  ];

  return (
    <div className="flex items-center space-x-1">
      {modes.map((m) => {
        const isActive = (m.id === '3D' && mode3d) || (!mode3d && activeMode === m.id);
        
        return (
          <div
            key={m.id}
            className={`
              group relative flex flex-col items-center justify-center w-14 h-10 
              border transition-all duration-300 cursor-pointer overflow-hidden
              ${isActive 
                ? 'bg-phantom-cyan bg-opacity-20 border-phantom-cyan' 
                : 'bg-phantom-bg border-phantom-accent hover:border-phantom-cyan hover:bg-phantom-accent hover:bg-opacity-20'
              }
            `}
          >
            {/* ── SELECTION_INDICATOR ──────────────────────────────────────── */}
            {isActive && (
              <div className="absolute top-0 left-0 w-full h-[2px] bg-phantom-cyan glow-border shadow-[0_0_10px_#00E5FF]" />
            )}

            {/* ── MODE_LABEL ─────────────────────────────────────────────── */}
            <span className={`text-[10px] font-bold tracking-tighter ${isActive ? 'text-phantom-cyan' : 'text-phantom-accent group-hover:text-phantom-cyan'}`}>
              {m.label}
            </span>

            {/* ── TOOLTIP_DESCRIPTIVE ─────────────────────────────────────── */}
            <div className={`
              absolute -top-10 left-1/2 -translate-x-1/2 px-2 py-1 
              bg-phantom-bg border border-phantom-cyan text-[8px] whitespace-nowrap
              transition-opacity duration-300 pointer-events-none opacity-0 group-hover:opacity-100
              phantom-bracket
            `}>
              {m.desc}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default BrushModeBar;
