import React from 'react';

/**
 * PHANTOM CHROMA CORE
 * Visualizes the current drawing color and spectrum index.
 * Designed to look like a fusion reactor cell.
 */
const ColorOrb = ({ color, index, total }) => {
  // Calculate stroke-dasharray for the circular progress ring
  const radius = 18;
  const circumference = 2 * Math.PI * radius;
  const progress = (index / total) * circumference;

  // Handle color formatting (Backend sends BGR tuples as arrays like [0, 229, 255])
  let cssColor = color;
  let colorLabel = "UNKNOWN";
  
  if (Array.isArray(color)) {
    // Convert BGR array [B, G, R] to rgb(R, G, B) string
    const [b, g, r] = color;
    cssColor = `rgb(${r}, ${g}, ${b})`;
    // Convert to hex for the label
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
    <div className="flex items-center space-x-4 pointer-events-auto">
      {/* ── SPECTRAL_DATA ──────────────────────────────────────────────── */}
      <div className="text-right flex flex-col justify-center">
        <span className="text-[8px] text-phantom-accent tracking-[0.2em] font-bold">SPECTRUM_ID</span>
        <span className="text-[10px] text-white font-mono">{colorLabel}</span>
      </div>

      {/* ── REACTOR_CORE ───────────────────────────────────────────────── */}
      <div className="relative w-12 h-12 flex items-center justify-center">
        {/* Background Ring */}
        <svg className="absolute inset-0 w-full h-full -rotate-90">
          <circle
            cx="24"
            cy="24"
            r={radius}
            fill="none"
            stroke="var(--color-phantom-accent)"
            strokeWidth="2"
            strokeDasharray="2, 2"
          />
          {/* Progress Ring */}
          <circle
            cx="24"
            cy="24"
            r={radius}
            fill="none"
            stroke={cssColor}
            strokeWidth="2"
            strokeDasharray={`${progress} ${circumference}`}
            className="transition-all duration-500 ease-out"
            style={{ filter: `drop-shadow(0 0 5px ${cssColor})` }}
          />
        </svg>

        {/* Central Core */}
        <div 
          className="w-6 h-6 rounded-sm transition-all duration-300 transform rotate-45 border border-white border-opacity-50"
          style={{ 
            backgroundColor: cssColor,
            boxShadow: `0 0 15px ${cssColor}`,
          }}
        />
        
        {/* Index Indicator */}
        <div className="absolute -bottom-1 -right-1 bg-phantom-bg border border-phantom-accent text-[8px] px-1 font-bold">
          {index}/{total}
        </div>
      </div>
    </div>
  );
};

export default ColorOrb;
