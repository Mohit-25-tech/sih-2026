import React, { useEffect, useState } from 'react';
import { ShieldCheck, AlertTriangle, FileSearch, ArrowRight, CheckCircle2, Clock, Shield } from 'lucide-react';
import { getDocumentsList } from '../services/api';
import SamplePicker from '../components/SamplePicker';

export default function Dashboard({ onNavigateScan, onNavigateDetail, onNavigateAudit }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDocs = async () => {
    try {
      const data = await getDocumentsList();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const totalCount = documents.length;
  const highRiskCount = documents.filter(d => d.risk_level === 'HIGH').length;
  const mediumRiskCount = documents.filter(d => d.risk_level === 'MEDIUM').length;
  const lowRiskCount = documents.filter(d => d.risk_level === 'LOW').length;
  const passRate = totalCount > 0 ? (((lowRiskCount + mediumRiskCount) / totalCount) * 100).toFixed(0) : 100;

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="enterprise-card p-6 md:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 bg-gradient-to-r from-slate-900 via-slate-800 to-blue-950 text-white border-0 shadow-md">
        <div>
          <div className="flex items-center space-x-2 text-blue-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <span className="w-2 h-2 rounded-full bg-blue-400"></span>
            <span>Border Security Checkpoint — Gateway 04</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            VERIBORDER
          </h1>
          <p className="text-blue-100 font-medium text-base mt-0.5">
            AI-powered identity document verification
          </p>
          <p className="text-xs text-blue-200 mt-2 max-w-xl leading-relaxed">
            Automated document verification, tamper detection and risk assessment for border security.
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={onNavigateScan}
            className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-5 py-2.5 rounded-lg text-sm shadow-sm transition-colors flex items-center space-x-2 cursor-pointer"
          >
            <FileSearch className="w-4 h-4" />
            <span>Start New Screening</span>
          </button>

          <button
            onClick={onNavigateAudit}
            className="bg-white/10 hover:bg-white/20 text-white font-medium px-4 py-2.5 rounded-lg text-sm border border-white/10 transition-colors cursor-pointer"
          >
            <span>View Audit Log</span>
          </button>
        </div>
      </div>

      {/* Analytics Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="enterprise-card p-5">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Documents Screened</span>
            <Shield className="w-5 h-5 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{totalCount}</div>
          <div className="text-xs text-slate-500 mt-1">Total screenings logged</div>
        </div>

        <div className="enterprise-card p-5">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">High Risk</span>
            <AlertTriangle className="w-5 h-5 text-red-600" />
          </div>
          <div className="text-2xl font-bold text-red-600">{highRiskCount}</div>
          <div className="text-xs text-slate-500 mt-1">Forgery & tampering flagged</div>
        </div>

        <div className="enterprise-card p-5">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Clearance Rate</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{passRate}%</div>
          <div className="text-xs text-slate-500 mt-1">Based on screened documents</div>
        </div>

        <div className="enterprise-card p-5">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Avg. Processing</span>
            <Clock className="w-5 h-5 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">1.2s</div>
          <div className="text-xs text-slate-500 mt-1">End-to-end pipeline latency</div>
        </div>
      </div>

      {/* Quick Demo Scenarios */}
      <SamplePicker onSampleLoaded={(doc) => onNavigateDetail(doc.id)} />

      {/* Recent Activity Table */}
      <div className="enterprise-card p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recent Verification Activity</h3>
            <p className="text-xs text-slate-500 mt-0.5">Latest document screenings recorded at Gateway 04</p>
          </div>
          
          <button 
            onClick={onNavigateAudit}
            className="text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center space-x-1 cursor-pointer"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {loading ? (
          <div className="py-10 text-center text-slate-500 text-xs">Loading activity feed...</div>
        ) : documents.length === 0 ? (
          <div className="py-10 text-center text-slate-500 text-xs">
            No document screenings recorded yet. Click "Start New Screening" or select a demo scenario above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-slate-500 border-b border-slate-200 text-[11px] uppercase font-semibold tracking-wider">
                  <th className="pb-3 pl-2">Document ID</th>
                  <th className="pb-3">Filename</th>
                  <th className="pb-3">Type</th>
                  <th className="pb-3">Timestamp</th>
                  <th className="pb-3">Risk Score</th>
                  <th className="pb-3">Risk Status</th>
                  <th className="pb-3 pr-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {documents.slice(0, 6).map((doc) => {
                  let badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
                  if (doc.risk_level === 'MEDIUM') badgeClass = "bg-amber-50 text-amber-700 border-amber-200";
                  if (doc.risk_level === 'HIGH') badgeClass = "bg-red-50 text-red-700 border-red-200";

                  return (
                    <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 pl-2 font-mono text-slate-500">#DOC-00{doc.id}</td>
                      <td className="py-3 font-semibold text-slate-900">{doc.filename}</td>
                      <td className="py-3 text-slate-600">{doc.document_type}</td>
                      <td className="py-3 text-slate-500">{new Date(doc.upload_time).toLocaleTimeString()}</td>
                      <td className="py-3 font-semibold text-slate-800">{doc.risk_score?.toFixed(1)} / 100</td>
                      <td className="py-3">
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${badgeClass}`}>
                          {doc.risk_level}
                        </span>
                      </td>
                      <td className="py-3 pr-2 text-right">
                        <button
                          onClick={() => onNavigateDetail(doc.id)}
                          className="text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center space-x-1 cursor-pointer"
                        >
                          <span>Inspect Report</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
