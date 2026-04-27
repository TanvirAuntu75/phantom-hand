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

const HUDOverlay = ({ isConnected, socket, videoFrame, handData, systemState, gestureLog, shapeCandidate, snappedShape, strokes3d }) => {
  const [exportVisible, setExportVisible] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key.toLowerCase() === 'e') {
        setExportVisible(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    // Check for FOUR_CLOSE gesture
    if (handData && handData.hands) {
      const isFourClose = handData.hands.some(h => h.gesture === 'FOUR_CLOSE');
      // Only open export menu if we are NOT in 3D mode. In 3D mode, FOUR_CLOSE is handled by Scene3D.
      if (isFourClose && !systemState.mode_3d) {
        setExportVisible(true);
      }
    }
  }, [handData, systemState.mode_3d]);

  useEffect(() => {
    if (!socket) return;
    const handleTrigger = (data) => {
        setExportVisible(true);
    };
    socket.on('trigger_export', handleTrigger);
    return () => socket.off('trigger_export', handleTrigger);
  }, [socket]);

  return (
    <div className="w-screen h-screen overflow-hidden relative selection:bg-primary selection:text-bg">
      <DrawingCanvas
        videoFrame={videoFrame}
        handData={handData}
        shapeCandidate={shapeCandidate}
      />
      <SnapFeedback snappedShape={snappedShape} />
      <ExportMenu visible={exportVisible} onClose={() => setExportVisible(false)} />
      {systemState.mode_3d && (
        <Scene3D strokes={strokes3d} hands={handData.hands} />
      )}

      <SystemPanel
        isConnected={isConnected}
        fps={handData.fps}
        systemState={systemState}
      />

      <GestureLog log={gestureLog} />

      <HandStatePanel hands={handData.hands || []} />

      <BrushModeBar activeMode={systemState.brushMode} mode3d={systemState.mode_3d} />
      <VoiceWave isActive={systemState.voice_active} socket={socket} />

      <ColorOrb
        color={systemState.color}
        index={systemState.colorIndex}
        total={systemState.totalColors}
      />
    </div>
  );
};

export default HUDOverlay;
