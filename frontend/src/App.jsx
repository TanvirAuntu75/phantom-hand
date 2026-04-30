import React from 'react';
import HUDOverlay from './components/HUDOverlay';
import { useSocket } from './hooks/useSocket';
import { useHandData } from './hooks/useHandData';

/**
 * PHANTOM APPLICATION KERNEL
 * Entry point for the frontend interface. 
 * Orchestrates socket connection and data distribution to the HUD.
 */
function App() {
  // Connection configuration
  const socketUrl = import.meta.env.PROD ? '' : 'http://localhost:8080';
  const { socket, isConnected } = useSocket(socketUrl);
  
  // Data ingestion hook
  const { 
    videoFrame, 
    hands, 
    telemetry, 
    systemState, 
    gestureLog, 
    shapeCandidate, 
    snappedShape, 
    strokes3d 
  } = useHandData(socket);

  return (
    <HUDOverlay
      isConnected={isConnected}
      socket={socket}
      videoFrame={videoFrame}
      hands={hands}
      telemetry={telemetry}
      systemState={systemState}
      gestureLog={gestureLog}
      shapeCandidate={shapeCandidate}
      snappedShape={snappedShape}
      strokes3d={strokes3d}
    />
  );
}

export default App;
