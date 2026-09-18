import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ScanDocument from './pages/ScanDocument';
import DocumentDetail from './pages/DocumentDetail';
import AuditLogs from './pages/AuditLogs';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedDocId, setSelectedDocId] = useState(null);

  const handleNavigateDetail = (docId) => {
    setSelectedDocId(docId);
    setActiveTab('detail');
  };

  const handleScanComplete = (docId) => {
    setSelectedDocId(docId);
    setActiveTab('detail');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col antialiased">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === 'dashboard' && (
          <Dashboard
            onNavigateScan={() => setActiveTab('scan')}
            onNavigateDetail={handleNavigateDetail}
            onNavigateAudit={() => setActiveTab('audit')}
          />
        )}

        {activeTab === 'scan' && (
          <ScanDocument
            onScanComplete={handleScanComplete}
            onNavigateDetail={handleNavigateDetail}
          />
        )}

        {activeTab === 'detail' && selectedDocId && (
          <DocumentDetail
            docId={selectedDocId}
            onBack={() => setActiveTab('dashboard')}
          />
        )}

        {activeTab === 'audit' && (
          <AuditLogs onNavigateDetail={handleNavigateDetail} />
        )}
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500 font-medium">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>VeriBorder — Government-Grade AI Identity Screening (SIH 2026 PS ID: SIH26187)</div>
          <div>Developed by Team Zenith • Checkpoint Gateway 04</div>
        </div>
      </footer>
    </div>
  );
}
