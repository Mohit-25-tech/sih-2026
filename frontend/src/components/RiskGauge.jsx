import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';

export default function RiskGauge({ score = 0, riskLevel = 'LOW' }) {
  const normScore = Math.min(100, Math.max(0, score));

  let colorClass = 'text-emerald-600 bg-emerald-500';
  let badgeStyle = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  let Icon = ShieldCheck;
  let labelText = 'LOW RISK';

  if (riskLevel === 'MEDIUM') {
    colorClass = 'text-amber-600 bg-amber-500';
    badgeStyle = 'bg-amber-50 text-amber-700 border-amber-200';
    Icon = AlertTriangle;
    labelText = 'MEDIUM RISK';
  } else if (riskLevel === 'HIGH') {
    colorClass = 'text-red-600 bg-red-500';
    badgeStyle = 'bg-red-50 text-red-700 border-red-200';
    Icon = ShieldAlert;
    labelText = 'HIGH RISK';
  }

  return (
    <div className="enterprise-card p-6 flex flex-col items-center justify-center text-center">
      {/* Risk Badge */}
      <div className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-full border text-xs font-bold uppercase tracking-wide mb-4 ${badgeStyle}`}>
        <Icon className="w-4 h-4" />
        <span>{labelText}</span>
      </div>

      {/* Numeric Score */}
      <div className="mb-3">
        <div className="text-4xl font-extrabold text-slate-900 tracking-tight font-sans">
          {normScore.toFixed(1)}
        </div>
        <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mt-0.5">
          Risk Index (0 – 100)
        </div>
      </div>

      {/* Modern Progress Bar Gauge */}
      <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden mb-2">
        <div
          className={`h-full rounded-full transition-all duration-500 ${colorClass}`}
          style={{ width: `${Math.max(4, normScore)}%` }}
        />
      </div>

      <div className="flex justify-between w-full text-[11px] font-medium text-slate-400">
        <span>0 (Authentic)</span>
        <span>50</span>
        <span>100 (High Risk)</span>
      </div>
    </div>
  );
}
