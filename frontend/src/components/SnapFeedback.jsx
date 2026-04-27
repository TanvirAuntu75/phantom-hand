import React, { useEffect, useState } from 'react';

const SnapFeedback = ({ snappedShape }) => {
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState(null);

  useEffect(() => {
    if (snappedShape) {
      setData(snappedShape);
      setVisible(true);

      // Hold for 0.8s, then start fading out. The component is unmounted by the hook after 2s anyway.
      const timer = setTimeout(() => {
        setVisible(false);
      }, 800);

      return () => clearTimeout(timer);
    }
  }, [snappedShape]);

  if (!data) return null;

  return (
    <div
      className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 pointer-events-none transition-opacity duration-200 ${visible ? 'opacity-100' : 'opacity-0'}`}
    >
      <div className="text-secondary font-mono text-[18px] font-bold uppercase tracking-[0.2em] drop-shadow-[0_0_8px_rgba(255,215,0,0.8)]">
        SHAPE LOCKED: {data.shape} {Math.round(data.confidence * 100)}%
      </div>
    </div>
  );
};

export default SnapFeedback;
