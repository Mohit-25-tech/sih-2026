import React, { useEffect, useState } from 'react';
import { Search, ShieldCheck } from 'lucide-react';
import { getAuditLogs, getDocumentsList } from '../services/api';

export default function AuditLogs({ onNavigateDetail }) {
  const [logs, setLogs] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [filterRisk, setFilterRisk] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getAuditLogs(), getDocumentsList()])
      .then(([logsData, docsData]) => {
        setLogs(logsData);
        setDocuments(docsData);
      })
      .catch((err) => console.error("Audit log load error:", err))
      .finally(() => setLoading(false));
  }, []);

  const filteredDocs = documents.filter((d) => {
    const matchesRisk = filterRisk === 'ALL' || d.risk_level === filterRisk;
    const matchesQuery =
      d.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.id.toString().includes(searchQuery);
    return matchesRisk && matchesQuery;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="enterprise-card p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Verification History</h1>
          <p className="text-xs text-slate-500 mt-1">
            Complete audit record of all document screening activity across checkpoint entry gates.
          </p>
        </div>

        <span className="bg-slate-100 text-slate-700 font-medium px-3 py-1.5 rounded-lg border border-slate-200 text-xs">
          Total Logged: {documents.length} Screenings
        </span>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="enterprise-card p-4 flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
        {/* Search input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by filename or Document ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-slate-800 focus:outline-none focus:border-blue-500 shadow-2xs"
          />
        </div>

        {/* Risk Level Filter pills */}
        <div className="flex items-center space-x-2 w-full md:w-auto overflow-x-auto">
          <span className="text-slate-500 text-xs font-semibold mr-1">Filter Risk:</span>
          {['ALL', 'LOW', 'MEDIUM', 'HIGH'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilterRisk(lvl)}
              className={`px-3 py-1.5 rounded-lg border transition-colors cursor-pointer font-semibold ${
                filterRisk === lvl
                  ? 'bg-blue-50 text-blue-600 border-blue-200 shadow-2xs'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* History Table */}
      <div className="enterprise-card p-6">
        {loading ? (
          <div className="py-12 text-center text-slate-500 text-xs">Loading audit records...</div>
        ) : filteredDocs.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs">
            No screening records found matching search query.
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
                {filteredDocs.map((doc) => {
                  let badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
                  if (doc.risk_level === 'MEDIUM') badgeClass = "bg-amber-50 text-amber-700 border-amber-200";
                  if (doc.risk_level === 'HIGH') badgeClass = "bg-red-50 text-red-700 border-red-200";

                  return (
                    <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3.5 pl-2 font-mono text-slate-500 font-semibold">#DOC-00{doc.id}</td>
                      <td className="py-3.5 font-semibold text-slate-900">{doc.filename}</td>
                      <td className="py-3.5 text-slate-600">{doc.document_type}</td>
                      <td className="py-3.5 text-slate-500">{new Date(doc.upload_time).toLocaleString()}</td>
                      <td className="py-3.5 font-semibold text-slate-800">{doc.risk_score?.toFixed(1)} / 100</td>
                      <td className="py-3.5">
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${badgeClass}`}>
                          {doc.risk_level}
                        </span>
                      </td>
                      <td className="py-3.5 pr-2 text-right">
                        <button
                          onClick={() => onNavigateDetail(doc.id)}
                          className="text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center space-x-1 cursor-pointer"
                        >
                          <span>View Report</span>
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
