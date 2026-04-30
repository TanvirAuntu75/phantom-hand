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
        <filter id="skel-glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        <filter id="ghost-glow-skel">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {hands.map((hand) => {
        const { landmarks, id, is_ghost } = hand;
        if (!landmarks || landmarks.length !== 21) return null;

        const color = is_ghost ? '#FF3D00' : '#00E5FF';
        const opacity = is_ghost ? 0.4 : 0.9;
        const filterStr = is_ghost ? "url(#ghost-glow-skel)" : "url(#skel-glow)";

        return (
          <g key={id} opacity={opacity} filter={filterStr}>
            {/* Bone Structure */}
            {CONNECTIONS.map(([startIdx, endIdx], i) => {
              const start = getLM(landmarks[startIdx]);
              const end = getLM(landmarks[endIdx]);
              return (
                <line
                  key={`bone-${id}-${i}`}
                  x1={start.x * width}
                  y1={start.y * height}
                  x2={end.x * width}
                  y2={end.y * height}
                  stroke={color}
                  strokeWidth="1.5"
                  strokeDasharray={is_ghost ? '4,4' : 'none'}
                  className="transition-all duration-300"
                />
              );
            })}

            {/* Joint Nodes */}
            {landmarks.map((lm, i) => {
              const p = getLM(lm);
              const isTip = i % 4 === 0 && i !== 0;
              return (
                <rect
                  key={`joint-${id}-${i}`}
                  x={(p.x * width) - (isTip ? 3 : 2)}
                  y={(p.y * height) - (isTip ? 3 : 2)}
                  width={isTip ? 6 : 4}
                  height={isTip ? 6 : 4}
                  fill={i === 8 ? 'white' : 'transparent'}
                  stroke={color}
                  strokeWidth="1"
                  className={i === 8 ? 'animate-pulse' : ''}
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
