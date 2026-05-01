import React, { useState, useEffect } from 'react';

const VoiceWave = ({ isActive, socket }) => {
  const [lastCommand, setLastCommand] = useState('');

  useEffect(() => {
    if (!socket) return;

    const handleVoiceCmd = (data) => {
      setLastCommand(data.command);
      setTimeout(() => setLastCommand(''), 3000);
    };

    socket.on('voice_command', handleVoiceCmd);
    return () => socket.off('voice_command', handleVoiceCmd);
  }, [socket]);

  if (!isActive && !lastCommand) return null;

  return (
    <div className="studio-pill px-4 py-2 flex items-center space-x-3 bg-indigo-500/10 border-indigo-500/30 overflow-hidden max-w-xs animate-fade-in-up">
      {isActive ? (
        <div className="w-4 h-4 bg-indigo-400 organic-blob opacity-80" />
      ) : (
        <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      )}

      <span className="text-sm font-medium text-white truncate w-full">
        {lastCommand || "Listening..."}
      </span>
    </div>
  );
};

export default VoiceWave;
