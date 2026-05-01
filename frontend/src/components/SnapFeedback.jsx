import React, { useEffect, useState } from 'react';

const SnapFeedback = ({ snappedShape }) => {
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState(null);

  useEffect(() => {
    if (snappedShape) {
      setData(snappedShape);
      setVisible(true);
      const timer = setTimeout(() => setVisible(false), 2500);
      return () => clearTimeout(timer);
    }
  }, [snappedShape]);

  if (!data) return null;

  return (
    <div className={`absolute top-16 left-1/2 -translate-x-1/2 z-50 pointer-events-none transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-8'}`}>
      <div className="studio-pill px-6 py-3 flex items-center space-x-4 bg-white/10 border-white/20 shadow-[0_8px_32px_rgba(255,255,255,0.1)]">

        {/* Animated Icon */}
        <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center relative overflow-hidden">
           <div className="absolute inset-0 bg-white opacity-0 animate-[pulse_1s_ease-out_1]" />
           <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
             <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
           </svg>
        </div>

        <div className="flex flex-col">
          <span className="text-xs text-gray-300 font-medium tracking-wide">Shape Recognized</span>
          <span className="text-lg font-bold text-white capitalize leading-none tracking-tight">
            {data.shape.replace(/_/g, ' ')}
          </span>
        </div>

      </div>
    </div>
  );
};

export default SnapFeedback;
