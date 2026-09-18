import React from 'react';
import { Shield, LayoutDashboard, FileSearch, ClipboardList, UserCheck } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 px-6 py-3 shadow-xs">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div 
          className="flex items-center space-x-3 cursor-pointer group" 
          onClick={() => setActiveTab('dashboard')}
        >
          <div className="bg-blue-600 text-white p-2 rounded-lg shadow-xs group-hover:bg-blue-700 transition-colors">
            <Shield className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">VERIBORDER</span>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 text-xs px-2 py-0.5 rounded font-medium">
                Enterprise Security
              </span>
            </div>
            <p className="text-xs text-slate-500 font-normal">AI Document Screening & Verification</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex items-center space-x-1 font-medium text-sm">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-md transition-colors cursor-pointer ${
              activeTab === 'dashboard'
                ? 'bg-blue-50 text-blue-600 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => setActiveTab('scan')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-md transition-colors cursor-pointer ${
              activeTab === 'scan'
                ? 'bg-blue-50 text-blue-600 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <FileSearch className="w-4 h-4" />
            <span>Screen Document</span>
          </button>

          <button
            onClick={() => setActiveTab('audit')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-md transition-colors cursor-pointer ${
              activeTab === 'audit'
                ? 'bg-blue-50 text-blue-600 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <ClipboardList className="w-4 h-4" />
            <span>Audit Log</span>
          </button>
        </nav>

        {/* System Status & Officer Profile */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-emerald-50 border border-emerald-200 text-emerald-700 px-2.5 py-1 rounded-full text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>System Active</span>
          </div>

          <div className="hidden md:flex items-center space-x-2.5 pl-3 border-l border-slate-200 text-xs">
            <div className="bg-slate-100 text-slate-700 p-1.5 rounded-full">
              <UserCheck className="w-4 h-4" />
            </div>
            <div>
              <div className="font-semibold text-slate-800">Officer Zenith</div>
              <div className="text-slate-500 font-mono text-[11px]">Checkpoint 04</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
