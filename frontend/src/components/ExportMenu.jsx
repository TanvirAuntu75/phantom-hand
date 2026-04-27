import React, { useState, useEffect } from 'react';

const ExportMenu = ({ visible, onClose }) => {
  const [exporting, setExporting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  // Auto-dismiss logic
  useEffect(() => {
    if (!visible) return;

    const timer = setTimeout(() => {
      onClose();
    }, 4000);

    return () => clearTimeout(timer);
  }, [visible, exporting, successMsg, onClose]); // Reset timer on state changes

  const handleExport = async (format) => {
    setExporting(true);
    setSuccessMsg("");

    try {
      const response = await fetch(`/api/export/${format}`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.status === 'success') {
        setSuccessMsg(`EXPORTED: ${data.filename}`);

        // Trigger download
        const link = document.createElement('a');
        link.href = `/api/export/${data.filename}`;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      console.error(`Export ${format} failed:`, error);
      setSuccessMsg("EXPORT FAILED");
    } finally {
      setExporting(false);

      // Clear success msg and close after 2s
      setTimeout(() => {
        setSuccessMsg("");
        onClose();
      }, 2000);
    }
  };

  if (!visible) return null;

  return (
    <div className="absolute top-1/2 right-12 -translate-y-1/2 z-50 pointer-events-auto">
      <div className="bg-[#0A1628]/90 border border-primary hud-bracket p-4 backdrop-blur-md w-48 shadow-[0_0_15px_rgba(0,229,255,0.2)]">

        <div className="text-dim text-xs tracking-widest mb-4 border-b border-inactive pb-1">
          EXPORT SYSTEM
        </div>

        {exporting ? (
          <div className="flex flex-col items-center justify-center py-6">
            <div className="text-primary text-xs tracking-widest mb-2 animate-pulse">
              PROCESSING_
            </div>
            <div className="w-6 h-6 border-2 border-inactive border-t-primary rounded-full animate-spin"></div>
          </div>
        ) : successMsg ? (
          <div className="py-6 text-center text-primary text-xs font-bold tracking-widest">
            {successMsg}
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {['png', 'svg', 'gif', 'mp4'].map((fmt) => (
              <button
                key={fmt}
                onClick={() => handleExport(fmt)}
                className="w-full py-2 bg-transparent border border-primary text-primary text-sm tracking-widest uppercase hover:bg-primary hover:text-bg transition-colors"
              >
                {fmt}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExportMenu;
