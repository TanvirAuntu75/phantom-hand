import React from 'react';
import DrawingCanvas from './DrawingCanvas';
import SystemPanel from './SystemPanel';
import GestureLog from './GestureLog';
import HandStatePanel from './HandStatePanel';
import BrushModeBar from './BrushModeBar';
import ColorOrb from './ColorOrb';
import SnapFeedback from './SnapFeedback';
import Scene3D from '../three/Scene3D';

const HUDOverlay = ({ isConnected, videoFrame, handData, systemState, gestureLog, shapeCandidate, snappedShape, strokes3d }) => {
  return (
    <div className="w-screen h-screen overflow-hidden relative selection:bg-primary selection:text-bg">
      <DrawingCanvas
        videoFrame={videoFrame}
        handData={handData}
        shapeCandidate={shapeCandidate}
      />
      <SnapFeedback snappedShape={snappedShape} />
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

      <ColorOrb
        color={systemState.color}
        index={systemState.colorIndex}
        total={systemState.totalColors}
      />
    </div>
  );
};

export default HUDOverlay;
