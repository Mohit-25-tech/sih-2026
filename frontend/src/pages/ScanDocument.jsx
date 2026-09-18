import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, ShieldCheck, ArrowRight } from 'lucide-react';
import { uploadDocument } from '../services/api';
import SamplePicker from '../components/SamplePicker';

export default function ScanDocument({ onScanComplete, onNavigateDetail }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [documentType, setDocumentType] = useState('PASSPORT');
  const [uploading, setUploading] = useState(false);
  const [scanStep, setScanStep] = useState(0); // 0: idle, 1: MRZ, 2: ELA, 3: Risk Fusion

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleStartScreening = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setScanStep(1); // MRZ Extraction

    try {
      setTimeout(() => setScanStep(2), 500); // ELA Heatmap
      setTimeout(() => setScanStep(3), 1000); // Risk Fusion

      const result = await uploadDocument(selectedFile, documentType);
      
      setTimeout(() => {
        setUploading(false);
        if (onScanComplete) onScanComplete(result.id);
      }, 1400);

    } catch (err) {
      console.error("Upload screening error:", err);
      setUploading(false);
      setScanStep(0);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="enterprise-card p-6">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Screen a Document</h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload an identity document to perform automated forensic verification and tamper analysis.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Zone (Left 2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="enterprise-card p-6">
            {/* Category Selector */}
            <div className="mb-5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-2">
                1. Document Category
              </label>
              <div className="grid grid-cols-3 gap-3 text-xs">
                {['PASSPORT', 'VISA', 'NATIONAL_ID'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setDocumentType(type)}
                    className={`py-2.5 px-3 rounded-lg border text-center transition-all cursor-pointer font-semibold ${
                      documentType === type
                        ? 'bg-blue-50 text-blue-600 border-blue-300 shadow-2xs'
                        : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    {type.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Dropzone Box */}
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors flex flex-col items-center justify-center min-h-[240px] ${
                selectedFile
                  ? 'border-blue-400 bg-blue-50/30'
                  : 'border-slate-300 bg-slate-50/50 hover:bg-slate-50 hover:border-slate-400'
              }`}
            >
              {previewUrl ? (
                <div className="relative w-full max-w-md max-h-60 flex flex-col items-center">
                  <img
                    src={previewUrl}
                    alt="Document Upload Preview"
                    className="max-h-48 rounded-lg object-contain border border-slate-200 shadow-sm"
                  />
                  <span className="text-xs font-semibold text-blue-600 mt-2">
                    {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <UploadCloud className="w-12 h-12 text-slate-400 mb-3" />
                  <p className="text-sm font-semibold text-slate-800 mb-1">
                    Drag and drop document image here
                  </p>
                  <p className="text-xs text-slate-500 mb-4">
                    Supports JPG, PNG, WEBP high-resolution passport scans
                  </p>
                  <label className="bg-white hover:bg-slate-50 text-slate-700 text-xs px-4 py-2.5 rounded-lg font-semibold cursor-pointer transition-colors border border-slate-300 shadow-2xs">
                    Browse files
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                </div>
              )}
            </div>

            {/* CTA Button */}
            <button
              onClick={handleStartScreening}
              disabled={!selectedFile || uploading}
              className="mt-6 w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 rounded-lg text-sm shadow-sm transition-colors flex items-center justify-center space-x-2 cursor-pointer"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{uploading ? 'Processing Pipeline...' : 'Run Forensic Verification'}</span>
            </button>
          </div>
        </div>

        {/* Pipeline Stepper (Right 1 col) */}
        <div className="space-y-4">
          <div className="enterprise-card p-6">
            <h3 className="text-sm font-bold text-slate-900 mb-4">
              Verification Pipeline
            </h3>

            <div className="space-y-3 text-xs">
              <div className={`p-3 rounded-lg border flex items-center space-x-3 ${
                scanStep >= 1 ? 'bg-blue-50 border-blue-200 text-blue-900' : 'bg-slate-50 border-slate-200 text-slate-500'
              }`}>
                <CheckCircle2 className={`w-4 h-4 shrink-0 ${scanStep >= 1 ? 'text-blue-600' : 'text-slate-400'}`} />
                <div>
                  <div className="font-semibold">01. OCR & MRZ Extraction</div>
                  <div className="text-[11px] text-slate-500">ICAO 9303 7-3-1 Checksum</div>
                </div>
              </div>

              <div className={`p-3 rounded-lg border flex items-center space-x-3 ${
                scanStep >= 2 ? 'bg-blue-50 border-blue-200 text-blue-900' : 'bg-slate-50 border-slate-200 text-slate-500'
              }`}>
                <CheckCircle2 className={`w-4 h-4 shrink-0 ${scanStep >= 2 ? 'text-blue-600' : 'text-slate-400'}`} />
                <div>
                  <div className="font-semibold">02. ELA Tamper Analysis</div>
                  <div className="text-[11px] text-slate-500">Error Level Heatmap</div>
                </div>
              </div>

              <div className={`p-3 rounded-lg border flex items-center space-x-3 ${
                scanStep >= 3 ? 'bg-blue-50 border-blue-200 text-blue-900' : 'bg-slate-50 border-slate-200 text-slate-500'
              }`}>
                <CheckCircle2 className={`w-4 h-4 shrink-0 ${scanStep >= 3 ? 'text-blue-600' : 'text-slate-400'}`} />
                <div>
                  <div className="font-semibold">03. Cross-Zone Validation</div>
                  <div className="text-[11px] text-slate-500">Visual vs MRZ zone match</div>
                </div>
              </div>

              <div className={`p-3 rounded-lg border flex items-center space-x-3 ${
                scanStep >= 3 ? 'bg-blue-50 border-blue-200 text-blue-900' : 'bg-slate-50 border-slate-200 text-slate-500'
              }`}>
                <CheckCircle2 className={`w-4 h-4 shrink-0 ${scanStep >= 3 ? 'text-blue-600' : 'text-slate-400'}`} />
                <div>
                  <div className="font-semibold">04. Risk Fusion Engine</div>
                  <div className="text-[11px] text-slate-500">Weighted Risk Rating</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Demo Presets */}
      <SamplePicker onSampleLoaded={(doc) => onNavigateDetail(doc.id)} />
    </div>
  );
}
