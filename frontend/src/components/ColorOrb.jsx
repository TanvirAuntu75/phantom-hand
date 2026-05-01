import React from 'react';

const ColorOrb = ({ color, index, total }) => {
  let cssColor = color;
  
  if (Array.isArray(color)) {
    const [b, g, r] = color;
    cssColor = `rgb(${r}, ${g}, ${b})`;
  } else if (typeof color === 'string') {
    cssColor = color;
  }

  // Smooth arc calculation for SVG
  const radius = 20;
  const circumference = 2 * Math.PI * radius;
  const progress = (index / total) * circumference;

  return (
    <div className="flex items-center space-x-4 pointer-events-auto group cursor-pointer">
      <div className="relative w-12 h-12 flex items-center justify-center btn-hover">
        {/* Progress Arc */}
        <svg className="absolute inset-0 w-full h-full -rotate-90 transform group-hover:scale-110 transition-transform duration-300">
          <circle cx="24" cy="24" r={radius} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />
          <circle
            cx="24"
            cy="24"
            r={radius}
            fill="none"
            stroke={cssColor}
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray={`${progress} ${circumference}`}
            className="transition-all duration-500 ease-out"
          />
        </svg>

        {/* Center Color Blob */}
        <div 
          className="w-6 h-6 rounded-full transition-all duration-300 shadow-md group-hover:shadow-lg"
          style={{ backgroundColor: cssColor }}
        />
      </div>
    </div>
  );
};

export default ColorOrb;
