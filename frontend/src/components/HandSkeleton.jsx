import React from 'react';

/**
 * PHANTOM BIOMETRIC SKELETON
 * Renders a high-fidelity digital wireframe over tracked hands.
 * Designed to look like a real-time AI blueprint.
 */
const CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [17, 18], [18, 19], [19, 20],
  [0, 17]
];

// Normalize landmark: handles both [x,y,z] arrays and {x,y,z} objects
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
        <filter id="glow">
          <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {hands.map((hand) => {
        const { landmarks, id, is_ghost } = hand;
        if (!landmarks || landmarks.length !== 21) return null;

        // Visual properties
        const color = is_ghost ? 'var(--color-phantom-alert)' : 'var(--color-phantom-cyan)';
        const opacity = is_ghost ? 0.3 : 0.8;

        return (
          <g key={id} opacity={opacity} filter="url(#glow)">
            {/* ── BONE_STRUCTURE ─────────────────────────────────────────── */}
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
                  strokeWidth="1"
                  strokeDasharray={is_ghost ? '2,2' : 'none'}
                  className="transition-all duration-300"
                />
              );
            })}

            {/* ── JOINT_NODES ────────────────────────────────────────────── */}
            {landmarks.map((lm, i) => {
              const p = getLM(lm);
              return (
                <circle
                  key={`joint-${id}-${i}`}
                  cx={p.x * width}
                  cy={p.y * height}
                  r={i % 4 === 0 ? '2.5' : '1.5'}
                  fill={i === 8 ? 'white' : color}
                  className={i === 8 ? 'animate-pulse' : ''}
                />
              );
            })}

            {/* ── INDEX_TARGETING_RING ───────────────────────────────────── */}
            {landmarks[8] && (() => {
              const tip = getLM(landmarks[8]);
              return (
                <g transform={`translate(${tip.x * width}, ${tip.y * height})`}>
                  <circle r="12" fill="none" stroke={color} strokeWidth="0.5" strokeDasharray="4,2" />
                  <circle r="8" fill="none" stroke={color} strokeWidth="1.5" className="animate-pulse" />
                </g>
              );
            })()}
          </g>
        );
      })}
    </svg>
  );
};

export default HandSkeleton;
