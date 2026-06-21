import React from 'react';

export default function PathToApproval({ counterfactualData, decision }) {
  if (!counterfactualData) return null;
  if (decision === "APPROVED" || !counterfactualData.counterfactual_needed) {
    return null;
  }

  const { fully_achievable, current_score, projected_score, changes_required, estimated_timeframe } = counterfactualData;

  return (
    <div className="card space-y-6 mt-6 border border-teal-200 shadow-sm">
      <div className="flex items-center space-x-2">
        <svg className="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
        <h2 className="text-xl font-bold text-gray-900">Path to Approval</h2>
      </div>

      {fully_achievable ? (
        <div className="bg-teal-50 rounded-lg p-4 flex items-center justify-between border border-teal-100">
          <div>
            <p className="text-sm text-teal-800 font-medium">Projected Outcome</p>
            <div className="flex items-center space-x-3 mt-1">
              <span className="text-2xl font-bold text-gray-500">{current_score}</span>
              <svg className="w-5 h-5 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <span className="text-3xl font-extrabold text-teal-700">{projected_score}</span>
            </div>
          </div>
          <div className="text-right">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-teal-100 text-teal-800">
              Approval Achievable
            </span>
          </div>
        </div>
      ) : (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-gray-700 text-sm">
          These changes would meaningfully improve your profile, though approval may require additional factors beyond what we can adjust here.
        </div>
      )}

      {changes_required && changes_required.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">Required Steps</h3>
          <ul className="space-y-3">
            {changes_required.map((change, idx) => (
              <li key={idx} className="flex space-x-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center text-xs font-bold mt-0.5">
                  {idx + 1}
                </span>
                <div>
                  <p className="text-sm font-medium text-gray-900">{change.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                  <p className="text-sm text-gray-600">{change.plain_explanation}</p>
                  <div className="flex items-center space-x-2 mt-1 text-xs text-gray-500">
                    <span className="bg-gray-100 px-2 py-0.5 rounded">{change.current_value}</span>
                    <span>→</span>
                    <span className="bg-teal-50 text-teal-700 px-2 py-0.5 rounded">{change.suggested_value}</span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {estimated_timeframe && (
        <div className="pt-4 border-t border-gray-100">
          <p className="text-xs text-gray-500 flex items-center">
            <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Estimated timeframe: {estimated_timeframe}
          </p>
        </div>
      )}
    </div>
  );
}
