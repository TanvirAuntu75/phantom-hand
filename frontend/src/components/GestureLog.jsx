import React from 'react';

const GestureLog = ({ log }) => {
  const entries = Array.isArray(log) ? log.slice(0, 12) : [];

  return (
    <div className="bg-black/60 border border-phantom-cyan/50 p-4 h-full flex flex-col pointer-events-auto backdrop-blur-md shadow-[0_0_15px_rgba(0,229,255,0.1)] relative">
      {/* Corner Brackets */}
      <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-phantom-cyan"></div>
      <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-phantom-cyan"></div>
      <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-phantom-cyan"></div>
      <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-phantom-cyan"></div>

      {/* Header */}
      <div className="flex justify-between items-center mb-3 border-b border-phantom-cyan/30 pb-2">
        <span className="text-xs font-bold font-mono tracking-[0.3em] text-phantom-cyan">CMD_TERMINAL</span>
        <div className="flex space-x-1.5">
          <div className="w-1.5 h-1.5 bg-phantom-cyan animate-pulse shadow-[0_0_5px_#00E5FF]" />
          <div className="w-1.5 h-1.5 bg-phantom-cyan animate-pulse shadow-[0_0_5px_#00E5FF] [animation-delay:200ms]" />
        </div>
      </div>

      {/* Log Entries */}
      <div className="flex-1 flex flex-col-reverse space-y-reverse space-y-1.5 overflow-hidden font-mono mt-2">
        {entries.length === 0 ? (
          <div className="text-[10px] text-phantom-cyan/40 italic tracking-widest mt-2">
            AWAITING_SIGNAL...
          </div>
        ) : (
          entries.map((entry, index) => {
            const opacity = Math.max(0.2, 1 - (index * 0.15));
            const isCommand = typeof entry === 'string' && (
              entry.includes('CLEAR') || entry.includes('UNDO') || entry.includes('REDO') || entry.includes('SAVE') || entry.includes('CONFIRM')
            );
            return (
              <div 
                key={index} 
                className="text-[10px] flex items-start space-x-3 whitespace-nowrap"
                style={{ opacity }}
              >
                <span className={`shrink-0 tracking-widest ${isCommand ? 'text-white drop-shadow-[0_0_5px_white]' : 'text-phantom-cyan'}`}>
                  {isCommand ? '[SYS_CMD]' : '[POS_TRK]'}
                </span>
                <span className={`truncate uppercase tracking-widest ${index === 0 ? 'font-bold' : ''}`}>{entry}</span>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-2 border-t border-phantom-cyan/30 flex justify-between text-[8px] font-mono opacity-50 text-phantom-cyan tracking-widest">
        <span>LOG_ID: 0x8842</span>
        <span className="animate-pulse">_STREAMING_</span>
      </div>
    </div>
  );
};

export default GestureLog;
