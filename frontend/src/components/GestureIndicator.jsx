import React, { useEffect, useState } from 'react';

const ICON_MAP = {
  DRAW: '●',
  ERASE: '✕',
  UNDO: '⟲',
  REDO: '⟳',
  CLEAR: '⎚',
  SHAPE: '⬡',
  COLOR: '◈',
  SIZE: '◧',
  HOVER: '·'
};

const GestureIndicator = ({ gesture }) => {
  const [displayGesture, setDisplayGesture] = useState('SYSTEM_IDLE');
  const [isChanging, setIsChanging] = useState(false);

  useEffect(() => {
    if (!gesture) return;
    setIsChanging(true);
    const timer = setTimeout(() => {
      setDisplayGesture(gesture === 'HOVER' ? 'SYSTEM_IDLE' : gesture);
      setIsChanging(false);
    }, 150);
    return () => clearTimeout(timer);
  }, [gesture]);

  const icon = ICON_MAP[gesture] || '·';
  const isActive = gesture !== 'HOVER' && gesture !== undefined;

  return (
    <div className="absolute top-8 left-1/2 -translate-x-1/2 z-40 pointer-events-none transition-all duration-300">
      <div className={`
        flex items-center space-x-6 px-8 py-3 transition-all duration-300 backdrop-blur-md relative
        border ${isActive ? 'border-phantom-cyan bg-phantom-cyan/10 shadow-[0_0_15px_rgba(0,229,255,0.2)]' : 'border-phantom-cyan/30 bg-black/40'}
      `}>
        {/* Frame Brackets */}
        <div className="absolute top-0 left-0 w-2 h-2 border-t-[2px] border-l-[2px] border-phantom-cyan"></div>
        <div className="absolute top-0 right-0 w-2 h-2 border-t-[2px] border-r-[2px] border-phantom-cyan"></div>
        <div className="absolute bottom-0 left-0 w-2 h-2 border-b-[2px] border-l-[2px] border-phantom-cyan"></div>
        <div className="absolute bottom-0 right-0 w-2 h-2 border-b-[2px] border-r-[2px] border-phantom-cyan"></div>

        <div className={`
          text-2xl transition-transform duration-300 font-mono
          ${isActive ? 'text-phantom-cyan drop-shadow-[0_0_8px_#00E5FF]' : 'text-phantom-cyan/50'}
        `}>
          {icon}
        </div>

        <div className="flex flex-col">
          <span className="text-[8px] text-phantom-cyan/60 tracking-[0.4em] font-mono mb-0.5">ACTIVE_STATE</span>
          <span className={`
            text-sm font-mono tracking-[0.3em] uppercase transition-all duration-200
            ${isChanging ? 'blur-[2px] opacity-50 translate-x-2' : 'blur-0 opacity-100 translate-x-0'}
            ${isActive ? 'text-white drop-shadow-[0_0_5px_white]' : 'text-phantom-cyan/70'}
          `}>
            {displayGesture}
          </span>
        </div>

        <div className="flex space-x-1.5 ml-6 border-l border-phantom-cyan/30 pl-4">
          <div className={`w-1.5 h-4 ${isActive ? 'bg-phantom-cyan shadow-[0_0_5px_#00E5FF] animate-pulse' : 'bg-phantom-cyan/20'}`} />
          <div className={`w-1.5 h-4 ${isActive ? 'bg-phantom-cyan shadow-[0_0_5px_#00E5FF] animate-pulse [animation-delay:150ms]' : 'bg-phantom-cyan/20'}`} />
          <div className={`w-1.5 h-4 ${isActive ? 'bg-phantom-cyan shadow-[0_0_5px_#00E5FF] animate-pulse [animation-delay:300ms]' : 'bg-phantom-cyan/20'}`} />
        </div>
      </div>
    </div>
  );
};

export default GestureIndicator;
