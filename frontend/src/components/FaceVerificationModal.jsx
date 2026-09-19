import React, { useState, useEffect, useRef } from 'react';
import {
  Camera,
  CheckCircle2,
  XCircle,
  RefreshCw,
  X,
  UserCheck,
  RotateCcw,
  Check,
  AlertTriangle,
  Upload
} from 'lucide-react';
import { verifyFace } from '../services/api';

export default function FaceVerificationModal({ documentId, onClose, onMatchComplete }) {
  const [loading, setLoading] = useState(false);
  const [matchResult, setMatchResult] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isConfirmed, setIsConfirmed] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  // Initialize camera on mount
  useEffect(() => {
    let active = true;

    async function startCamera() {
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error("getUserMedia is not supported by your browser environment");
        }

        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
          }
        });

        if (!active) {
          stream.getTracks().forEach(t => t.stop());
          return;
        }

        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play().catch(e => console.log("Video play warning:", e));
        }
        setCameraActive(true);
        setCameraError(null);
      } catch (err) {
        console.warn("Camera init failed:", err);
        setCameraActive(false);
        const errMsg = err.name === 'NotAllowedError'
          ? "Camera permission was denied. Please enable camera access in your browser or use the file upload fallback below."
          : `Camera stream unavailable (${err.message || 'No camera hardware found'}). Please use the file upload fallback below.`;
        setCameraError(errMsg);
      }
    }

    startCamera();

    return () => {
      active = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop());
        streamRef.current = null;
      }
    };
  }, []);

  // Capture frame from active video feed
  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    setCapturedImage(dataUrl);
    setIsConfirmed(false);
    setMatchResult(null);
  };

  // Retake photo / clear captured frame
  const handleRetake = () => {
    setCapturedImage(null);
    setIsConfirmed(false);
    setMatchResult(null);

    // Ensure video resumes playing if camera stream is active
    if (videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(e => console.log("Video resume error:", e));
    }
  };

  // Confirm captured frame
  const handleConfirm = () => {
    setIsConfirmed(true);
  };

  // Fallback: Upload an image file from disk
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setCapturedImage(reader.result);
        setIsConfirmed(false);
        setMatchResult(null);
      };
      reader.readAsDataURL(file);
    }
  };

  // Execute verification against backend
  const handleRunVerification = async () => {
    if (!capturedImage || !isConfirmed) return;
    setLoading(true);
    try {
      const res = await verifyFace(documentId, capturedImage);
      setMatchResult(res);
      if (onMatchComplete) onMatchComplete(res);
    } catch (err) {
      console.error("Face verification error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white border border-slate-200 rounded-xl max-w-lg w-full p-6 shadow-2xl relative max-h-[92vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="bg-blue-50 p-2.5 rounded-lg border border-blue-100 text-blue-600">
            <Camera className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Biometric Face Verification</h3>
            <p className="text-xs text-slate-500">Live checkpoint subject comparison against document photo</p>
          </div>
        </div>

        {/* Hidden Canvas for Frame Capture */}
        <canvas ref={canvasRef} className="hidden" />

        {/* Camera Feed / Captured Image Viewport */}
        <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-200 relative min-h-[220px] flex items-center justify-center">
          {capturedImage ? (
            // Static Captured Frame Preview
            <div className="relative w-full h-56 bg-slate-950 flex items-center justify-center">
              <img
                src={capturedImage}
                alt="Captured Subject"
                className="w-full h-full object-contain"
              />
              <div className="absolute top-2 left-2 bg-slate-900/80 text-white text-[10px] font-semibold px-2 py-0.5 rounded backdrop-blur-xs">
                {isConfirmed ? 'Frame Locked & Confirmed' : 'Captured Frame — Pending Confirmation'}
              </div>
            </div>
          ) : (
            // Live Camera Viewport
            <div className="relative w-full h-56 bg-slate-950 flex items-center justify-center">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`w-full h-full object-cover ${cameraActive ? 'block' : 'hidden'}`}
              />

              {/* Target Facial Alignment Guide Overlay */}
              {cameraActive && (
                <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                  <div className="w-36 h-44 border-2 border-dashed border-white/60 rounded-full flex items-center justify-center">
                    <span className="text-[10px] font-mono text-white/70 bg-slate-900/40 px-2 py-0.5 rounded">
                      Align Face
                    </span>
                  </div>
                </div>
              )}

              {/* Camera Offline / Error Fallback Display */}
              {!cameraActive && (
                <div className="p-6 text-center text-slate-400">
                  <Camera className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                  <p className="text-xs text-slate-300 font-medium">Camera Feed Offline</p>
                  <p className="text-[11px] text-slate-500 mt-1 max-w-xs mx-auto">
                    {cameraError || "Initializing camera stream..."}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Camera Permission / Error Warning Banner */}
        {cameraError && !capturedImage && (
          <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start space-x-2 text-xs text-amber-800">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Camera Access Notice</p>
              <p className="text-[11px] text-amber-700 mt-0.5">{cameraError}</p>
            </div>
          </div>
        )}

        {/* Action Controls for Capture / Retake / Confirm */}
        <div className="mt-3.5 space-y-2">
          {!capturedImage ? (
            <div className="flex flex-col sm:flex-row gap-2">
              <button
                onClick={handleCapture}
                disabled={!cameraActive}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-3 rounded-lg text-xs transition-colors flex items-center justify-center space-x-1.5 shadow-2xs cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Camera className="w-4 h-4" />
                <span>Capture Photo Frame</span>
              </button>

              <label className="bg-white hover:bg-slate-50 text-slate-700 font-semibold py-2 px-3 rounded-lg text-xs border border-slate-200 transition-colors flex items-center justify-center space-x-1.5 cursor-pointer shadow-2xs">
                <Upload className="w-4 h-4 text-slate-500" />
                <span>Upload File Fallback</span>
                <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
              </label>
            </div>
          ) : (
            <div className="space-y-2">
              {!isConfirmed ? (
                <div className="flex gap-2">
                  <button
                    onClick={handleRetake}
                    className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2 px-3 rounded-lg text-xs transition-colors flex items-center justify-center space-x-1.5 cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Retake Photo</span>
                  </button>

                  <button
                    onClick={handleConfirm}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2 px-3 rounded-lg text-xs transition-colors flex items-center justify-center space-x-1.5 shadow-2xs cursor-pointer"
                  >
                    <Check className="w-4 h-4" />
                    <span>Confirm This Frame</span>
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800">
                  <div className="flex items-center space-x-1.5 font-medium">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>Photo confirmed & locked. Ready for biometric scan.</span>
                  </div>
                  <button
                    onClick={handleRetake}
                    className="text-[11px] text-slate-600 hover:text-slate-900 underline font-semibold ml-2 cursor-pointer"
                  >
                    Retake
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Verification Result Card */}
        {matchResult && (
          <div
            className={`p-3.5 rounded-lg border text-xs my-4 ${
              matchResult.is_match
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                : (matchResult.details?.includes('Face not detected') ? 'bg-amber-50 border-amber-200 text-amber-800' : 'bg-red-50 border-red-200 text-red-800')
            }`}
          >
            <div className="flex items-center space-x-2 font-bold text-sm mb-1">
              {matchResult.is_match ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              ) : (matchResult.details?.includes('Face not detected') ? (
                <AlertTriangle className="w-4 h-4 text-amber-600" />
              ) : (
                <XCircle className="w-4 h-4 text-red-600" />
              ))}
              <span>
                {matchResult.details?.includes('Face not detected')
                  ? 'Face Not Detected'
                  : (matchResult.is_match ? 'Biometric Match Verified' : 'Biometric Mismatch Detected')}
              </span>
            </div>
            <p className="text-slate-600 text-xs mt-0.5">{matchResult.details}</p>
            {!matchResult.details?.includes('Face not detected') && (
              <div className="mt-2 text-[11px] font-mono text-slate-500">
                Similarity Score: {matchResult.match_score}% (Threshold: {matchResult.threshold}%)
              </div>
            )}
          </div>
        )}

        {/* Main Verification Execution Button */}
        <div className="mt-5">
          <button
            onClick={handleRunVerification}
            disabled={loading || !capturedImage || !isConfirmed}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg text-xs transition-colors flex items-center justify-center space-x-2 shadow-2xs cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <UserCheck className="w-4 h-4" />}
            <span>
              {loading
                ? 'Processing Biometric Match...'
                : !capturedImage
                ? 'Capture or Upload Subject Photo First'
                : !isConfirmed
                ? 'Confirm Frame to Enable Verification'
                : 'Run Face Verification'}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
