import React from 'react';
import { AlertTriangle, TrendingDown, CheckCircle2, AlertCircle } from 'lucide-react';

export default function StatementSummary({ data, scoreDelta }) {
  if (!data) return null;

  const { statement_summary, extracted_features, income_verification } = data;
  
  const formatCurrency = (val) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(val);

  return (
    <div className="card space-y-5">
      <div className="flex justify-between items-center border-b pb-3">
        <h3 className="font-bold text-gray-900 flex items-center gap-2">
          📄 Statement Analysis
        </h3>
        <span className="text-xs font-medium bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
          {statement_summary.months_analyzed} months analyzed
        </span>
      </div>

      {/* Income Verification */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
        <p className="text-sm font-bold text-gray-700 mb-3">Income Verification</p>
        <div className="grid grid-cols-2 gap-4 mb-3">
          <div>
            <p className="text-xs text-gray-500">Claimed Annual Income</p>
            <p className="font-semibold text-gray-900">{income_verification.claimed_income ? formatCurrency(income_verification.claimed_income) : 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Actual Income (Bank Data)</p>
            <p className="font-semibold text-gray-900">{formatCurrency(income_verification.actual_income)}</p>
          </div>
        </div>
        
        {income_verification.verification_status === 'MATCHES' && (
          <div className="flex items-center gap-2 text-green-700 bg-green-50 px-3 py-2 rounded-md text-sm font-medium">
            <CheckCircle2 className="w-4 h-4" />
            Income Matches
          </div>
        )}
        {income_verification.verification_status === 'OVERSTATED' && (
          <div className="flex items-center gap-2 text-red-700 bg-red-50 px-3 py-2 rounded-md text-sm font-medium">
            <AlertCircle className="w-4 h-4" />
            ⚠️ Claimed income is {income_verification.discrepancy_pct.toFixed(0)}% higher than bank data
          </div>
        )}
        {income_verification.verification_status === 'UNDERSTATED' && (
          <div className="flex items-center gap-2 text-amber-700 bg-amber-50 px-3 py-2 rounded-md text-sm font-medium">
            <AlertTriangle className="w-4 h-4" />
            Claimed income is lower than actual income
          </div>
        )}
      </div>

      {/* 3-Column Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
          <p className="text-xs text-gray-500 mb-1">Avg Monthly Bal</p>
          <p className="font-bold text-gray-900">{formatCurrency(statement_summary.avg_monthly_balance)}</p>
        </div>
        <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
          <p className="text-xs text-gray-500 mb-1">Income Regularity</p>
          <div className="flex items-end justify-between mb-1">
            <p className="font-bold text-gray-900">{statement_summary.income_regularity_score.toFixed(0)}</p>
            <span className="text-[10px] text-gray-400">/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${statement_summary.income_regularity_score}%` }}></div>
          </div>
        </div>
        <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
          <p className="text-xs text-gray-500 mb-1">Financial Stress</p>
          <p className="font-bold text-gray-900">{statement_summary.financial_stress_score.toFixed(0)}</p>
        </div>
      </div>

      {/* Risk Signals */}
      {(statement_summary.bounce_count > 0 || statement_summary.hidden_emi_count > 0 || extracted_features.cash_withdrawal_ratio > 0) && (
        <div className="pt-2 border-t">
          <p className="text-xs font-bold text-gray-700 uppercase mb-3 tracking-wider">Risk Signals Detected</p>
          <div className="space-y-2">
            {statement_summary.bounce_count > 0 && (
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Cheque/ACH Bounces</span>
                <span className="font-bold text-red-600">{statement_summary.bounce_count} events</span>
              </div>
            )}
            {statement_summary.hidden_emi_count > 0 && (
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Undisclosed EMIs</span>
                <span className="font-bold text-amber-600">{statement_summary.hidden_emi_count} detected</span>
              </div>
            )}
            {extracted_features.cash_withdrawal_ratio > 0 && (
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Cash Withdrawals</span>
                <span className="font-bold text-gray-900">{extracted_features.cash_withdrawal_ratio.toFixed(1)}% of debits</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Enhancement Callout */}
      {scoreDelta !== undefined && scoreDelta !== null && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <TrendingDown className={`w-5 h-5 ${scoreDelta >= 0 ? 'text-green-600 rotate-180' : 'text-red-600'}`} />
            <p className="font-bold text-orange-900">
              {scoreDelta >= 0 ? '+' : ''}{scoreDelta} points vs without statement
            </p>
          </div>
          <p className="text-xs text-orange-700 mt-1">
            Statement verification added reliability to your score.
          </p>
        </div>
      )}
    </div>
  );
}
