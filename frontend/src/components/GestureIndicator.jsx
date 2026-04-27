import React, { useEffect, useState } from 'react';

const ICON_MAP = {
  DRAW: '✦',
  ERASE: '◈',
  UNDO: '↩',
  REDO: '↪',
  CLEAR: '⊗',
  SHAPE: '◇',
  SNAP_SHAPE: '◇',
  COLOR: '◉',
  SWIPE_RIGHT: '◉',
  SWIPE_LEFT: '◉',
  SIZE: '◈',
  SWIPE_UP: '◈',
  SWIPE_DOWN: '◈',
  THREE_UP: '▤',
  HORNS: '▤',
  L_SHAPE: '◧',
  PINKY_ONLY: '◨',
  HOVER: ''
};

const GestureIndicator = ({ gesture }) => {
  const [activeGesture, setActiveGesture] = useState(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!gesture || gesture === 'HOVER') return;

    setActiveGesture(gesture);
    setVisible(true);

    const timer = setTimeout(() => {
      setVisible(false);
    }, 800);

    return () => clearTimeout(timer);
  }, [gesture]);

  if (!visible || !activeGesture) return null;

  const icon = ICON_MAP[activeGesture] || '•';

  return (
    <div className="absolute top-10 left-1/2 -translate-x-1/2 z-50 pointer-events-none transition-opacity duration-300">
      <div className="bg-[#00E5FF1E] border border-primary hud-bracket px-6 py-3 flex items-center gap-3 backdrop-blur-sm">
        <span className="text-primary text-xl">{icon}</span>
        <span className="text-white font-mono text-[13px] tracking-[0.2em]">{activeGesture}</span>
      </div>
    </div>
  );
};

export default GestureIndicator;
