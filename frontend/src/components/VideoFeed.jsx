import React from 'react';

const VideoFeed = ({ frameSrc }) => {
  return (
    <div className="absolute inset-0 z-0 flex items-center justify-center p-8 pointer-events-none">
      <div className="relative w-full max-w-[1280px] aspect-video border border-primary hud-bracket shadow-[0_0_15px_rgba(0,229,255,0.1)]">
        {frameSrc ? (
          <img
            src={frameSrc}
            alt="Camera Feed"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center bg-[#03060a]">
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

export default VideoFeed;
