/**
 * PersonaSelector.jsx
 * One-click demo persona loader strip.
 * Shown at the top of every form page so judges can fire
 * a demo without filling in 22 fields manually.
 */

import { DEMO_PERSONAS, RISK_BANDS } from "../lib/constants";

export default function PersonaSelector({ onSelect, loading }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
          Try a demo applicant
        </p>
        <span className="badge bg-orange-100 text-orange-800 ml-auto">
          Hackathon Mode
        </span>
      </div>

      <div className="flex gap-4 overflow-x-auto pb-2">
        {DEMO_PERSONAS.map((p) => {
          const band = RISK_BANDS[p.expectedBand];
          return (
            <button
              key={p.id}
              onClick={() => onSelect(p.id)}
              disabled={loading}
              className="flex-1 min-w-[140px] text-left p-4 rounded-md border border-gray-300
                         hover:border-orange-500 hover:bg-orange-50
                         transition-colors duration-150 disabled:opacity-50
                         disabled:cursor-not-allowed group bg-white shadow-sm"
            >
              <p className="text-xs font-medium text-gray-900
                            group-hover:text-orange-600 truncate">
                {p.name}
              </p>
              <p className="text-xs text-gray-500 mt-0.5 truncate">
                {p.role}
              </p>
              <div className="flex items-center gap-1 mt-1.5">
                <span
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: band.color }}
                />
                <span className="text-xs font-medium"
                      style={{ color: band.color }}>
                  ~{p.expectedScore}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
