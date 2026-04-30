import React from 'react';

const ShapeGhost = ({ shapeCandidate, width, height }) => {
  if (!shapeCandidate || !shapeCandidate.fitted_points) return null;

  // Assuming fitted_points is an array of [x, y] coordinates in normalized space (0.0 to 1.0)
  // or absolute pixel space. The backend usually normalizes, but if it's absolute, we scale.
  // We'll map them assuming normalized space. If they are absolute, we'll need logic to handle it.
  // The ShapeRecognizer in core returns normalized or pixel? shape_recognizer resamples and fits based on stroke points.
  // The prompt says "Color: rgba(0, 229, 255, 0.25)" and "Border: 1px dashed cyan".

  const points = shapeCandidate.fitted_points.map(pt => {
    // If pt is < 1.5, assume it's normalized. Otherwise assume absolute pixels.
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
      <polygon
        points={points}
        fill="rgba(0, 229, 255, 0.25)"
        stroke="#00E5FF"
        strokeWidth="1"
        strokeDasharray="4 4"
        className="animate-[pulse_1s_ease-in-out_infinite]"
      />
    </svg>
  );
};

export default ShapeGhost;
