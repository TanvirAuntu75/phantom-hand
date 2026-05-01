import React, { useState, useEffect } from 'react';
import DrawingCanvas from './DrawingCanvas';
import SystemPanel from './SystemPanel';
import GestureLog from './GestureLog';
import HandStatePanel from './HandStatePanel';
import BrushModeBar from './BrushModeBar';
import ColorOrb from './ColorOrb';
import SnapFeedback from './SnapFeedback';
import Scene3D from '../three/Scene3D';
import ExportMenu from './ExportMenu';
import VoiceWave from './VoiceWave';

const HUDOverlay = ({ 
  isConnected, 
  socket, 
  videoFrame, 
  hands, 
  telemetry,
  systemState, 
  gestureLog, 
  shapeCandidate, 
  snappedShape, 
  strokes3d 
}) => {
  const [exportVisible, setExportVisible] = useState(false);
  const [isBooting, setIsBooting] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsBooting(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key.toLowerCase() === 'e') setExportVisible(true);
    };
    window.addEventListener('keydown', handleKeyDown);
    
    if (hands?.some(h => h.gesture === 'FOUR_CLOSE') && !systemState.mode_3d) {
      setExportVisible(true);
    }

    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [hands, systemState.mode_3d]);

  return (
    <div className="w-screen h-screen overflow-hidden relative bg-studio-bg text-gray-100 select-none font-sans">

      {/* Boot Screen */}
      {isBooting && (
        <div className="absolute inset-0 z-50 bg-studio-bg flex flex-col items-center justify-center transition-opacity duration-1000">
          <div className="w-16 h-16 rounded-full border-4 border-studio-border border-t-studio-accent animate-spin mb-8"></div>
          <div className="text-2xl font-light text-white tracking-widest">PHANTOM STUDIO</div>
        </div>
      )}

      {/* Main Canvas Area */}
      <div className="absolute inset-0 z-0">
        <DrawingCanvas
          videoFrame={videoFrame}
          handData={{ hands }}
          shapeCandidate={shapeCandidate}
        />
        {systemState.mode_3d && (
          <Scene3D strokes={strokes3d} hands={hands || []} />
        )}
        <div className="canvas-vignette" />
      </div>

      {/* Floating UI Layer */}
      <div className="absolute inset-0 z-40 pointer-events-none p-8 flex flex-col justify-between">

        {/* Top Header Row */}
        <div className="flex justify-between items-start w-full">
            <SystemPanel
              isConnected={isConnected}
              telemetry={telemetry}
            />

            <div className="flex space-x-4">
              <VoiceWave isActive={systemState.voice_active} socket={socket} />
              <HandStatePanel hands={hands || []} />
            </div>
        </div>

        {/* Floating Side Toasts */}
        <div className="absolute left-8 bottom-32 w-72">
           <GestureLog log={gestureLog} />
        </div>

        {/* Centered Bottom Dock */}
        <div className="w-full flex justify-center pb-4">
          <div className="studio-pill px-8 py-3 flex items-center space-x-12 pointer-events-auto animate-fade-in-up">
            <BrushModeBar activeMode={systemState.brushMode} mode3d={systemState.mode_3d} />
            <div className="w-px h-10 bg-studio-border" />
            <ColorOrb
              color={systemState.color}
              index={systemState.colorIndex}
              total={systemState.totalColors}
            />
            <div className="w-px h-10 bg-studio-border" />
            <button
              onClick={() => setExportVisible(true)}
              className="w-10 h-10 rounded-full flex items-center justify-center text-studio-muted hover:text-white hover:bg-white/10 transition-colors"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
            </button>
          </div>
        </div>

      </div>

      {/* Overlays */}
      <SnapFeedback snappedShape={snappedShape} />
      <ExportMenu visible={exportVisible} onClose={() => setExportVisible(false)} />
    </div>
  );
};

export default HUDOverlay;
