import React from 'react';

const ShapeGhost = ({ shapeCandidate, width, height }) => {
  if (!shapeCandidate || !shapeCandidate.fitted_points) return null;

  const points = shapeCandidate.fitted_points.map(pt => {
    const isNormalized = pt[0] <= 1.5 && pt[1] <= 1.5;
    const x = isNormalized ? pt[0] * width : pt[0];
    const y = isNormalized ? pt[1] * height : pt[1];
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg
      className="absolute inset-0 pointer-events-none z-20"
      width="100%"
      height="100%"
      viewBox={`0 0 ${width} ${height}`}
    >
      <defs>
        <filter id="ghost-glow">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <polygon
        points={points}
        fill="rgba(0, 229, 255, 0.15)"
        stroke="#00E5FF"
        strokeWidth="2"
        strokeDasharray="6 4"
        filter="url(#ghost-glow)"
        className="animate-[pulse_1.5s_ease-in-out_infinite]"
      />
    </svg>
  );
};

export default ShapeGhost;
