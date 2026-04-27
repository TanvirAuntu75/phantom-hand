import React from 'react';
import VideoFeed from './VideoFeed';
import SystemPanel from './SystemPanel';
import GestureLog from './GestureLog';
import HandStatePanel from './HandStatePanel';
import BrushModeBar from './BrushModeBar';
import ColorOrb from './ColorOrb';

const HUDOverlay = ({ isConnected, videoFrame, handData, systemState, gestureLog }) => {
  return (
    <div className="w-screen h-screen overflow-hidden relative selection:bg-primary selection:text-bg">
      <VideoFeed frameSrc={videoFrame} />

      <SystemPanel
        isConnected={isConnected}
        fps={handData.fps}
        systemState={systemState}
      />

      <GestureLog log={gestureLog} />

      <HandStatePanel hands={handData.hands || []} />

      <BrushModeBar activeMode={systemState.brushMode} />

      <ColorOrb
        color={systemState.color}
        index={systemState.colorIndex}
        total={systemState.totalColors}
      />
    </div>
  );
};

export default HUDOverlay;
