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
        <filter id="ghost-blur" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="8" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* Soft Fill */}
      <polygon
        points={points}
        fill="rgba(255, 255, 255, 0.05)"
        stroke="rgba(255, 255, 255, 0.6)"
        strokeWidth="2"
        strokeLinejoin="round"
        filter="url(#ghost-blur)"
        className="animate-pulse-slow"
      />
    </svg>
  );
};

export default ShapeGhost;
