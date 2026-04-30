import React from 'react';

// Normalize landmark: handles both [x,y,z] arrays and {x,y,z} objects
const getLM = (lm) => Array.isArray(lm) ? { x: lm[0], y: lm[1], z: lm[2] || 0 } : (lm || { x: 0, y: 0, z: 0 });

const HandStatePanel = ({ hands }) => {
  return (
    <div className="flex flex-col space-y-4 pointer-events-auto">
      {hands.length === 0 ? (
        <div className="bg-black/60 border border-phantom-alert/50 p-4 text-center backdrop-blur-md shadow-[0_0_15px_rgba(255,61,0,0.15)]">
          <span className="text-phantom-alert text-[10px] tracking-[0.4em] font-mono animate-pulse drop-shadow-[0_0_5px_#FF3D00]">
            NO_TARGETS_ACQUIRED...
          </span>
        </div>
      ) : (
        hands.map((hand, i) => {
          const isGhost = hand.is_ghost;
          const accentColor = isGhost ? 'var(--color-phantom-alert)' : 'var(--color-phantom-cyan)';
          const bgColor = isGhost ? 'rgba(255, 61, 0, 0.05)' : 'rgba(0, 229, 255, 0.05)';
          const pos = hand.landmarks?.[0] ? getLM(hand.landmarks[0]) : { x: 0, y: 0, z: 0 };

          return (
            <div 
              key={hand.id} 
              className="bg-black/60 border p-4 relative backdrop-blur-md transition-colors duration-300"
              style={{
                borderColor: isGhost ? 'rgba(255, 61, 0, 0.5)' : 'rgba(0, 229, 255, 0.4)',
                backgroundColor: bgColor,
                boxShadow: `0 0 20px ${isGhost ? 'rgba(255, 61, 0, 0.1)' : 'rgba(0, 229, 255, 0.1)'}`
              }}
            >
              {/* Corner Details */}
              <div className="absolute top-0 left-0 w-2 h-2 border-t border-l" style={{ borderColor: accentColor }} />
              <div className="absolute top-0 right-0 w-2 h-2 border-t border-r" style={{ borderColor: accentColor }} />
              <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l" style={{ borderColor: accentColor }} />
              <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r" style={{ borderColor: accentColor }} />

              {/* ── TARGET_HEADER ─────────────────────────────────────────── */}
              <div className="flex justify-between items-start mb-3 border-b pb-2" style={{ borderColor: `${accentColor}40` }}>
                <div className="flex flex-col">
                  <span className="text-[12px] font-bold tracking-widest font-mono drop-shadow-[0_0_5px_currentColor]" style={{ color: accentColor }}>
                    TARGET_0{i + 1}
                  </span>
                  <span className="text-[8px] font-mono tracking-widest text-phantom-cyan/50">
                    TYPE: {isGhost ? 'GHOST_MODE' : 'LIVE_FEED'}
                  </span>
                </div>
                {isGhost && (
                  <div className="bg-phantom-alert text-black text-[8px] px-1.5 py-0.5 font-bold tracking-widest animate-pulse font-mono shadow-[0_0_8px_#FF3D00]">
                    TRK_LOST
                  </div>
                )}
              </div>

              {/* ── GESTURE_READOUT ───────────────────────────────────────── */}
              <div className="flex items-center justify-between mb-4">
                  <div className="text-xl font-bold font-mono tracking-wider drop-shadow-[0_0_8px_currentColor] uppercase" style={{ color: accentColor }}>
                    {hand.gesture}
                  </div>
                  <div className="text-[10px] font-mono text-phantom-cyan/50 tracking-widest bg-black/40 px-2 py-1 border" style={{borderColor: `${accentColor}30`}}>
                      CFD: {Math.round((hand.confidence || 0) * 100)}%
                  </div>
              </div>

              {/* ── SPATIAL_TELEMETRY ─────────────────────────────────────── */}
              <div className="grid grid-cols-3 gap-2 mb-4 bg-black/40 p-2 border" style={{borderColor: `${accentColor}30`}}>
                <div className="flex flex-col">
                  <span className="text-[8px] text-phantom-cyan/50 font-mono tracking-widest">POS_X</span>
                  <span className="text-[10px] text-white font-mono">{pos.x.toFixed(3)}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[8px] text-phantom-cyan/50 font-mono tracking-widest">POS_Y</span>
                  <span className="text-[10px] text-white font-mono">{pos.y.toFixed(3)}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[8px] text-phantom-cyan/50 font-mono tracking-widest">DEPTH</span>
                  <span className="text-[10px] text-white font-mono">{pos.z.toFixed(3)}</span>
                </div>
              </div>

              {/* ── SIGNAL_QUALITY ────────────────────────────────────────── */}
              <div className="flex flex-col space-y-1">
                <div className="flex justify-between text-[8px] text-phantom-cyan/70 font-mono tracking-widest">
                  <span>SIG_QUAL</span>
                  <span>{isGhost ? 'ERR' : 'OPT'}</span>
                </div>
                <div className="h-[2px] bg-black/50 w-full overflow-hidden border border-white/5">
                  <div 
                    className="h-full transition-all duration-300"
                    style={{ 
                      width: isGhost ? '35%' : '98%',
                      backgroundColor: accentColor,
                      boxShadow: `0 0 5px ${accentColor}`
                    }} 
                  />
                </div>
              </div>

              {/* ── UNIQUE_IDENTIFIER ─────────────────────────────────────── */}
              <div className="mt-3 text-[8px] font-mono tracking-widest text-phantom-cyan/40 flex justify-between">
                <span>UID: {String(hand.id || "NULL").toUpperCase()}</span>
                <span>[{isGhost ? 'DEAD_RECKONING' : 'AI_TRACKING'}]</span>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export default HandStatePanel;
