import React from 'react';

const CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [17, 18], [18, 19], [19, 20],
  [0, 17]
];

const getLM = (lm) => Array.isArray(lm) ? { x: lm[0], y: lm[1], z: lm[2] || 0 } : (lm || { x: 0, y: 0, z: 0 });

const HandSkeleton = ({ hands, width, height }) => {
  if (!hands || hands.length === 0) return null;

  return (
    <svg
      className="absolute inset-0 pointer-events-none z-30"
      width="100%"
      height="100%"
      viewBox={`0 0 ${width} ${height}`}
    >
      <defs>
        <filter id="soft-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="6" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {hands.map((hand) => {
        const { landmarks, id, is_ghost } = hand;
        if (!landmarks || landmarks.length !== 21) return null;

        const baseColor = is_ghost ? '#FF715B' : '#4ADE80';
        const opacity = is_ghost ? 0.3 : 0.6;

        return (
          <g key={id} opacity={opacity} filter="url(#soft-glow)">
            {/* Draw bones as organic, rounded paths */}
            <path
              d={CONNECTIONS.map(([startIdx, endIdx]) => {
                const start = getLM(landmarks[startIdx]);
                const end = getLM(landmarks[endIdx]);
                return `M ${start.x * width} ${start.y * height} L ${end.x * width} ${end.y * height}`;
              }).join(' ')}
              stroke={baseColor}
              strokeWidth={is_ghost ? "2" : "3"}
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
              className="transition-all duration-100 ease-out"
            />

            {/* Joints as soft dots */}
            {landmarks.map((lm, i) => {
              const p = getLM(lm);
              const isTip = i % 4 === 0 && i !== 0;
              return (
                <circle
                  key={`joint-${id}-${i}`}
                  cx={p.x * width}
                  cy={p.y * height}
                  r={isTip ? "4" : "2.5"}
                  fill={i === 8 ? '#FFFFFF' : baseColor}
                  className={i === 8 ? 'animate-pulse-slow' : ''}
                />
              );
            })}
          </g>
        );
      })}
    </svg>
  );
};

export default HandSkeleton;
