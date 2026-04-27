import React from 'react';
import HUDOverlay from './components/HUDOverlay';
import { useSocket } from './hooks/useSocket';
import { useHandData } from './hooks/useHandData';

function App() {
  // Use relative path for production (Docker), localhost for dev
  const socketUrl = import.meta.env.PROD ? '' : 'http://localhost:8000';

  const { socket, isConnected } = useSocket(socketUrl);
  const { videoFrame, handData, systemState, gestureLog } = useHandData(socket);

  return (
    <HUDOverlay
      isConnected={isConnected}
      videoFrame={videoFrame}
      handData={handData}
      systemState={systemState}
      gestureLog={gestureLog}
    />
  );
}

export default App;
