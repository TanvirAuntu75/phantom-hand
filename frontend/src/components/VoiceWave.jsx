import React, { useState, useEffect } from 'react';

const VoiceWave = ({ isActive, socket }) => {
  const [lastCommand, setLastCommand] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (!socket) return;

    const handleVoiceCmd = (data) => {
      setLastCommand(data.command);
      setIsProcessing(false);
      setTimeout(() => setLastCommand(''), 2500);
    };

    const handleVoiceError = (data) => {
      setLastCommand(`ERR: ${data.error.slice(0, 15)}`);
      setIsProcessing(false);
      setTimeout(() => setLastCommand(''), 2500);
    };

    socket.on('voice_command', handleVoiceCmd);
    socket.on('voice_error', handleVoiceError);

    return () => {
      socket.off('voice_command', handleVoiceCmd);
      socket.off('voice_error', handleVoiceError);
    };
  }, [socket]);

  if (!isActive) return (
    <div className="bg-black/60 border border-phantom-accent/40 p-3 opacity-50 flex items-center justify-between backdrop-blur-sm shadow-[0_0_10px_rgba(0,0,0,0.5)]">
      <span className="text-xs font-mono tracking-widest text-phantom-accent">AUDIO_LINK_OFFLINE</span>
      <div className="w-2 h-2 bg-phantom-accent" />
    </div>
  );

  return (
    <div className="bg-black/60 border border-phantom-cyan p-4 flex flex-col space-y-4 shadow-[0_0_15px_rgba(0,229,255,0.15)] relative backdrop-blur-md">
      {/* Corner Brackets */}
      <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-phantom-cyan"></div>
      <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-phantom-cyan"></div>
      <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-phantom-cyan"></div>
      <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-phantom-cyan"></div>

      {/* Header */}
      <div className="flex items-center justify-between border-b border-phantom-cyan/30 pb-2">
        <span className="text-xs font-bold font-mono tracking-[0.3em] glow-text text-phantom-cyan">AUDIO_UPLINK</span>
        <div className="flex space-x-1 items-end h-4">
          {[...Array(10)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-phantom-cyan shadow-[0_0_5px_#00E5FF] animate-[wave_0.5s_ease-in-out_infinite_alternate]"
              style={{ 
                height: '4px',
                animationDelay: `${i * 0.05}s`,
                animationDuration: `${0.2 + (i % 3) * 0.15}s`
              }}
            />
          ))}
        </div>
      </div>

      {/* Main Display Box */}
      <div className="h-12 flex items-center justify-center border border-phantom-cyan/50 bg-phantom-cyan/10 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-phantom-cyan/20 to-transparent animate-[scanlineMove_2s_linear_infinite]" />
        {lastCommand ? (
          <div className="text-sm font-bold text-white font-mono tracking-widest z-10 drop-shadow-[0_0_5px_rgba(255,255,255,0.8)]">
            {`> ${lastCommand}`}
          </div>
        ) : (
          <div className="text-[10px] text-phantom-cyan/60 font-mono tracking-widest italic z-10">
             AWAITING_VOCAL_INPUT...
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="flex justify-between text-[8px] text-phantom-cyan/50 font-mono tracking-widest mt-1">
        <span>FRQ: 48.0KHZ</span>
        <span className="animate-pulse text-phantom-cyan">__REC__</span>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes wave {
          0% { height: 4px; opacity: 0.4; }
          100% { height: 16px; opacity: 1; }
        }
      `}} />
    </div>
  );
};

export default VoiceWave;
