import { useState, useEffect } from 'react';

export const useHandData = (socket) => {
  const [videoFrame, setVideoFrame] = useState(null);

  // Expose parsed hand data
  const [hands, setHands] = useState([]);
  const [fps, setFps] = useState(0);
  const [shapeCandidate, setShapeCandidate] = useState(null);
  const [snappedShape, setSnappedShape] = useState(null);
  const [gestureLog, setGestureLog] = useState([]);

  // Default system state fallback
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

  useEffect(() => {
    if (!socket) return;

    const handleVideoFrame = (data) => {
      setVideoFrame(data.image);
    };

    const handleHandData = (data) => {
      setFps(data.fps || 0);

      if (data.hands) {
        setHands(data.hands);
      }

      if (data.shape_candidate) {
        setShapeCandidate(data.shape_candidate);
      } else {
        setShapeCandidate(null);
      }

      if (data.systemState || data.canvas_state) {
        setSystemState(data.systemState || data.canvas_state);
      }

      // Update gesture log
      if (data.hands && data.hands.length > 0) {
        data.hands.forEach(hand => {
          if (hand.gesture && hand.gesture !== 'HOVER') {
             setGestureLog(prev => {
                const now = new Date();
                const timeString = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
                const entry = `${timeString} - ${hand.gesture}`;

                // Don't add if it's exactly the same as the last entry
                if (prev.length > 0 && prev[0].split(' - ')[1] === hand.gesture) {
                    return prev;
                }

                return [entry, ...prev].slice(0, 8);
             });
          }
        });
      }
    };

    const handleShapeSnapped = (data) => {
      setSnappedShape(data);
      // Clear after 2 seconds
      setTimeout(() => {
        setSnappedShape(null);
      }, 2000);
    };

    socket.on('video_frame', handleVideoFrame);
    socket.on('hand_data', handleHandData);
    socket.on('shape_snapped', handleShapeSnapped);

    return () => {
      socket.off('video_frame', handleVideoFrame);
      socket.off('hand_data', handleHandData);
      socket.off('shape_snapped', handleShapeSnapped);
    };
  }, [socket]);

  return { videoFrame, hands, fps, systemState, gestureLog, shapeCandidate, snappedShape };
};
