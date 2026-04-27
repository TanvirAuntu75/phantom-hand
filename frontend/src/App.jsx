import React from 'react';
import HUDOverlay from './components/HUDOverlay';
import { useSocket } from './hooks/useSocket';
import { useHandData } from './hooks/useHandData';

function App() {
  // Use relative path for production (Docker), localhost for dev
  const socketUrl = import.meta.env.PROD ? '' : 'http://localhost:8000';

  const { socket, isConnected } = useSocket(socketUrl);
  const { videoFrame, handData, fps, systemState, gestureLog, shapeCandidate } = useHandData(socket);

  // Re-map fps into handData structure to avoid prop drilling issues in HUDOverlay if it relies on handData.fps
  const consolidatedHandData = { ...handData, fps: fps };

  return (
    <HUDOverlay
      isConnected={isConnected}
      videoFrame={videoFrame}
      handData={consolidatedHandData}
      systemState={systemState}
      gestureLog={gestureLog}
      shapeCandidate={shapeCandidate}
    />
  );
}

export default App;
