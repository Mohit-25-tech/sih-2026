import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  Camera,
  Download,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  ShieldCheck,
  ShieldAlert,
  Loader2
} from 'lucide-react';
import { getDocumentDetail } from '../services/api';
import RiskGauge from '../components/RiskGauge';
import ELAHeatmapViewer from '../components/ELAHeatmapViewer';
import FaceVerificationModal from '../components/FaceVerificationModal';

export default function DocumentDetail({ docId, onBack }) {
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showFaceModal, setShowFaceModal] = useState(false);

  useEffect(() => {
    if (docId) {
      getDocumentDetail(docId)
        .then((data) => {
          setDoc(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Error loading document detail:", err);
          setLoading(false);
        });
    }
  }, [docId]);

  if (loading) {
    return (
      <div className="py-24 text-center space-y-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
        <p className="text-sm text-slate-500 font-medium">Loading Verification Report #DOC-00{docId}...</p>
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="py-24 text-center space-y-3">
        <p className="text-red-600 font-bold text-base">Document #DOC-00{docId} not found.</p>
        <button onClick={onBack} className="text-blue-600 underline text-xs font-semibold">Back to Dashboard</button>
      </div>
    );
  }

  const riskScore = doc.risk_score?.score || 0;
  const riskLevel = doc.risk_score?.risk_level || 'LOW';
  const factors = doc.risk_score?.factors || {};
  const reasoning = doc.risk_score?.summary_reasoning || '';
  const fields = doc.extracted_fields || [];
  const elaResult = doc.tamper_result || {};

  const exportReportJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(doc, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `VeriBorder_Report_DOC_${doc.id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Convert raw reasoning string to clean checklist items for judge presentation
  const reasoningLines = reasoning
    .split('\n')
    .filter(line => line.trim().length > 0 && !line.includes('ALERTS') && !line.includes('AUTHENTIC'));

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg text-slate-600 hover:text-slate-900 transition-colors cursor-pointer shadow-2xs"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Document Verification Report</span>
              <span className="text-xs text-slate-300">•</span>
              <span className="text-xs font-mono text-slate-500">#DOC-00{doc.id}</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {doc.filename}
            </h1>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowFaceModal(true)}
            className="bg-white hover:bg-slate-50 text-slate-700 text-xs px-3.5 py-2 rounded-lg border border-slate-200 font-semibold flex items-center space-x-1.5 transition-colors cursor-pointer shadow-2xs"
          >
            <Camera className="w-4 h-4 text-blue-600" />
            <span>Face Verification</span>
          </button>

          <button
            onClick={exportReportJson}
            className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3.5 py-2 rounded-lg font-semibold flex items-center space-x-1.5 shadow-xs transition-colors cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export Report</span>
          </button>
        </div>
      </div>

      {/* Risk Summary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Gauge Card */}
        <RiskGauge score={riskScore} riskLevel={riskLevel} />

        {/* Verification Analytical Cards & Explainable AI */}
        <div className="lg:col-span-2 space-y-4">
          {/* Analytical Summary Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="enterprise-card p-4">
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">MRZ Checksum</div>
              <div className={`text-base font-bold mt-1 ${!factors.mrz_detected ? 'text-slate-500' : (factors.checksum_pass ? 'text-emerald-600' : 'text-red-600')}`}>
                {!factors.mrz_detected ? 'N/A' : (factors.checksum_pass ? 'PASS' : 'FAIL')}
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">
                {!factors.mrz_detected ? 'No MRZ on document' : 'ICAO 9303 standard'}
              </div>
            </div>

            <div className="enterprise-card p-4">
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Field Consistency</div>
              <div className={`text-base font-bold mt-1 ${!factors.mrz_detected ? 'text-slate-500' : (factors.mismatched_count === 0 ? 'text-emerald-600' : 'text-amber-600')}`}>
                {!factors.mrz_detected ? 'N/A' : (factors.mismatched_count === 0 ? 'Consistent' : `${factors.mismatched_count} Mismatches`)}
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">
                {!factors.mrz_detected ? 'Cross-zone check skipped' : 'Visual vs MRZ zone'}
              </div>
            </div>

            <div className="enterprise-card p-4">
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">ELA Tamper</div>
              <div className={`text-base font-bold mt-1 ${elaResult.ela_score > 40 ? 'text-red-600' : 'text-emerald-600'}`}>
                {elaResult.ela_score?.toFixed(1)}%
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">JPEG artifact diff</div>
            </div>

            <div className="enterprise-card p-4">
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Face Match</div>
              <div className={`text-base font-bold mt-1 ${factors.has_face_check && factors.face_match_score != null ? (factors.face_match_score >= 65 ? 'text-emerald-600' : 'text-red-600') : 'text-slate-500'}`}>
                {factors.has_face_check && factors.face_match_score != null ? `${factors.face_match_score}%` : 'Not Run'}
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">
                {factors.has_face_check ? 'Biometric similarity' : 'Verification pending'}
              </div>
            </div>
          </div>

          {/* Explainable AI Panel */}
          <div className="enterprise-card p-5">
            <h3 className="text-sm font-bold text-slate-900 mb-3">
              Why this document received this score
            </h3>

            <div className="space-y-2.5 text-xs">
              {reasoningLines.map((line, idx) => {
                const isFail = line.includes('Failed') || line.includes('Failure') || line.includes('Anomaly') || line.includes('Mismatch');
                const isWarn = line.includes('Inconsistency') || line.includes('Flag');

                let icon = <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />;
                let itemBg = "bg-emerald-50/60 border-emerald-100 text-emerald-950";

                if (isFail) {
                  icon = <XCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />;
                  itemBg = "bg-red-50/60 border-red-100 text-red-950 font-medium";
                } else if (isWarn) {
                  icon = <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />;
                  itemBg = "bg-amber-50/60 border-amber-100 text-amber-950";
                }

                const cleanLineText = line.replace(/^[•\s\-\d\.]+\s*/, '');

                return (
                  <div key={idx} className={`p-3 rounded-lg border flex items-start space-x-2.5 ${itemBg}`}>
                    {icon}
                    <span className="leading-relaxed">{cleanLineText}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Forensic ELA Heatmap Viewer */}
      <ELAHeatmapViewer
        originalUrl={doc.file_path}
        heatmapUrl={elaResult.ela_heatmap_path}
        anomalies={elaResult.anomaly_regions || []}
        elaScore={elaResult.ela_score || 0}
      />

      {/* Extracted Fields Comparison Table */}
      <div className="enterprise-card p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Cross-Zone Field Validation
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Visual OCR zone text vs. parsed MRZ zone data comparison</p>
          </div>
        </div>

        {factors.mrz_detected === false ? (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 text-center text-slate-500">
            <p className="text-xs font-semibold text-slate-700">Cross-zone validation not applicable — no MRZ zone detected on this document.</p>
            <p className="text-[11px] text-slate-500 mt-1">Cross-zone verification compares visual zone fields against cryptographic MRZ fields. For documents without an MRZ (e.g. college IDs, standard licences), this check is bypassed.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-500 border-b border-slate-200 text-[11px] uppercase font-semibold tracking-wider">
                  <th className="pb-3 pl-2">Field Name</th>
                  <th className="pb-3">Visual Zone Value</th>
                  <th className="pb-3">Parsed MRZ Value</th>
                  <th className="pb-3">Confidence</th>
                  <th className="pb-3 pr-2 text-right">Validation Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {fields.map((f, i) => {
                  const hasVisual = f.visual_value && f.visual_value !== 'Not Detected';
                  const hasMrz = f.mrz_value && f.mrz_value !== 'Not Detected';
                  const isNA = !hasVisual || !hasMrz;

                  return (
                    <tr key={i} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 pl-2 font-semibold text-slate-900">{f.field_name}</td>
                      <td className={`py-3 ${hasVisual ? (f.is_match ? 'text-slate-800' : 'text-red-600 font-bold') : 'text-slate-400 italic'}`}>
                        {f.visual_value || '—'}
                      </td>
                      <td className={`py-3 font-mono ${hasMrz ? 'text-slate-700' : 'text-slate-400 italic'}`}>
                        {f.mrz_value || '—'}
                      </td>
                      <td className="py-3 text-slate-500">
                        {isNA ? '—' : `${(f.confidence * 100).toFixed(0)}%`}
                      </td>
                      <td className="py-3 pr-2 text-right">
                        {isNA ? (
                          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold border bg-slate-100 text-slate-600 border-slate-200">
                            <span>N/A</span>
                          </span>
                        ) : (
                          <span
                            className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
                              f.is_match
                                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                : 'bg-red-50 text-red-700 border-red-200'
                            }`}
                          >
                            {f.is_match ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                            <span>{f.is_match ? 'Match' : 'Mismatch'}</span>
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Face Verification Modal Popup */}
      {showFaceModal && (
        <FaceVerificationModal
          documentId={doc.id}
          onClose={() => setShowFaceModal(false)}
          onMatchComplete={() => {
            getDocumentDetail(doc.id).then(setDoc);
          }}
        />
      )}
    </div>
  );
}
