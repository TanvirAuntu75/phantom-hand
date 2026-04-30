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
    const timer = setTimeout(() => setIsBooting(false), 2000);
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
    <div className="w-screen h-screen overflow-hidden relative bg-phantom-bg text-phantom-cyan select-none flex items-center justify-center">
      <div className="phantom-grid" />
      <div className="phantom-vignette" />
      <div className="phantom-scanline" />

      {isBooting && (
        <div className="absolute inset-0 z-50 bg-phantom-bg flex flex-col items-center justify-center space-y-4">
          <div className="text-4xl glow-text animate-pulse font-mono tracking-widest text-phantom-cyan">JARVIS_SYSTEM</div>
          <div className="text-xs font-mono text-phantom-cyan opacity-80">INITIALIZING_PROTOCOL...</div>
          <div className="w-64 h-[1px] bg-phantom-accent relative overflow-hidden mt-4">
             <div className="absolute inset-0 bg-phantom-cyan animate-[scanlineMove_1.5s_infinite]" />
          </div>
        </div>
      )}

      {/* Center Main Display Area */}
      <div className="relative w-[90%] h-[85%] border border-phantom-cyan bg-black/40 backdrop-blur-sm z-10 flex flex-col">
          {/* Main Headers */}
          <div className="flex justify-between p-4 border-b border-phantom-cyan/30">
            <div className="flex flex-col">
              <span className="font-mono text-sm tracking-[0.2em] text-phantom-cyan">MAIN_VIEWPORT</span>
              <span className="font-mono text-[10px] text-phantom-cyan/50 tracking-widest">ACTIVE_SESSION: 0x4B3A</span>
            </div>
             <div className="flex items-center space-x-4">
               <span className={`text-[10px] font-mono tracking-[0.2em] ${isConnected ? 'text-phantom-cyan animate-pulse' : 'text-phantom-alert'}`}>
                  {isConnected ? 'SYS.ONLINE' : 'SYS.OFFLINE'}
               </span>
             </div>
          </div>

          <div className="relative flex-grow overflow-hidden">
            <DrawingCanvas
              videoFrame={videoFrame}
              handData={{ hands }}
              shapeCandidate={shapeCandidate}
            />
            {systemState.mode_3d && (
              <Scene3D strokes={strokes3d} hands={hands || []} />
            )}
          </div>
      </div>

      {/* Floating UI Elements */}
      <div className="absolute top-6 left-6 z-40">
        <SystemPanel 
          isConnected={isConnected} 
          telemetry={telemetry} 
          systemState={systemState} 
        />
      </div>

      <div className="absolute bottom-6 left-6 z-40 w-64 space-y-4">
        <GestureLog log={gestureLog} />
        <VoiceWave isActive={systemState.voice_active} socket={socket} />
      </div>

      <div className="absolute top-6 right-6 z-40 w-72">
        <HandStatePanel hands={hands || []} />
      </div>

      {/* Footer Controls */}
      <footer className="absolute bottom-6 left-1/2 -translate-x-1/2 z-40 flex items-center space-x-10 px-8 py-3 bg-black/50 border border-phantom-cyan backdrop-blur-md">
        <BrushModeBar activeMode={systemState.brushMode} mode3d={systemState.mode_3d} />
        <div className="h-10 w-px bg-phantom-cyan/30" />
        <ColorOrb
          color={systemState.color}
          index={systemState.colorIndex}
          total={systemState.totalColors}
        />
      </footer>

      {/* Extras */}
      <SnapFeedback snappedShape={snappedShape} />
      <ExportMenu visible={exportVisible} onClose={() => setExportVisible(false)} />
    </div>
  );
};

export default HUDOverlay;
