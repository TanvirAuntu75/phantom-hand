import React from 'react';

const SystemPanel = ({ isConnected, telemetry }) => {
  const { fps = 0 } = telemetry || {};

  return (
    <div className="studio-pill px-4 py-2 flex items-center space-x-4">
      {/* Status Dot */}
      <div className="flex items-center space-x-2">
        <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-studio-secondary shadow-[0_0_8px_#4ADE80]' : 'bg-red-500'}`} />
        <span className="text-xs font-medium text-gray-300">
          {isConnected ? 'Connected' : 'Offline'}
        </span>
      </div>

      <div className="w-px h-4 bg-studio-border" />

      {/* FPS Counter */}
      <div className="flex items-center space-x-1.5">
        <span className="text-xs text-studio-muted">FPS</span>
        <span className="text-sm font-semibold text-white w-6 text-right">
          {Math.round(fps || 0)}
        </span>
      </div>
    </div>
  );
};

export default SystemPanel;
