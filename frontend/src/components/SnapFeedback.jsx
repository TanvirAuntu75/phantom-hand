import React, { useEffect, useState } from 'react';

/**
 * PHANTOM GEOMETRY LOCK FEEDBACK
 * Provides a high-impact visual notification when the engine 
 * successfully snaps a freeform stroke into a geometric primitive.
 */
const SnapFeedback = ({ snappedShape }) => {
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState(null);

  useEffect(() => {
    if (snappedShape) {
      setData(snappedShape);
      setVisible(true);

      // Animation lifecycle
      const timer = setTimeout(() => {
        setVisible(false);
      }, 1200);

      return () => clearTimeout(timer);
    }
  }, [snappedShape]);

  if (!data) return null;

  return (
    <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[60%] z-50 pointer-events-none transition-all duration-300 ${visible ? 'opacity-100 scale-100' : 'opacity-0 scale-110'}`}>
      <div className="flex flex-col items-center">
        {/* ── LOCK_ON_RETICLE ─────────────────────────────────────────── */}
        <div className="relative w-48 h-48 mb-4">
          <div className="absolute inset-0 border-2 border-white border-opacity-20 animate-[spin_4s_linear_infinite]" />
          <div className="absolute inset-4 border-t-4 border-b-4 border-white animate-[pulse_0.5s_ease-in-out_infinite]" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-px h-full bg-white opacity-20" />
            <div className="h-px w-full bg-white opacity-20 absolute" />
          </div>
        </div>

        {/* ── DATA_READOUT ────────────────────────────────────────────── */}
        <div className="phantom-panel phantom-bracket p-4 bg-white bg-opacity-10 border-white text-center">
          <div className="text-[10px] text-white text-opacity-60 tracking-[0.3em] mb-1">
             GEOMETRY_CONFORMITY_LOCKED
          </div>
          <div className="text-3xl font-bold text-white glow-text tracking-widest uppercase">
            {data.shape}
          </div>
          <div className="mt-2 flex justify-center space-x-4">
             <div className="flex flex-col">
               <span className="text-[8px] text-white opacity-40">ACCURACY</span>
               <span className="text-xs font-bold text-white">{Math.round(data.confidence * 100)}%</span>
             </div>
             <div className="w-px h-full bg-white opacity-20" />
             <div className="flex flex-col">
               <span className="text-[8px] text-white opacity-40">VERTICES</span>
               <span className="text-xs font-bold text-white">SNAP_OK</span>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SnapFeedback;
