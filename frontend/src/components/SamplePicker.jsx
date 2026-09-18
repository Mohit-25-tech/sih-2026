import React, { useEffect, useState } from 'react';
import { getSampleDocuments, loadSampleDocument } from '../services/api';
import { Play, Sparkles } from 'lucide-react';

export default function SamplePicker({ onSampleLoaded }) {
  const [samples, setSamples] = useState([]);
  const [loadingSample, setLoadingSample] = useState(null);

  useEffect(() => {
    getSampleDocuments()
      .then(setSamples)
      .catch((err) => console.error("Error fetching samples:", err));
  }, []);

  const handleSelectSample = async (sampleId) => {
    setLoadingSample(sampleId);
    try {
      const docDetail = await loadSampleDocument(sampleId);
      if (onSampleLoaded) onSampleLoaded(docDetail);
    } catch (err) {
      console.error("Error loading sample document:", err);
    } finally {
      setLoadingSample(null);
    }
  };

  return (
    <div className="enterprise-card p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">Quick Demo Scenarios</h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">Preconfigured documents for demonstrating the verification pipeline</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {samples.map((s) => {
          let badgeStyle = "bg-emerald-50 text-emerald-700 border-emerald-200";
          if (s.expected_risk === 'MEDIUM') {
            badgeStyle = "bg-amber-50 text-amber-700 border-amber-200";
          } else if (s.expected_risk === 'HIGH') {
            badgeStyle = "bg-red-50 text-red-700 border-red-200";
          }

          return (
            <div
              key={s.id}
              onClick={() => handleSelectSample(s.id)}
              className="p-4 rounded-xl border border-slate-200 bg-white hover:border-blue-300 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{s.type}</span>
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${badgeStyle}`}>
                    {s.expected_risk} RISK
                  </span>
                </div>
                <h4 className="text-sm font-bold text-slate-900 mb-1">{s.title}</h4>
                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">{s.description}</p>
              </div>

              <button
                disabled={loadingSample === s.id}
                className="mt-4 w-full bg-slate-50 hover:bg-blue-50 text-blue-600 hover:text-blue-700 text-xs py-2 rounded-lg font-semibold flex items-center justify-center space-x-1.5 border border-slate-200 hover:border-blue-200 transition-colors"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{loadingSample === s.id ? 'Running Verification...' : 'Run Verification'}</span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
