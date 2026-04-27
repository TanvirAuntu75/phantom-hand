import React, { useState, useEffect } from 'react';

const VoiceWave = ({ isActive, socket }) => {
  const [lastCommand, setLastCommand] = useState('');

  useEffect(() => {
    if (!socket) return;

    const handleVoiceCmd = (data) => {
      setLastCommand(data.command);
      setTimeout(() => setLastCommand(''), 1500);
    };

    const handleVoiceError = (data) => {
      setLastCommand(`ERROR: ${data.error}`);
      setTimeout(() => setLastCommand(''), 1500);
    };

    socket.on('voice_command', handleVoiceCmd);
    socket.on('voice_error', handleVoiceError);

    return () => {
      socket.off('voice_command', handleVoiceCmd);
      socket.off('voice_error', handleVoiceError);
    };
  }, [socket]);

  if (!isActive) return null;

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-[200px] h-[60px] flex flex-col items-center justify-end z-50 pointer-events-none">
      <div className="text-primary text-[10px] tracking-[0.2em] font-bold mb-1 opacity-80">
        VOICE ACTIVE
      </div>

      {/* Waveform */}
      <div className="flex items-end justify-center gap-1 h-6">
        {[...Array(12)].map((_, i) => {
          // Add some organic variation to the sine wave
          const delay = i * 0.1;
          const duration = 0.8 + (i % 3) * 0.2;

          return (
            <div
              key={i}
              className="w-1.5 bg-primary"
              style={{
                height: '4px', // base height
                animation: `waveform ${duration}s ease-in-out infinite alternate`,
                animationDelay: `${delay}s`
              }}
            />
          );
        })}
      </div>

      {/* Last Command */}
      <div className="mt-2 text-secondary text-xs tracking-widest h-4 font-bold uppercase transition-opacity duration-200">
        {lastCommand}
      </div>

      <style jsx>{`
        @keyframes waveform {
          0% { height: 4px; }
          100% { height: 24px; }
        }
      `}</style>
    </div>
  );
};

export default VoiceWave;
