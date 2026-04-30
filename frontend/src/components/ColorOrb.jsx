import React from 'react';

const ColorOrb = ({ color, index, total }) => {
  const radius = 22;
  const circumference = 2 * Math.PI * radius;
  const progress = (index / total) * circumference;

  let cssColor = color;
  let colorLabel = "UNKNOWN";
  
  if (Array.isArray(color)) {
    const [b, g, r] = color;
    cssColor = `rgb(${r}, ${g}, ${b})`;
    const toHex = (c) => {
      const hex = Math.round(c).toString(16);
      return hex.length === 1 ? "0" + hex : hex;
    };
    colorLabel = `#${toHex(r)}${toHex(g)}${toHex(b)}`.toUpperCase();
  } else if (typeof color === 'string') {
    cssColor = color;
    colorLabel = color.toUpperCase();
  }

  return (
    <div className="flex items-center space-x-6 pointer-events-auto">
      <div className="text-right flex flex-col justify-center">
        <span className="text-[10px] text-phantom-cyan/70 tracking-[0.3em] font-mono mb-1">CHROMA_SYNC</span>
        <span className="text-sm text-white font-mono drop-shadow-[0_0_5px_currentColor]" style={{ color: cssColor }}>{colorLabel}</span>
      </div>

      <div className="relative w-16 h-16 flex items-center justify-center">
        {/* Background Tracker */}
        <svg className="absolute inset-0 w-full h-full -rotate-90">
          <circle
            cx="32"
            cy="32"
            r={radius}
            fill="none"
            stroke="rgba(0, 229, 255, 0.2)"
            strokeWidth="3"
            strokeDasharray="4, 4"
          />
          {/* Active Level */}
          <circle
            cx="32"
            cy="32"
            r={radius}
            fill="none"
            stroke={cssColor}
            strokeWidth="3"
            strokeDasharray={`${progress} ${circumference}`}
            className="transition-all duration-500 ease-out"
            style={{ filter: `drop-shadow(0 0 8px ${cssColor})` }}
          />
        </svg>

        {/* Energy Core */}
        <div 
          className="w-8 h-8 rounded-sm transition-all duration-300 transform rotate-45 border border-white/50 animate-pulse"
          style={{ 
            backgroundColor: cssColor,
            boxShadow: `0 0 20px ${cssColor}, inset 0 0 10px rgba(255,255,255,0.5)`,
          }}
        />
        
        {/* Sequence Numbers */}
        <div className="absolute -bottom-2 -right-2 bg-black border border-phantom-cyan px-1.5 py-0.5 shadow-[0_0_10px_rgba(0,229,255,0.2)] flex items-center space-x-1">
          <span className="text-[10px] text-white font-mono">{index}</span>
          <span className="text-[10px] text-phantom-cyan/50 font-mono">/</span>
          <span className="text-[10px] text-phantom-cyan/50 font-mono">{total}</span>
        </div>
      </div>
    </div>
  );
};

export default ColorOrb;
