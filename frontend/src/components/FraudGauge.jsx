/**
 * FraudGauge.jsx
 * Semi-circle SVG gauge showing Fraud Risk Score 0-100.
 * Lower is better (Green). Higher is worse (Red).
 */

import React, { useState, useEffect } from 'react';

export default function FraudGauge({ score, size: defaultSize = 220 }) {
  const [size, setSize] = useState(typeof window !== 'undefined' && window.innerWidth < 768 ? 180 : defaultSize);
  
  useEffect(() => {
    const handleResize = () => setSize(window.innerWidth < 768 ? 180 : defaultSize);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [defaultSize]);

  // 0-100 scale.
  // Color scale: 0-25 Green, 26-60 Orange, 61-100 Red
  let color = "#22C55E"; // Green
  let label = "LOW RISK";
  if (score > 25) { color = "#F59E0B"; label = "MODERATE RISK"; }
  if (score > 60) { color = "#EF4444"; label = "HIGH RISK"; }

  // Convert score to angle: 0→-180deg (left), 100→0deg (right)
  const pct       = score / 100;
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
      <svg width={size} height={size * 0.65} viewBox={`0 0 ${size} ${size * 0.65}`}>
        {/* Background arc */}
        <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`} fill="none" stroke="#E5E7EB" strokeWidth={size * 0.07} strokeLinecap="round" />

        {/* Colored arc (progress) */}
        {pct > 0 && (
          <path d={`M ${startX} ${startY} A ${r} ${r} 0 ${largeArc} 1 ${endX} ${endY}`} fill="none" stroke={color} strokeWidth={size * 0.07} strokeLinecap="round" style={{ transition: "all 0.6s ease-out" }} />
        )}

        {/* Needle */}
        <line x1={cx} y1={cy} x2={needleX} y2={needleY} stroke="#374151" strokeWidth={size * 0.018} strokeLinecap="round" style={{ transition: "all 0.6s ease-out" }} />
        <circle cx={cx} cy={cy} r={size * 0.035} fill="#374151" />
      </svg>

      {/* Score number */}
      <div className="text-center -mt-2">
        <p className="font-bold leading-none" style={{ fontSize: size * 0.2, color }}>{score.toFixed(1)}</p>
        <p className="text-sm font-semibold mt-1" style={{ color }}>{label}</p>
        <p className="text-xs text-gray-400 mt-0.5">Fraud Risk / 100</p>
      </div>
    </div>
  );
}
