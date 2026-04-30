import React, { useEffect, useState } from 'react';

const SnapFeedback = ({ snappedShape }) => {
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState(null);

  useEffect(() => {
    if (snappedShape) {
      setData(snappedShape);
      setVisible(true);
      const timer = setTimeout(() => setVisible(false), 1500);
      return () => clearTimeout(timer);
    }
  }, [snappedShape]);

  if (!data) return null;

  return (
    <div className={`absolute top-[40%] left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 pointer-events-none transition-all duration-300 ${visible ? 'opacity-100 scale-100' : 'opacity-0 scale-[1.15]'}`}>
      <div className="flex flex-col items-center">
        {/* Reticle */}
        <div className="relative w-56 h-56 mb-6">
          <div className="absolute inset-0 border border-phantom-cyan/30 rounded-full animate-[spin_6s_linear_infinite]" />
          <div className="absolute inset-2 border-2 border-dashed border-phantom-cyan/50 rounded-full animate-[spin_8s_linear_infinite_reverse]" />
          <div className="absolute inset-6 border-t-[3px] border-b-[3px] border-white rounded-full animate-[spin_2s_ease-in-out_infinite] shadow-[0_0_15px_rgba(255,255,255,0.5)]" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-px h-[110%] bg-phantom-cyan/40" />
            <div className="h-px w-[110%] bg-phantom-cyan/40 absolute" />
            <div className="w-4 h-4 bg-white shadow-[0_0_10px_white] rotate-45 animate-pulse" />
          </div>
        </div>

        {/* Readout */}
        <div className="bg-black/80 border border-white p-5 backdrop-blur-md text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-white/5 animate-pulse" />
          <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-white"></div>
          <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-white"></div>
          <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-white"></div>
          <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-white"></div>

          <div className="text-[10px] text-phantom-cyan tracking-[0.4em] font-mono mb-2 relative z-10">
             GEOMETRY_CONFORMITY_LOCKED
          </div>
          <div className="text-4xl font-bold text-white font-mono tracking-widest uppercase drop-shadow-[0_0_10px_white] relative z-10">
            {data.shape}
          </div>
          <div className="mt-4 pt-3 border-t border-white/30 flex justify-center space-x-6 relative z-10">
             <div className="flex flex-col items-center">
               <span className="text-[8px] text-phantom-cyan/70 font-mono tracking-widest">ACCURACY</span>
               <span className="text-sm font-bold text-white font-mono">{Math.round(data.confidence * 100)}%</span>
             </div>
             <div className="w-px h-8 bg-white/30" />
             <div className="flex flex-col items-center">
               <span className="text-[8px] text-phantom-cyan/70 font-mono tracking-widest">STATUS</span>
               <span className="text-sm font-bold text-white font-mono">OK</span>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SnapFeedback;
