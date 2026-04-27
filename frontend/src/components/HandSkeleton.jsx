import React from 'react';

// MediaPipe hand connections (pairs of landmark indices)
const CONNECTIONS = [
  // Thumb
  [0, 1], [1, 2], [2, 3], [3, 4],
  // Index
  [0, 5], [5, 6], [6, 7], [7, 8],
  // Middle
  [5, 9], [9, 10], [10, 11], [11, 12],
  // Ring
  [9, 13], [13, 14], [14, 15], [15, 16],
  // Pinky
  [13, 17], [17, 18], [18, 19], [19, 20],
  [0, 17] // Palm base
];

const HandSkeleton = ({ hands, width, height }) => {
  if (!hands || hands.length === 0) return null;

  return (
    <svg
      className="absolute inset-0 pointer-events-none z-30"
      width="100%"
      height="100%"
      viewBox={`0 0 ${width} ${height}`}
    >
      {hands.map((hand) => {
        if (!hand.landmarks || hand.landmarks.length !== 21) return null;

        const isLeft = hand.id.includes('Left') || hand.id.includes('Left') ? true : false;
        // Default cyan for first hand, magenta for second if not explicitly labeled
        const isCyan = hand.id.includes('Right') || !isLeft;

        const color = isCyan ? '#00E5FF' : '#FF00C8';
        const opacity = hand.is_ghost ? 0.3 : 1.0;

        return (
          <g key={hand.id} opacity={opacity}>
            {/* Draw Bones (Lines) */}
            {CONNECTIONS.map(([startIdx, endIdx], i) => {
              const start = hand.landmarks[startIdx];
              const end = hand.landmarks[endIdx];
              return (
                <line
                  key={`bone-${i}`}
                  x1={start[0] * width}
                  y1={start[1] * height}
                  x2={end[0] * width}
                  y2={end[1] * height}
                  stroke={color}
                  strokeWidth="1"
                  strokeOpacity="0.4"
                />
              );
            })}

            {/* Draw Fingertip Dots (Indices 4, 8, 12, 16, 20) */}
            {[4, 8, 12, 16, 20].map((idx) => {
              const lm = hand.landmarks[idx];
              return (
                <circle
                  key={`tip-${idx}`}
                  cx={lm[0] * width}
                  cy={lm[1] * height}
                  r="6"
                  fill={color}
                />
              );
            })}

            {/* Index Fingertip Ring (Index 8) */}
            {hand.landmarks[8] && (
              <circle
                cx={hand.landmarks[8][0] * width}
                cy={hand.landmarks[8][1] * height}
                r="14"
                fill="none"
                stroke={color}
                strokeWidth="2"
                opacity="1.0"
              />
            )}
          </g>
        );
      })}
    </svg>
  );
};

export default HandSkeleton;
