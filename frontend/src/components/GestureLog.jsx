import React from 'react';

/**
 * PHANTOM EVENT CONSOLE
 * A scrolling terminal-style log of system events, gesture detections, and commands.
 */
const GestureLog = ({ log }) => {
  const entries = Array.isArray(log) ? log.slice(0, 10) : [];

  return (
    <div className="phantom-panel phantom-bracket p-4 h-full flex flex-col pointer-events-auto">
      {/* ── LOG_HEADER ──────────────────────────────────────────────────── */}
      <div className="flex justify-between items-center mb-3 border-b border-phantom-accent pb-1">
        <span className="text-[10px] font-bold tracking-[0.3em]">EVENT_LOG_STREAM</span>
        <div className="flex space-x-1">
          <div className="w-1 h-1 bg-phantom-cyan rounded-full animate-pulse" />
          <div className="w-1 h-1 bg-phantom-cyan rounded-full animate-pulse [animation-delay:200ms]" />
        </div>
      </div>

      {/* ── LOG_STREAM ──────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col-reverse space-y-reverse space-y-1 overflow-hidden font-mono">
        {entries.length === 0 ? (
          <div className="text-[10px] text-phantom-accent italic opacity-30">
            WAITING_FOR_INPUT...
          </div>
        ) : (
          entries.map((entry, index) => {
            const opacity = Math.max(0.2, 1 - (index * 0.1));
            // entry is now just the gesture string from the hook
            const isCommand = typeof entry === 'string' && (
              entry.includes('CLEAR') || entry.includes('UNDO') || entry.includes('REDO')
            );
            return (
              <div 
                key={index} 
                className="text-[10px] flex items-start space-x-2 whitespace-nowrap"
                style={{ opacity }}
              >
                <span className={`shrink-0 ${isCommand ? 'text-white' : 'text-phantom-cyan'}`}>
                  {isCommand ? '[EXE_OK]' : '[GESTURE]'}
                </span>
                <span className="truncate uppercase font-bold">{entry}</span>
              </div>
            );
          })
        )}
      </div>

      {/* ── FOOTER_STATUS ───────────────────────────────────────────────── */}
      <div className="mt-3 text-[8px] text-phantom-accent flex justify-between opacity-50">
        <span>STRM_ID: 0x8842</span>
        <span className="animate-pulse">_SYNCED_</span>
      </div>
    </div>
  );
};

export default GestureLog;
