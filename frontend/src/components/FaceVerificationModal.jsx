import React, { useState } from 'react';
import { Camera, CheckCircle2, XCircle, RefreshCw, X, UserCheck } from 'lucide-react';
import { verifyFace } from '../services/api';

export default function FaceVerificationModal({ documentId, onClose, onMatchComplete }) {
  const [loading, setLoading] = useState(false);
  const [matchResult, setMatchResult] = useState(null);
  const [liveImagePreview, setLiveImagePreview] = useState(null);

  const handleRunVerification = async () => {
    setLoading(true);
    try {
      const res = await verifyFace(documentId);
      setMatchResult(res);
      if (onMatchComplete) onMatchComplete(res);
    } catch (err) {
      console.error("Face verification error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateWebcam = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setLiveImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="bg-white border border-slate-200 rounded-xl max-w-md w-full p-6 shadow-xl relative">
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="bg-blue-50 p-2.5 rounded-lg border border-blue-100 text-blue-600">
            <Camera className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Biometric Face Verification</h3>
            <p className="text-xs text-slate-500">Match document photo against live subject image</p>
          </div>
        </div>

        {/* Camera / Upload Container */}
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200 flex flex-col items-center justify-center min-h-[200px] my-4">
          {liveImagePreview ? (
            <img src={liveImagePreview} alt="Live Subject" className="max-h-44 rounded-md object-cover border border-slate-200" />
          ) : (
            <div className="text-center p-4">
              <Camera className="w-10 h-10 text-slate-400 mx-auto mb-2" />
              <p className="text-xs text-slate-600 font-medium mb-3">Live Video Snapshot (Checkpoint Gate 04)</p>
              <label className="bg-white hover:bg-slate-100 text-slate-700 text-xs px-3.5 py-2 rounded-md font-semibold cursor-pointer border border-slate-300 transition-colors inline-block shadow-2xs">
                Upload Live Image
                <input type="file" accept="image/*" onChange={handleSimulateWebcam} className="hidden" />
              </label>
            </div>
          )}
        </div>

        {/* Results Box */}
        {matchResult && (
          <div className={`p-3.5 rounded-lg border text-xs my-4 ${
            matchResult.is_match
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-red-50 border-red-200 text-red-800'
          }`}>
            <div className="flex items-center space-x-2 font-bold text-sm mb-1">
              {matchResult.is_match ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <XCircle className="w-4 h-4 text-red-600" />}
              <span>{matchResult.is_match ? 'Biometric Match Verified' : 'Biometric Mismatch Detected'}</span>
            </div>
            <p className="text-slate-600 text-xs mt-0.5">{matchResult.details}</p>
            <div className="mt-2 text-[11px] font-mono text-slate-500">
              Similarity Score: {matchResult.match_score}% (Threshold: {matchResult.threshold}%)
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="mt-5">
          <button
            onClick={handleRunVerification}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg text-xs transition-colors flex items-center justify-center space-x-2 shadow-2xs cursor-pointer disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <UserCheck className="w-4 h-4" />}
            <span>{loading ? 'Processing Biometrics...' : 'Run Face Verification'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
