import React, { useState } from 'react';
import { Layers, Eye, SlidersHorizontal, AlertCircle } from 'lucide-react';

export default function ELAHeatmapViewer({ originalUrl, heatmapUrl, anomalies = [], elaScore = 0 }) {
  const [viewMode, setViewMode] = useState('heatmap'); // 'original', 'heatmap', 'split'
  const [sliderPos, setSliderPos] = useState(50);
  const [showAnomalies, setShowAnomalies] = useState(true);

  return (
    <div className="enterprise-card p-6 flex flex-col h-full">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 mb-4 border-b border-slate-200 gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">Forensic Tamper Analysis</h3>
            <span className="bg-slate-100 text-slate-700 text-xs px-2.5 py-0.5 rounded-full font-medium border border-slate-200">
              ELA Score: {elaScore}%
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">Error Level Analysis (ELA) JPEG compression artifact inspection</p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg text-xs font-medium text-slate-600">
          <button
            onClick={() => setViewMode('original')}
            className={`px-3 py-1.5 rounded-md transition-colors cursor-pointer ${
              viewMode === 'original' ? 'bg-white text-slate-900 font-semibold shadow-xs' : 'hover:text-slate-900'
            }`}
          >
            Original
          </button>

          <button
            onClick={() => setViewMode('heatmap')}
            className={`px-3 py-1.5 rounded-md transition-colors cursor-pointer ${
              viewMode === 'heatmap' ? 'bg-white text-blue-600 font-semibold shadow-xs' : 'hover:text-slate-900'
            }`}
          >
            ELA Heatmap
          </button>

          <button
            onClick={() => setViewMode('split')}
            className={`px-3 py-1.5 rounded-md transition-colors cursor-pointer ${
              viewMode === 'split' ? 'bg-white text-blue-600 font-semibold shadow-xs' : 'hover:text-slate-900'
            }`}
          >
            Compare
          </button>
        </div>
      </div>

      {/* Image Canvas Container */}
      <div className="relative bg-slate-900 rounded-lg overflow-hidden border border-slate-200 flex-1 min-h-[380px] flex items-center justify-center">
        {viewMode === 'original' && (
          <img
            src={originalUrl}
            alt="Original Document"
            className="w-full h-full object-contain max-h-[460px]"
          />
        )}

        {viewMode === 'heatmap' && (
          <div className="relative w-full h-full flex items-center justify-center">
            <img
              src={heatmapUrl || originalUrl}
              alt="ELA Heatmap Analysis"
              className="w-full h-full object-contain max-h-[460px]"
            />

            {/* Anomaly Bounding Box Overlays */}
            {showAnomalies &&
              anomalies.map((anno, idx) => (
                <div
                  key={idx}
                  style={{
                    left: `${(anno.x / 850) * 100}%`,
                    top: `${(anno.y / 560) * 100}%`,
                    width: `${(anno.width / 850) * 100}%`,
                    height: `${(anno.height / 560) * 100}%`,
                  }}
                  className="absolute border-2 border-red-500 bg-red-500/15 pointer-events-none flex items-start p-1"
                >
                  <span className="bg-red-600 text-white text-[11px] font-semibold px-2 py-0.5 rounded shadow-xs">
                    {anno.label} ({anno.intensity}%)
                  </span>
                </div>
              ))}
          </div>
        )}

        {viewMode === 'split' && (
          <div className="relative w-full h-full max-h-[460px] select-none">
            <img
              src={originalUrl}
              alt="Original"
              className="absolute inset-0 w-full h-full object-contain"
            />
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ width: `${sliderPos}%` }}
            >
              <img
                src={heatmapUrl || originalUrl}
                alt="Heatmap"
                className="w-full h-full object-contain max-h-[460px] max-w-none"
                style={{ width: '100%' }}
              />
            </div>

            {/* Divider Line */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-blue-500 cursor-ew-resize z-20"
              style={{ left: `${sliderPos}%` }}
            >
              <div className="absolute top-1/2 -translate-y-1/2 -left-3 bg-blue-600 text-white rounded-full p-1 shadow-md">
                <SlidersHorizontal className="w-3.5 h-3.5" />
              </div>
            </div>

            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-30"
            />
          </div>
        )}
      </div>

      {/* Legend & Controls */}
      <div className="mt-4 flex items-center justify-between text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200">
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-slate-500" />
          <span>
            {anomalies.length > 0
              ? `${anomalies.length} anomalous digital modification region(s) identified.`
              : 'No structural digital modification contours detected.'}
          </span>
        </div>

        <button
          onClick={() => setShowAnomalies(!showAnomalies)}
          aria-label={showAnomalies ? 'Hide Anomaly Overlays' : 'Show Anomaly Overlays'}
          className="text-blue-600 hover:text-blue-700 font-semibold flex items-center space-x-1 cursor-pointer"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>{showAnomalies ? 'Hide Callouts' : 'Show Callouts'}</span>
        </button>
      </div>
    </div>
  );
}
