import React, { useState, useEffect } from 'react';

/**
 * PHANTOM AUDIO INTERFACE
 * Visualizes the voice kernel state and displays recognized commands.
 */
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
    <div className="phantom-panel phantom-bracket p-3 opacity-30 flex items-center justify-between border-phantom-accent">
      <span className="text-[10px] tracking-widest text-phantom-accent">VOICE_OFFLINE</span>
      <div className="w-2 h-2 bg-phantom-accent rounded-full" />
    </div>
  );

  return (
    <div className="phantom-panel phantom-bracket p-4 flex flex-col space-y-4 border-phantom-cyan bg-phantom-cyan bg-opacity-5">
      {/* ── AUDIO_SPECTRUM ─────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold tracking-[0.3em] glow-text">VOICE_LISTENING</span>
        <div className="flex space-x-[2px] items-end h-4">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="w-[2px] bg-phantom-cyan animate-[wave_0.5s_ease-in-out_infinite_alternate]"
              style={{ 
                height: '4px',
                animationDelay: `${i * 0.1}s`,
                animationDuration: `${0.3 + (i % 3) * 0.2}s`
              }}
            />
          ))}
        </div>
      </div>

      {/* ── COMMAND_READOUT ────────────────────────────────────────────── */}
      <div className="h-10 flex items-center justify-center border border-phantom-accent border-dashed relative">
        <div className="absolute inset-0 bg-phantom-cyan bg-opacity-5 animate-pulse" />
        {lastCommand ? (
          <div className="text-xs font-bold text-white tracking-widest animate-data">
            {`> ${lastCommand}`}
          </div>
        ) : (
          <div className="text-[8px] text-phantom-accent tracking-tighter italic">
             [STANDBY_FOR_INPUT]
          </div>
        )}
      </div>

      {/* ── STATUS_BAR ─────────────────────────────────────────────────── */}
      <div className="flex justify-between text-[8px] text-phantom-accent font-mono">
        <span>FREQ: 44.1KHZ</span>
        <span className="animate-pulse">_LISTENING_</span>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes wave {
          0% { height: 4px; opacity: 0.3; }
          100% { height: 16px; opacity: 1; }
        }
      `}} />
    </div>
  );
};

export default VoiceWave;
