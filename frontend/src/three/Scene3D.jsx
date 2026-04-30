import React, { useMemo, useEffect, useRef } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter';

const Stroke = ({ points, color, width }) => {
  const geometry = useMemo(() => {
    if (points.length < 2) return null;

    // Convert points to Vector3
    const vecs = points.map(p => new THREE.Vector3(p[0], p[1], p[2]));

    // Create curve
    const curve = new THREE.CatmullRomCurve3(vecs);

    // Create tube geometry along the curve
    return new THREE.TubeGeometry(curve, points.length * 2, width / 2, 8, false);
  }, [points, width]);

  if (!geometry) return null;

  return (
    <mesh geometry={geometry}>
      <meshBasicMaterial
        color={new THREE.Color(`rgb(${color[0]}, ${color[1]}, ${color[2]})`)}
      />
    </mesh>
  );
};

const CameraController = ({ hands }) => {
  const { camera } = useThree();

  useEffect(() => {
    if (!hands) return;

    // Find gestures across all hands
    let zoomIn = false;
    let zoomOut = false;

    for (const hand of hands) {
      if (hand.gesture === 'ZOOM_IN') zoomIn = true;
      if (hand.gesture === 'ZOOM_OUT') zoomOut = true;
    }

    if (zoomIn) {
      camera.translateZ(-5);
    } else if (zoomOut) {
      camera.translateZ(5);
    }

    // Note: TWO_HAND rotation requires delta calculations typically handled
    // by the backend sending delta angles or OrbitControls mouse mapping.
    // The prompt says "TWO_HAND rotate gesture -> rotate camera".
    // We will implement a basic zoom here. If TWO_HAND implies generic rotation:
    const twoHand = hands.filter(h => h.gesture === 'TWO_HAND').length > 0;
    // But gesture constants don't include TWO_HAND in the list, only ZOOM_IN/OUT.

  }, [hands, camera]);

  return <OrbitControls enableDamping={false} />;
};

const ExportHandler = ({ hands }) => {
  const scene = useThree(state => state.scene);

  useEffect(() => {
    if (!hands) return;

    const shouldExport = hands.some(h => h.gesture === 'FOUR_CLOSE');

    if (shouldExport) {
      const exporter = new OBJExporter();
      const result = exporter.parse(scene);

      const blob = new Blob([result], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.style.display = 'none';
      link.href = url;
      link.download = 'phantom_hand_export.obj';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  }, [hands, scene]);

  return null;
};

const Scene3D = ({ strokes, hands }) => {
  return (
    <div className="absolute inset-0 z-10 pointer-events-auto">
      <Canvas
        camera={{ position: [0, 0, 600], fov: 60 }}
        gl={{ alpha: true }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[100, 100, 100]} intensity={1} />

        {strokes.map((stroke, i) => (
          <Stroke
            key={i}
            points={stroke.points}
            color={stroke.color}
            width={stroke.width}
          />
        ))}

        <CameraController hands={hands} />
        <ExportHandler hands={hands} />
      </Canvas>
    </div>
  );
};

export default Scene3D;
