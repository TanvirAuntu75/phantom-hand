import React, { useEffect, useRef } from 'react';
import GestureIndicator from './GestureIndicator';
import HandSkeleton from './HandSkeleton';
import ShapeGhost from './ShapeGhost';

const getLM = (lm) => Array.isArray(lm) ? { x: lm[0], y: lm[1], z: lm[2] || 0 } : (lm || { x: 0, y: 0, z: 0 });

const DrawingCanvas = ({ videoFrame, handData, shapeCandidate }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!videoFrame || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      requestAnimationFrame(() => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      });
    };
    img.src = videoFrame;
  }, [videoFrame]);

  const primaryHand = handData?.hands?.[0];
  const currentGesture = primaryHand?.gesture || 'HOVER';
  
  const rawIndexTip = primaryHand?.landmarks?.[8];
  const indexTip = rawIndexTip ? getLM(rawIndexTip) : null;
  const crosshairX = indexTip ? indexTip.x * 1280 : 0;
  const crosshairY = indexTip ? indexTip.y * 720 : 0;

  return (
    <div className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none">
      <div className="relative w-full h-full overflow-hidden bg-[#0F1115]">
        
        {/* Base Feed - Softly styled to look like a canvas, not a security camera */}
        <canvas
          ref={canvasRef}
          width={1280}
          height={720}
          className="w-full h-full object-cover filter contrast-[1.05] saturate-[0.8] brightness-[0.9]"
        />

        <div className="absolute inset-0 pointer-events-none">
          
          <HandSkeleton
            hands={handData?.hands}
            width={1280}
            height={720}
          />

          {/* Minimal Cursor */}
          {primaryHand && !primaryHand.is_ghost && (
            <div 
              className="absolute transition-all duration-75 ease-out"
              style={{ 
                left: `${(crosshairX / 1280) * 100}%`, 
                top: `${(crosshairY / 720) * 100}%`,
                transform: 'translate(-50%, -50%)'
              }}
            >
              <div className="relative w-8 h-8 flex items-center justify-center">
                <div className="w-1.5 h-1.5 bg-white rounded-full shadow-[0_0_10px_white]" />
                <div className="absolute inset-0 border border-white/30 rounded-full animate-ping opacity-50" />
              </div>
            </div>
          )}

          <ShapeGhost
            shapeCandidate={shapeCandidate}
            width={1280}
            height={720}
          />

          {/* Invisible unless actively gesturing */}
          <GestureIndicator gesture={currentGesture} />
        </div>

        {/* Offline State */}
        {!videoFrame && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-studio-bg backdrop-blur-xl">
            <div className="w-20 h-20 rounded-full bg-studio-glass flex items-center justify-center mb-6 shadow-glass">
                <svg className="w-8 h-8 text-studio-muted animate-pulse-slow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
            </div>
            <div className="text-xl font-medium text-white mb-2">Camera Offline</div>
            <div className="text-sm text-studio-muted">Waiting for vision system connection...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DrawingCanvas;
