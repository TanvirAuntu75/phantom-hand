import { useState, useEffect } from 'react';

/**
 * PHANTOM DATA HOOK
 * Orchestrates real-time state synchronization between the vision backend 
 * and the tactical HUD frontend via Socket.IO.
 */
export const useHandData = (socket) => {
  const [videoFrame, setVideoFrame] = useState(null);
  const [hands, setHands] = useState([]);
  const [shapeCandidate, setShapeCandidate] = useState(null);
  const [snappedShape, setSnappedShape] = useState(null);
  const [gestureLog, setGestureLog] = useState([]);
  const [strokes3d, setStrokes3d] = useState([]);
  
  // Dedicated telemetry state for HUD diagnostics
  const [telemetry, setTelemetry] = useState({
    fps: 0,
    latency: { tracking: 0, gesture: 0, total: 0 },
    system: { cpu: 0, mem: 0 }
  });

  // System configuration state
  const [systemState, setSystemState] = useState({
    brushMode: 'BASIC',
    activeLayer: 1,
    totalLayers: 5,
    brushSize: 12,
    mode_3d: false,
    voice_active: false,
    color: '#00E5FF',
    colorIndex: 1,
    totalColors: 7
  });

  useEffect(() => {
    if (!socket) return;

    // ── UNIFIED_SYNC_STREAM ───────────────────────────────────────────
    const handleSyncFrame = (data) => {
      // 1. Update Video
      if (data.image) setVideoFrame(data.image);
      
      // 2. Update Performance Stats
      if (data.stats) {
        setTelemetry({
          fps: data.stats.fps || 0,
          latency: data.stats.latency || { tracking: 0, gesture: 0, total: 0 },
          system: data.stats.system || { cpu: 0, mem: 0 }
        });
      }

      // 3. Update Hand State
      if (data.hands) {
        setHands(data.hands);
        
        // Log valid gestures
        data.hands.forEach(hand => {
          if (hand.gesture && hand.gesture !== 'HOVER') {
            setGestureLog(prev => {
              if (prev.length > 0 && prev[0] === hand.gesture) return prev;
              return [hand.gesture, ...prev].slice(0, 10);
            });
          }
        });
      }

      // 4. Update Shape Candidate
      if (data.shape_candidate) {
        setShapeCandidate(data.shape_candidate);
      } else {
        setShapeCandidate(null);
      }

      // 5. Update System Config
      if (data.systemState) {
        setSystemState(data.systemState);
      }
    };

    // ── EVENT_TRIGGERS (Remain separate as they are rare) ─────────────
    const handleShapeSnapped = (data) => {
      setSnappedShape(data);
      setTimeout(() => setSnappedShape(null), 2000);
    };

    const handleStrokes3d = (data) => {
      setStrokes3d(data);
    };

    // Socket registration
    socket.on('sync_frame', handleSyncFrame);
    socket.on('shape_snapped', handleShapeSnapped);
    socket.on('strokes_3d', handleStrokes3d);

    return () => {
      socket.off('sync_frame', handleSyncFrame);
      socket.off('shape_snapped', handleShapeSnapped);
      socket.off('strokes_3d', handleStrokes3d);
    };
  }, [socket]);

  return { 
    videoFrame, 
    hands, 
    telemetry, 
    systemState, 
    gestureLog, 
    shapeCandidate, 
    snappedShape, 
    strokes3d 
  };
};
