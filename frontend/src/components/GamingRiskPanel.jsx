import { ShieldAlert, Info, ArrowDownToLine, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

const TIER_COLORS = {
  CLEAN: { bg: 'bg-green-100', text: 'text-green-800', bar: 'bg-green-500' },
  LOW_RISK: { bg: 'bg-blue-100', text: 'text-blue-800', bar: 'bg-blue-500' },
  ELEVATED: { bg: 'bg-amber-100', text: 'text-amber-800', bar: 'bg-amber-500' },
  HIGH_RISK: { bg: 'bg-red-100', text: 'text-red-800', bar: 'bg-red-600' }
};

const SIGNAL_EXPLANATIONS = {
  salary_injection_spike: "Salary injection spike — a large lump-sum deposit occurred suspiciously close to the application date.",
  circular_transaction_pattern: "Circular transactions — money flows out and returns shortly after, artificially inflating cash flow.",
  round_number_bias: "Round number bias — unusually high percentage of transaction amounts end in 000 or 500, suggesting staged activity.",
  declared_vs_actual_income_gap: "Income gap — declared income significantly exceeds actual verified income.",
  employment_tenure_inconsistency: "Tenure inconsistency — claimed employment history does not match verified salary duration.",
  rapid_reapplication_pattern: "Rapid reapplication — multiple recent applications, attempting to iterate/game the score.",
  dormant_account_reactivation: "Account reactivation — account was dormant for months then suddenly activated just before application."
};

export default function GamingRiskPanel({ result }) {
  const [expanded, setExpanded] = useState(false);

  if (!result || !result.gaming_analysis) return null;

  const { gaming_analysis, penalty_applied, score_capped } = result;
  const { gaming_risk_score, risk_tier, signals, flagged_signal_count } = gaming_analysis;

  const colors = TIER_COLORS[risk_tier] || TIER_COLORS.CLEAN;
  
  const activeSignals = Object.entries(signals).filter(([key, data]) => {
    if (key === "declared_vs_actual_income_gap") {
      return data.detected && data.severity !== "LOW";
    }
    return data.detected;
  });

  return (
    <div className="card shadow-sm space-y-0 p-0 overflow-hidden">
      <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-b border-gray-200">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900">Anti-Gaming Analysis</h3>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
          {risk_tier.replace('_', ' ')}
        </span>
      </div>

      <div className="bg-white p-6">
        <div className="mb-4">
          <div className="flex justify-between items-end mb-1">
            <span className="text-sm font-medium text-gray-700">Gaming Risk Score</span>
            <span className={`text-lg font-bold ${colors.text}`}>{gaming_risk_score} / 100</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-1000 ${colors.bar}`}
              style={{ width: `${Math.min(gaming_risk_score, 100)}%` }}
            ></div>
          </div>
        </div>

        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-gray-600 font-medium">Signals detected: <span className="font-bold text-gray-900">{flagged_signal_count} of 7</span></p>
          {activeSignals.length > 0 && (
            <button 
              onClick={() => setExpanded(!expanded)} 
              className="text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1 font-medium"
            >
              {expanded ? 'Hide Details' : 'Show Details'}
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          )}
        </div>

        {expanded && activeSignals.length > 0 && (
          <div className="mt-3 space-y-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
            {activeSignals.map(([key, data]) => (
              <div key={key} className="flex items-start gap-2 text-sm">
                <Info className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                <span className="text-slate-700">{SIGNAL_EXPLANATIONS[key] || "Irregular pattern detected."}</span>
              </div>
            ))}
          </div>
        )}

        {penalty_applied > 0 && (
          <div className="mt-4 bg-red-50 text-red-700 p-3 rounded-lg flex items-start gap-3 border border-red-100">
            <ArrowDownToLine className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-500" />
            <div>
              <p className="font-bold text-sm">-{penalty_applied} points applied</p>
              <p className="text-xs mt-0.5 opacity-90">Score reduced due to detected gaming patterns.</p>
            </div>
          </div>
        )}

        {score_capped && (
          <div className="mt-2 bg-slate-900 text-white p-3 rounded-lg flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-400" />
            <div>
              <p className="font-bold text-sm text-red-100">Score capped at 550</p>
              <p className="text-xs mt-0.5 text-slate-300">Maximum allowable score restricted regardless of other factors due to high-risk gaming signals.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
