import React, { useEffect, useRef } from 'react';
import GestureIndicator from './GestureIndicator';
import HandSkeleton from './HandSkeleton';
import ShapeGhost from './ShapeGhost';

const DrawingCanvas = ({ videoFrame, handData, shapeCandidate }) => {
  const canvasRef = useRef(null);

  // The backend already composites the drawing onto the camera frame and sends it.
  // So the base64 'videoFrame' string IS the full composite.
  // We just need to draw it efficiently to a canvas to maintain exactly 1280x720 scaling.

  useEffect(() => {
    if (!videoFrame || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    const img = new Image();
    img.onload = () => {
      // Use requestAnimationFrame to sync drawing with display refresh
      requestAnimationFrame(() => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      });
    };
    img.src = videoFrame;
  }, [videoFrame]);

  // Determine current gesture from hands (prioritize first hand for indicator)
  const currentGesture = handData?.hands?.[0]?.gesture || 'HOVER';

  return (
    <div className="absolute inset-0 z-0 flex items-center justify-center p-8 pointer-events-none">
      <div className="relative w-full max-w-[1280px] aspect-video border border-primary hud-bracket shadow-[0_0_15px_rgba(0,229,255,0.1)] overflow-hidden">

        {/* The 1280x720 composite video feed from the backend */}
        <canvas
          ref={canvasRef}
          width={1280}
          height={720}
          className="w-full h-full object-cover"
        />

        {/*
          If we needed a truly separate overlay canvas for frontend drawing,
          it would go here. But backend handles compositing.
        */}

        {/* Overlays */}
        <GestureIndicator gesture={currentGesture} />

        <HandSkeleton
          hands={handData?.hands}
          width={1280}
          height={720}
        />

        <ShapeGhost
          shapeCandidate={shapeCandidate}
          width={1280}
          height={720}
        />

        {!videoFrame && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#03060a]">
            <div className="text-dim text-sm tracking-[0.2em] mb-2">AWAITING VIDEO SIGNAL</div>
            <div className="w-48 h-1 bg-inactive relative overflow-hidden">
                <div className="absolute top-0 left-0 h-full bg-primary animate-[pulse_1.5s_ease-in-out_infinite] w-full" style={{transformOrigin: 'left', transform: 'scaleX(0.5)'}}></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DrawingCanvas;
