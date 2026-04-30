import React, { useEffect, useRef } from 'react';
import GestureIndicator from './GestureIndicator';
import HandSkeleton from './HandSkeleton';
import ShapeGhost from './ShapeGhost';

// Normalize landmark: handles both [x,y,z] arrays and {x,y,z} objects
const getLM = (lm) => Array.isArray(lm) ? { x: lm[0], y: lm[1], z: lm[2] || 0 } : (lm || { x: 0, y: 0, z: 0 });

/**
 * PHANTOM VISION VIEWPORT
 * The primary interactive canvas that renders the camera feed,
 * drawing strokes, and tactical HUD overlays (crosshairs, skeleton).
 */
const DrawingCanvas = ({ videoFrame, handData, shapeCandidate }) => {
  const canvasRef = useRef(null);

  // High-performance canvas rendering for the 1280x720 video feed
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

  // Extract primary tracking target (first hand)
  const primaryHand = handData?.hands?.[0];
  const currentGesture = primaryHand?.gesture || 'HOVER';
  
  // Calculate relative coordinates for the crosshair
  const rawIndexTip = primaryHand?.landmarks?.[8];
  const indexTip = rawIndexTip ? getLM(rawIndexTip) : null;
  const crosshairX = indexTip ? indexTip.x * 1280 : 0;
  const crosshairY = indexTip ? indexTip.y * 720 : 0;

  return (
    <div className="absolute inset-0 z-0 flex items-center justify-center p-8 pointer-events-none">
      <div className="relative w-full max-w-[1280px] aspect-video phantom-bracket border border-phantom-accent shadow-[0_0_40px_rgba(0,0,0,0.8)] overflow-hidden">
        
        {/* ── BASE_VIDEO_FEED ───────────────────────────────────────────── */}
        <canvas
          ref={canvasRef}
          width={1280}
          height={720}
          className="w-full h-full object-cover filter brightness-90 contrast-110"
        />

        {/* ── TACTICAL_OVERLAYS ─────────────────────────────────────────── */}
        <div className="absolute inset-0 pointer-events-none">
          
          {/* Hand Skeleton (Digital Blueprint) */}
          <HandSkeleton
            hands={handData?.hands}
            width={1280}
            height={720}
          />

          {/* Dynamic Crosshair (Target Lock) */}
          {primaryHand && !primaryHand.is_ghost && (
            <div 
              className="absolute transition-all duration-75 ease-out"
              style={{ 
                left: `${(crosshairX / 1280) * 100}%`, 
                top: `${(crosshairY / 720) * 100}%`,
                transform: 'translate(-50%, -50%)'
              }}
            >
              <div className="relative w-12 h-12">
                {/* Crosshair Brackets */}
                <div className="absolute top-0 left-0 w-3 h-3 border-l-2 border-t-2 border-phantom-cyan" />
                <div className="absolute top-0 right-0 w-3 h-3 border-r-2 border-t-2 border-phantom-cyan" />
                <div className="absolute bottom-0 left-0 w-3 h-3 border-l-2 border-bottom-2 border-phantom-cyan" />
                <div className="absolute bottom-0 right-0 w-3 h-3 border-r-2 border-bottom-2 border-phantom-cyan" />
                
                {/* Central Dot */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1 h-1 bg-phantom-cyan rounded-full animate-pulse" />
                
                {/* Floating ID Tag */}
                <div className="absolute -top-6 -right-12 bg-phantom-cyan bg-opacity-20 border border-phantom-cyan px-1 py-0.5 text-[8px] text-phantom-cyan font-bold whitespace-nowrap">
                  LOCK_ID: {String(primaryHand.id || "NULL").slice(-4).toUpperCase()}
                </div>
              </div>
            </div>
          )}

          {/* Shape Preview (Ghost Mode) */}
          <ShapeGhost
            shapeCandidate={shapeCandidate}
            width={1280}
            height={720}
          />

          {/* Gesture Floating Indicator */}
          <GestureIndicator gesture={currentGesture} />
        </div>

        {/* ── SIGNAL_LOSS_OVERLAY ────────────────────────────────────────── */}
        {!videoFrame && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-phantom-bg">
            <div className="text-phantom-cyan text-sm tracking-[0.4em] mb-4 glow-text animate-pulse">
               AWAITING_VISION_FEED
            </div>
            <div className="text-[10px] text-phantom-accent mb-4 tracking-[0.2em]">INITIALIZING_SECURE_LINK...</div>
            <div className="w-64 h-0.5 bg-phantom-accent relative overflow-hidden">
                <div className="absolute top-0 left-0 h-full bg-phantom-cyan animate-[scanlineMove_2s_infinite] w-full" />
            </div>
          </div>
        )}

        {/* CRT/Scanline Over-Canvas Mask */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-phantom-cyan to-transparent opacity-[0.03] pointer-events-none" />
      </div>
    </div>
  );
};

export default DrawingCanvas;
