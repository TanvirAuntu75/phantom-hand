import React from 'react';

const BrushModeBar = ({ activeMode, mode3d }) => {
  const modes = [
    { id: 'PNC', label: 'PNC', desc: 'PENCIL' },
    { id: 'NEO', label: 'NEO', desc: 'NEON' },
    { id: 'LSR', label: 'LSR', desc: 'LASER' },
    { id: 'AIR', label: 'AIR', desc: 'SPRAY' },
    { id: 'CHK', label: 'CHK', desc: 'CHALK' },
    { id: '3D',  label: '3D',  desc: 'Z_AXIS'  }
  ];

  return (
    <div className="flex items-center space-x-2">
      {modes.map((m) => {
        const isActive = (m.id === '3D' && mode3d) || (!mode3d && activeMode === m.id);
        
        return (
          <div
            key={m.id}
            className={`
              group relative flex flex-col items-center justify-center w-16 h-12
              border transition-all duration-300 cursor-pointer overflow-hidden
              ${isActive 
                ? 'bg-phantom-cyan/20 border-phantom-cyan shadow-[0_0_15px_rgba(0,229,255,0.3)]'
                : 'bg-black/40 border-phantom-cyan/30 hover:border-phantom-cyan/70 hover:bg-phantom-cyan/10'
              }
            `}
          >
            {/* Active Top Bar */}
            {isActive && (
              <div className="absolute top-0 left-0 w-full h-[3px] bg-phantom-cyan shadow-[0_0_10px_#00E5FF]" />
            )}

            {/* Label */}
            <span className={`text-xs font-mono tracking-widest transition-colors ${isActive ? 'text-white drop-shadow-[0_0_5px_white]' : 'text-phantom-cyan/70 group-hover:text-phantom-cyan'}`}>
              {m.label}
            </span>

            {/* Tooltip */}
            <div className={`
              absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1
              bg-black/90 border border-phantom-cyan text-[10px] whitespace-nowrap font-mono tracking-widest text-phantom-cyan
              transition-opacity duration-200 pointer-events-none opacity-0 group-hover:opacity-100 shadow-[0_0_10px_rgba(0,229,255,0.2)]
            `}>
              {m.desc}
            </div>

            {/* Decorative Dots */}
            <div className="absolute bottom-1 w-full flex justify-center space-x-1">
                 <div className={`w-0.5 h-0.5 ${isActive ? 'bg-phantom-cyan' : 'bg-phantom-cyan/30'}`} />
                 <div className={`w-0.5 h-0.5 ${isActive ? 'bg-phantom-cyan' : 'bg-phantom-cyan/30'}`} />
                 <div className={`w-0.5 h-0.5 ${isActive ? 'bg-phantom-cyan' : 'bg-phantom-cyan/30'}`} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default BrushModeBar;
