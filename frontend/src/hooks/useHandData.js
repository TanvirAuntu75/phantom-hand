import { useState, useEffect } from 'react';

export const useHandData = (socket) => {
  const [videoFrame, setVideoFrame] = useState(null);
  const [handData, setHandData] = useState({ fps: 0, hands: [] });
  const [systemState, setSystemState] = useState({
    brushMode: 'PNC',
    activeLayer: 1,
    totalLayers: 5,
    brushSize: 12,
    mirrorH: false,
    mirrorV: false,
    color: '#00E5FF',
    colorIndex: 1,
    totalColors: 7
  });

  const [gestureLog, setGestureLog] = useState([]);

  useEffect(() => {
    if (!socket) return;

    const handleVideoFrame = (data) => {
      setVideoFrame(data.image);
    };

    const handleHandData = (data) => {
      setHandData(data);
      if (data.systemState) {
        setSystemState(data.systemState);
      }

      // Extract gestures for the log (a real backend might emit these specifically)
      if (data.hands && data.hands.length > 0) {
        data.hands.forEach(hand => {
          if (hand.gesture && hand.gesture !== 'HOVER' && hand.gesture !== 'DRAW') {
             // Basic deduplication based on time (prevent flooding)
             setGestureLog(prev => {
                const now = new Date();
                const timeString = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
                const entry = `${timeString} - ${hand.gesture}`;

                // Don't add if it's the exact same as the last entry (simple debounce visualization)
                if (prev.length > 0 && prev[0].split(' - ')[1] === hand.gesture) {
                    return prev;
                }

                const newLog = [entry, ...prev].slice(0, 8); // Keep last 8
                return newLog;
             });
          }
        });
      }
    };

    socket.on('video_frame', handleVideoFrame);
    socket.on('hand_data', handleHandData);

    return () => {
      socket.off('video_frame', handleVideoFrame);
      socket.off('hand_data', handleHandData);
    };
  }, [socket]);

  return { videoFrame, handData, systemState, gestureLog };
};
