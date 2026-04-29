import React from 'react';

// Normalize landmark: handles both [x,y,z] arrays and {x,y,z} objects
const getLM = (lm) => Array.isArray(lm) ? { x: lm[0], y: lm[1], z: lm[2] || 0 } : (lm || { x: 0, y: 0, z: 0 });

/**
 * PHANTOM TARGET ACQUISITION PANEL
 * Real-time telemetry for tracked hand entities.
 * Displays identity, gesture classification, and spatial coordinates.
 */
const HandStatePanel = ({ hands }) => {
  return (
    <div className="flex flex-col space-y-4 pointer-events-auto">
      {hands.length === 0 ? (
        <div className="phantom-panel phantom-bracket p-4 text-center border-phantom-alert bg-phantom-alert bg-opacity-5">
          <span className="text-phantom-alert text-[10px] tracking-[0.4em] animate-pulse">
            SEARCHING_FOR_TARGETS...
          </span>
        </div>
      ) : (
        hands.map((hand, i) => {
          // Tactical color mapping
          const isPrimary = i === 0;
          const accentColor = hand.is_ghost ? 'var(--color-phantom-alert)' : 'var(--color-phantom-cyan)';
          
          // Get primary landmark (Wrist or Index Tip) for readout
          const pos = hand.landmarks?.[0] ? getLM(hand.landmarks[0]) : { x: 0, y: 0, z: 0 };

          return (
            <div 
              key={hand.id} 
              className="phantom-panel phantom-bracket p-4 relative"
              style={{ borderColor: hand.is_ghost ? 'rgba(255, 61, 0, 0.3)' : 'rgba(0, 48, 64, 0.5)' }}
            >
              {/* ── TARGET_HEADER ─────────────────────────────────────────── */}
              <div className="flex justify-between items-start mb-2">
                <div className="flex flex-col">
                  <span className="text-[10px] font-bold tracking-widest" style={{ color: accentColor }}>
                    TARGET_0{i + 1}
                  </span>
                  <span className="text-[8px] text-phantom-accent">TYPE: {hand.is_ghost ? 'PHANTOM_PERSISTENT' : 'AI_LIVE_FEED'}</span>
                </div>
                {hand.is_ghost && (
                  <div className="bg-phantom-alert text-phantom-bg text-[8px] px-1 font-bold animate-pulse">
                    TRACK_LOST_RECOVERING
                  </div>
                )}
              </div>

              {/* ── GESTURE_READOUT ───────────────────────────────────────── */}
              <div className="text-xl font-bold mb-3 glow-text" style={{ color: accentColor }}>
                {hand.gesture}
              </div>

              {/* ── SPATIAL_TELEMETRY ─────────────────────────────────────── */}
              <div className="grid grid-cols-3 gap-2 mb-4 border-t border-phantom-accent pt-2">
                <div className="flex flex-col">
                  <span className="text-[8px] text-phantom-accent">POS_X</span>
                  <span className="text-[10px]">{pos.x.toFixed(3)}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[8px] text-phantom-accent">POS_Y</span>
                  <span className="text-[10px]">{pos.y.toFixed(3)}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[8px] text-phantom-accent">DEPTH_Z</span>
                  <span className="text-[10px]">{pos.z.toFixed(3)}</span>
                </div>
              </div>

              {/* ── SIGNAL_QUALITY ────────────────────────────────────────── */}
              <div className="flex flex-col space-y-1">
                <div className="flex justify-between text-[8px] text-phantom-accent">
                  <span>SIGNAL_STABILITY</span>
                  <span>{hand.is_ghost ? '32%' : '98%'}</span>
                </div>
                <div className="h-[2px] bg-phantom-accent bg-opacity-30 w-full">
                  <div 
                    className="h-full transition-all duration-300"
                    style={{ 
                      width: hand.is_ghost ? '32%' : '98%', 
                      backgroundColor: accentColor 
                    }} 
                  />
                </div>
              </div>

              {/* ── UNIQUE_IDENTIFIER ─────────────────────────────────────── */}
              <div className="mt-3 text-[8px] text-phantom-accent font-mono truncate opacity-30">
                UID: {String(hand.id || "UNKNOWN").toUpperCase()}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export default HandStatePanel;
