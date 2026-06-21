/**
 * ScoreGauge.jsx
 * Semi-circle SVG gauge showing ScoreSeva score 300-900.
 * Color changes based on risk band.
 */

import { RISK_BANDS } from "../lib/constants";

const SCORE_MIN = 300;
const SCORE_MAX = 900;

function getBandFromScore(score) {
  if (score >= 750) return "EXCELLENT";
  if (score >= 650) return "GOOD";
  if (score >= 550) return "FAIR";
  if (score >= 450) return "POOR";
  return "VERY POOR";
}

import React, { useState, useEffect } from 'react';

export default function ScoreGauge({ score, size: defaultSize = 220 }) {
  const [size, setSize] = useState(typeof window !== 'undefined' && window.innerWidth < 768 ? 180 : defaultSize);
  
  useEffect(() => {
    const handleResize = () => setSize(window.innerWidth < 768 ? 180 : defaultSize);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [defaultSize]);

  const band      = getBandFromScore(score);
  const bandInfo  = RISK_BANDS[band];
  const color     = bandInfo.color;

  // Convert score to angle: 300→-180deg (left), 900→0deg (right)
  const pct       = (score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN);
  const angleDeg  = -180 + pct * 180;
  const angleRad  = (angleDeg * Math.PI) / 180;

  const cx = size / 2;
  const cy = size * 0.58;
  const r  = size * 0.38;

  // Arc path from -180° to current angle
  const startX = cx - r;
  const startY = cy;
  const endX   = cx + r * Math.cos(angleRad);
  const endY   = cy + r * Math.sin(angleRad);
  const largeArc = pct > 0.5 ? 1 : 0;

  // Needle
  const needleLen = r * 0.85;
  const needleX   = cx + needleLen * Math.cos(angleRad);
  const needleY   = cy + needleLen * Math.sin(angleRad);

  return (
    <div className="flex flex-col items-center">
      <svg
        width={size}
        height={size * 0.65}
        viewBox={`0 0 ${size} ${size * 0.65}`}
      >
        {/* Background arc */}
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={size * 0.07}
          strokeLinecap="round"
        />

        {/* Colored arc (progress) */}
        {pct > 0 && (
          <path
            d={`M ${startX} ${startY} A ${r} ${r} 0 ${largeArc} 1 ${endX} ${endY}`}
            fill="none"
            stroke={color}
            strokeWidth={size * 0.07}
            strokeLinecap="round"
            style={{ transition: "all 0.6s ease-out" }}
          />
        )}

        {/* Band markers */}
        {[0, 0.25, 0.5, 0.75, 1].map((p) => {
          const a  = (-180 + p * 180) * (Math.PI / 180);
          const x1 = cx + (r - size * 0.05) * Math.cos(a);
          const y1 = cy + (r - size * 0.05) * Math.sin(a);
          const x2 = cx + (r + size * 0.02) * Math.cos(a);
          const y2 = cy + (r + size * 0.02) * Math.sin(a);
          return (
            <line
              key={p}
              x1={x1} y1={y1} x2={x2} y2={y2}
              stroke="#D1D5DB"
              strokeWidth={1.5}
            />
          );
        })}

        {/* Needle */}
        <line
          x1={cx} y1={cy}
          x2={needleX} y2={needleY}
          stroke="#374151"
          strokeWidth={size * 0.018}
          strokeLinecap="round"
          style={{ transition: "all 0.6s ease-out" }}
        />
        <circle cx={cx} cy={cy} r={size * 0.035} fill="#374151" />
      </svg>

      {/* Score number */}
      <div className="text-center mt-4 mb-2">
        <p
          className="text-6xl font-extrabold leading-none tracking-tight"
          style={{ color }}
        >
          {score}
        </p>
        <p className="text-sm font-semibold mt-2 tracking-wide" style={{ color }}>
          {bandInfo.label.toUpperCase()}
        </p>
        <p className="text-xs text-gray-500 mt-1">{bandInfo.range}</p>
      </div>
    </div>
  );
}
