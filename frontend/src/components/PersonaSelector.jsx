/**
 * PersonaSelector.jsx
 * One-click demo persona loader strip.
 * Shown at the top of every form page so judges can fire
 * a demo without filling in 22 fields manually.
 */

import { DEMO_PERSONAS, RISK_BANDS } from "../lib/constants";

export default function PersonaSelector({ onSelect, loading }) {
  return (
    <div className="card mb-6">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">⚡</span>
        <p className="text-sm font-semibold text-gray-700">
          Quick Demo — Load a persona
        </p>
        <span className="badge bg-brand-orange-bg text-brand-orange ml-auto">
          Hackathon Mode
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
        {DEMO_PERSONAS.map((p) => {
          const band = RISK_BANDS[p.expectedBand];
          return (
            <button
              key={p.id}
              onClick={() => onSelect(p.id)}
              disabled={loading}
              className="text-left p-3 rounded-xl border border-gray-100
                         hover:border-brand-orange hover:bg-brand-orange-bg
                         transition-all duration-150 disabled:opacity-50
                         disabled:cursor-not-allowed group"
            >
              <p className="text-xs font-semibold text-gray-800
                            group-hover:text-brand-orange truncate">
                {p.name}
              </p>
              <p className="text-xs text-gray-400 mt-0.5 truncate">
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
