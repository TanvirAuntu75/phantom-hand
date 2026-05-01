import React from 'react';

const BrushModeBar = ({ activeMode, mode3d }) => {
  const modes = [
    { id: 'PNC', label: 'Pencil', icon: 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z' },
    { id: 'AIR', label: 'Airbrush', icon: 'M12 2v20m-5-2l5 2 5-2M4 10h16M7 6h10M6 14h12' }, // Abstract representation
    { id: 'NEO', label: 'Neon', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
    { id: '3D',  label: '3D Orbit', icon: 'M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1-11v6h2v-6h-2zm0-4v2h2V7h-2z' }
  ];

  return (
    <div className="flex items-center space-x-2">
      {modes.map((m) => {
        const isActive = (m.id === '3D' && mode3d) || (!mode3d && activeMode === m.id);
        
        return (
          <div
            key={m.id}
            className={`
              group relative flex items-center justify-center w-12 h-12 rounded-full
              transition-all duration-300 cursor-pointer
              ${isActive 
                ? 'bg-studio-accent text-white shadow-glow transform scale-110'
                : 'text-studio-muted hover:bg-studio-glassLight hover:text-white'
              }
            `}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d={m.icon} />
            </svg>

            {/* Tooltip */}
            <div className="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-gray-800 text-white text-xs rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none shadow-lg font-medium">
              {m.label}
              {/* Tooltip Arrow */}
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full border-[5px] border-transparent border-t-gray-800"></div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default BrushModeBar;
