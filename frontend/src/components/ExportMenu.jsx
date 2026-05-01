import React, { useState, useEffect } from 'react';

const ExportMenu = ({ visible, onClose }) => {
  const [exporting, setExporting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    if (!visible) return;
    const timer = setTimeout(() => onClose(), 6000);
    return () => clearTimeout(timer);
  }, [visible, exporting, successMsg, onClose]);

  const handleExport = async (format) => {
    setExporting(true);
    setSuccessMsg("");

    try {
      const response = await fetch(`/api/export/${format}`, { method: 'POST' });
      const data = await response.json();

      if (data.status === 'success') {
        setSuccessMsg(`Exported ${format.toUpperCase()}`);
        const link = document.createElement('a');
        link.href = `/api/export/${data.filename}`;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      setSuccessMsg("Export failed");
    } finally {
      setExporting(false);
      setTimeout(() => {
        setSuccessMsg("");
        onClose();
      }, 3000);
    }
  };

  if (!visible) return null;

  return (
    <div className="absolute bottom-24 right-1/2 translate-x-[150%] z-50 pointer-events-auto animate-fade-in-up">
      <div className="studio-panel p-4 flex flex-col space-y-2 w-40">

        <div className="text-xs text-studio-muted font-medium mb-1 px-2 uppercase tracking-widest text-center">
          Export As
        </div>

        {exporting ? (
          <div className="flex flex-col items-center justify-center py-6">
            <div className="w-5 h-5 border-2 border-studio-border border-t-white rounded-full animate-spin"></div>
          </div>
        ) : successMsg ? (
          <div className="py-6 text-center text-sm font-medium text-white">
            {successMsg}
          </div>
        ) : (
          ['png', 'svg', 'gif', 'mp4'].map((fmt) => (
            <button
              key={fmt}
              onClick={() => handleExport(fmt)}
              className="w-full py-2 px-3 rounded-xl text-sm font-medium text-gray-200 bg-white/5 hover:bg-white/10 hover:text-white transition-colors flex justify-between items-center"
            >
              <span className="uppercase">{fmt}</span>
              <svg className="w-4 h-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </button>
          ))
        )}
      </div>
    </div>
  );
};

export default ExportMenu;
