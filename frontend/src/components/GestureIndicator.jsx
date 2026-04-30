import React, { useEffect, useState } from 'react';

/**
 * PHANTOM GESTURE INTERPRETER
 * Provides immediate visual feedback for the currently recognized hand pose.
 * Features a high-fidelity "Scramble" animation for state transitions.
 */
const ICON_MAP = {
  DRAW: '●',
  ERASE: '×',
  UNDO: '«',
  REDO: '»',
  CLEAR: '∅',
  SHAPE: '◆',
  COLOR: '◈',
  SIZE: '⚖',
  HOVER: '•'
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

  const icon = ICON_MAP[gesture] || '•';
  const isActive = gesture !== 'HOVER' && gesture !== undefined;

  return (
    <div className="absolute top-12 left-1/2 -translate-x-1/2 z-40 pointer-events-none transition-all duration-300">
      <div className={`
        flex items-center space-x-4 px-6 py-2 transition-all duration-300
        phantom-panel phantom-bracket
        ${isActive ? 'border-phantom-cyan bg-phantom-cyan bg-opacity-10' : 'border-phantom-accent opacity-50'}
      `}>
        {/* ── STATUS_ICON ───────────────────────────────────────────────── */}
        <div className={`
          text-lg transition-transform duration-300 
          ${isActive ? 'text-phantom-cyan scale-110' : 'text-phantom-accent scale-100'}
        `}>
          {icon}
        </div>

        {/* ── GESTURE_NAME ──────────────────────────────────────────────── */}
        <div className="flex flex-col">
          <span className="text-[8px] text-phantom-accent tracking-[0.3em] font-bold">STATE_INTENT</span>
          <span className={`
            text-sm font-bold tracking-[0.2em] transition-all duration-200
            ${isChanging ? 'blur-sm translate-y-1' : 'blur-0 translate-y-0'}
            ${isActive ? 'text-white' : 'text-phantom-accent'}
          `}>
            {displayGesture}
          </span>
        </div>

        {/* ── ACTIVITY_MONITOR ──────────────────────────────────────────── */}
        <div className="flex space-x-1 ml-4">
          <div className={`w-1 h-3 ${isActive ? 'bg-phantom-cyan animate-pulse' : 'bg-phantom-accent'}`} />
          <div className={`w-1 h-3 ${isActive ? 'bg-phantom-cyan animate-pulse [animation-delay:100ms]' : 'bg-phantom-accent'}`} />
          <div className={`w-1 h-3 ${isActive ? 'bg-phantom-cyan animate-pulse [animation-delay:200ms]' : 'bg-phantom-accent'}`} />
        </div>
      </div>
    </div>
  );
};

export default GestureIndicator;
