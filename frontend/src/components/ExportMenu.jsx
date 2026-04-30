import React, { useState, useEffect } from 'react';

const ExportMenu = ({ visible, onClose }) => {
  const [exporting, setExporting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    if (!visible) return;
    const timer = setTimeout(() => onClose(), 5000);
    return () => clearTimeout(timer);
  }, [visible, exporting, successMsg, onClose]);

  const handleExport = async (format) => {
    setExporting(true);
    setSuccessMsg("");

    try {
      const response = await fetch(`/api/export/${format}`, { method: 'POST' });
      const data = await response.json();

      if (data.status === 'success') {
        setSuccessMsg(`FILE_SAVED: ${data.filename}`);
        const link = document.createElement('a');
        link.href = `/api/export/${data.filename}`;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      setSuccessMsg("SYS_ERR: SAVE_FAILED");
    } finally {
      setExporting(false);
      setTimeout(() => {
        setSuccessMsg("");
        onClose();
      }, 2500);
    }
  };

  if (!visible) return null;

  return (
    <div className="absolute top-1/2 right-24 -translate-y-1/2 z-50 pointer-events-auto">
      <div className="bg-black/80 border border-phantom-cyan p-5 backdrop-blur-md w-56 shadow-[0_0_20px_rgba(0,229,255,0.2)] relative">
        <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-phantom-cyan"></div>
        <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-phantom-cyan"></div>
        <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-phantom-cyan"></div>
        <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-phantom-cyan"></div>

        <div className="text-phantom-cyan text-xs font-mono tracking-[0.3em] mb-4 border-b border-phantom-cyan/30 pb-2">
          DATA_EXPORT_PROTOCOL
        </div>

        {exporting ? (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="text-white text-xs font-mono tracking-widest mb-4 animate-pulse">
              ENCODING_DATA...
            </div>
            <div className="w-8 h-8 border border-phantom-cyan/30 border-t-phantom-cyan rounded-full animate-spin shadow-[0_0_10px_rgba(0,229,255,0.5)]"></div>
          </div>
        ) : successMsg ? (
          <div className="py-8 text-center text-white text-xs font-mono font-bold tracking-widest drop-shadow-[0_0_5px_white]">
            {successMsg}
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {['png', 'svg', 'gif', 'mp4'].map((fmt) => (
              <button
                key={fmt}
                onClick={() => handleExport(fmt)}
                className="w-full py-2 bg-phantom-cyan/5 border border-phantom-cyan/50 text-phantom-cyan text-xs font-mono tracking-[0.2em] uppercase hover:bg-phantom-cyan hover:text-black transition-all duration-200 hover:shadow-[0_0_15px_rgba(0,229,255,0.4)] text-left px-4 group flex justify-between items-center"
              >
                <span>{fmt}</span>
                <span className="opacity-0 group-hover:opacity-100 transition-opacity">&gt;</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExportMenu;
