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
      <div className="relative w-full h-full overflow-hidden">
        
        {/* ── BASE_VIDEO_FEED ───────────────────────────────────────────── */}
        <canvas
          ref={canvasRef}
          width={1280}
          height={720}
          className="w-full h-full object-cover filter brightness-100 contrast-125 saturate-50 sepia-[.2] hue-rotate-[180deg]"
        />

        {/* ── TACTICAL_OVERLAYS ─────────────────────────────────────────── */}
        <div className="absolute inset-0 pointer-events-none">
          
          <HandSkeleton
            hands={handData?.hands}
            width={1280}
            height={720}
          />

          {primaryHand && !primaryHand.is_ghost && (
            <div 
              className="absolute transition-all duration-75 ease-out"
              style={{ 
                left: `${(crosshairX / 1280) * 100}%`, 
                top: `${(crosshairY / 720) * 100}%`,
                transform: 'translate(-50%, -50%)'
              }}
            >
              <div className="relative w-16 h-16">
                <div className="absolute top-0 left-0 w-4 h-4 border-l-[3px] border-t-[3px] border-phantom-cyan" />
                <div className="absolute top-0 right-0 w-4 h-4 border-r-[3px] border-t-[3px] border-phantom-cyan" />
                <div className="absolute bottom-0 left-0 w-4 h-4 border-l-[3px] border-b-[3px] border-phantom-cyan" />
                <div className="absolute bottom-0 right-0 w-4 h-4 border-r-[3px] border-b-[3px] border-phantom-cyan" />
                
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-phantom-cyan shadow-[0_0_8px_#00E5FF] animate-ping" />
                
                <div className="absolute -top-6 -right-16 bg-phantom-cyan/20 border border-phantom-cyan px-1.5 py-0.5 text-[8px] text-phantom-cyan font-mono tracking-widest whitespace-nowrap backdrop-blur-sm">
                  TGT_LCK: {String(primaryHand.id || "NULL").slice(-4).toUpperCase()}
                </div>
              </div>
            </div>
          )}

          <ShapeGhost
            shapeCandidate={shapeCandidate}
            width={1280}
            height={720}
          />

          <GestureIndicator gesture={currentGesture} />
        </div>

        {/* ── SIGNAL_LOSS_OVERLAY ────────────────────────────────────────── */}
        {!videoFrame && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 backdrop-blur-md">
            <div className="relative w-48 h-48 mb-8 border border-phantom-cyan rounded-full flex items-center justify-center">
                <div className="absolute inset-2 border border-phantom-cyan border-dashed rounded-full animate-[spin_10s_linear_infinite]" />
                <div className="absolute inset-6 border border-phantom-cyan border-dotted rounded-full animate-[spin_5s_linear_infinite_reverse]" />
                <div className="text-phantom-cyan text-sm tracking-[0.4em] font-mono animate-pulse">
                   OFFLINE
                </div>
            </div>
            <div className="text-[10px] text-phantom-cyan/60 mb-4 tracking-[0.3em] font-mono uppercase">WAITING_FOR_UPLINK...</div>
            <div className="w-64 h-[2px] bg-phantom-accent relative overflow-hidden">
                <div className="absolute top-0 left-0 h-full bg-phantom-cyan animate-[scanlineMove_1.5s_infinite] w-full shadow-[0_0_10px_#00E5FF]" />
            </div>
          </div>
        )}

        {/* Tactical Screen FX */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-transparent to-black/60 pointer-events-none" />
      </div>
    </div>
  );
};

export default DrawingCanvas;
