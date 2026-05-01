import React, { useEffect, useState } from 'react';

const GestureIndicator = ({ gesture }) => {
  const [displayGesture, setDisplayGesture] = useState('HOVER');

  useEffect(() => {
    if (!gesture) return;
    const timer = setTimeout(() => {
      setDisplayGesture(gesture);
    }, 100); // Small debounce
    return () => clearTimeout(timer);
  }, [gesture]);

  const isActive = displayGesture !== 'HOVER' && displayGesture !== undefined;

  return (
    <div className={`absolute top-24 left-1/2 -translate-x-1/2 z-40 pointer-events-none transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] ${isActive ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
      <div className="studio-pill px-6 py-2 bg-white/10 border-white/10 shadow-[0_4px_24px_rgba(0,0,0,0.2)] flex items-center space-x-3">
         <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
         <span className="text-sm font-medium text-white tracking-wide capitalize">
           {displayGesture.replace(/_/g, ' ').toLowerCase()}
         </span>
      </div>
    </div>
  );
};

export default GestureIndicator;
