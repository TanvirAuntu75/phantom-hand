import React from 'react';

const GestureLog = ({ log }) => {
  // Ensure we always render 8 slots, even if empty
  const slots = Array.from({ length: 8 }).map((_, i) => log[i] || null);

  return (
    <div className="fixed bottom-6 left-6 w-64 z-10 pointer-events-auto">
      <div className="text-dim text-[10px] tracking-widest mb-2 border-b border-inactive pb-1">
        ACTION LOG
      </div>
      <div className="space-y-[2px] flex flex-col-reverse">
        {slots.map((entry, index) => {
          // Newest at index 0 (bottom of the UI stack due to flex-col-reverse or manual mapping)
          // Actually, we want newest at the bottom, fading out towards the top.
          // If log[0] is the newest, then index 0 should have highest opacity.
          const opacity = Math.max(0.1, 1 - (index * 0.15));

          return (
            <div
              key={index}
              className="text-[11px] tracking-wider h-4"
              style={{
                color: entry ? `rgba(0, 229, 255, ${opacity})` : 'transparent'
              }}
            >
              {entry || "---"}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default GestureLog;
