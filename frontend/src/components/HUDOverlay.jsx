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

/**
 * PHANTOM HUD ORCHESTRATOR
 * The main high-fidelity interface for the Phantom Hand system.
 * Implements a tactical, multi-panel HUD with real-time telemetry.
 */
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

  // Initialize Boot Sequence
  useEffect(() => {
    const timer = setTimeout(() => setIsBooting(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  // Keyboard & Gesture Listeners for Export Trigger
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key.toLowerCase() === 'e') setExportVisible(true);
    };
    window.addEventListener('keydown', handleKeyDown);
    
    // Auto-open export on specific gesture (if not in 3D mode)
    if (hands?.some(h => h.gesture === 'FOUR_CLOSE') && !systemState.mode_3d) {
      setExportVisible(true);
    }

    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [hands, systemState.mode_3d]);

  return (
    <div className="w-screen h-screen overflow-hidden relative bg-phantom-bg text-phantom-cyan select-none">
      {/* ── BACKGROUND_FX ─────────────────────────────────────────────────── */}
      <div className="phantom-grid" />
      <div className="phantom-vignette" />
      <div className="phantom-scanline" />

      {/* ── CORE_VIEWPORT ─────────────────────────────────────────────────── */}
      <div className="absolute inset-0 z-0">
        <DrawingCanvas
          videoFrame={videoFrame}
          handData={{ hands }} // Compatibility wrap for DrawingCanvas if needed
          shapeCandidate={shapeCandidate}
        />
        {systemState.mode_3d && (
          <Scene3D strokes={strokes3d} hands={hands || []} />
        )}
      </div>

      {/* ── BOOT_OVERLAY ──────────────────────────────────────────────────── */}
      {isBooting && (
        <div className="absolute inset-0 z-50 bg-phantom-bg flex flex-col items-center justify-center space-y-4">
          <div className="text-4xl glow-text animate-pulse">PHANTOM_HAND_OS</div>
          <div className="text-xs phantom-data">INITIALIZING_VISION_KERNEL...</div>
          <div className="w-48 h-1 bg-phantom-accent relative overflow-hidden">
             <div className="absolute inset-0 bg-phantom-cyan animate-[scanlineMove_1s_infinite]" />
          </div>
        </div>
      )}

      {/* ── TOP_TELEMETRY_BAR ─────────────────────────────────────────────── */}
      <header className="absolute top-0 left-0 w-full p-4 z-40 flex justify-between items-start pointer-events-none">
        <SystemPanel 
          isConnected={isConnected} 
          telemetry={telemetry} 
          systemState={systemState} 
        />
        <div className="phantom-panel phantom-bracket p-3 flex flex-col items-end">
          <div className="text-[10px] text-phantom-accent">AUTH_TOKEN</div>
          <div className="text-sm">PH-75801-XNT</div>
        </div>
      </header>

      {/* ── SIDE_COMMAND_PANELS ───────────────────────────────────────────── */}
      <aside className="absolute left-6 top-32 bottom-32 w-64 z-30 flex flex-col space-y-6 pointer-events-none">
        <div className="pointer-events-auto h-1/2">
          <GestureLog log={gestureLog} />
        </div>
        <div className="pointer-events-auto h-1/2">
          <VoiceWave isActive={systemState.voice_active} socket={socket} />
        </div>
      </aside>

      <aside className="absolute right-6 top-32 bottom-32 w-72 z-30 flex flex-col pointer-events-none">
        <div className="pointer-events-auto">
          <HandStatePanel hands={hands || []} />
        </div>
      </aside>

      {/* ── FOOTER_CONTROLS ───────────────────────────────────────────────── */}
      <footer className="absolute bottom-6 left-1/2 -translate-x-1/2 z-40 flex items-center space-x-8 px-8 py-4 phantom-panel phantom-bracket">
        <BrushModeBar activeMode={systemState.brushMode} mode3d={systemState.mode_3d} />
        <div className="h-8 w-px bg-phantom-accent" />
        <ColorOrb
          color={systemState.color}
          index={systemState.colorIndex}
          total={systemState.totalColors}
        />
      </footer >

      {/* ── FEEDBACK_OVERLAYS ─────────────────────────────────────────────── */}
      <SnapFeedback snappedShape={snappedShape} />
      <ExportMenu visible={exportVisible} onClose={() => setExportVisible(false)} />
    </div>
  );
};

export default HUDOverlay;
