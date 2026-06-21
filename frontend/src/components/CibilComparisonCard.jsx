import { RISK_BANDS } from "../lib/constants";
import { AlertTriangle, XCircle, CheckCircle2, Info } from 'lucide-react';

export default function CibilComparisonCard({ result }) {
  if (!result || !result.augmentation) return null;

  const {
    final_score,
    score_breakdown,
    comparison,
    augmentation
  } = result;

  const {
    bureau_confidence,
    cibil_weight,
    alt_data_weight
  } = augmentation;

  const getBureauCardConfig = () => {
    if (bureau_confidence === "NONE") {
      return {
        bg: "bg-red-50",
        border: "border-red-200",
        icon: <XCircle className="w-8 h-8 text-red-500 mb-2" />,
        title: "No CIBIL file found",
        titleColor: "text-red-700",
        desc: "Most lenders stop here. Application auto-rejected."
      };
    }
    if (bureau_confidence === "LOW") {
      return {
        bg: "bg-amber-50",
        border: "border-amber-200",
        icon: <AlertTriangle className="w-8 h-8 text-amber-500 mb-2" />,
        title: "Insufficient credit history",
        titleColor: "text-amber-700",
        desc: `CIBIL score: ${comparison.bureau_only_score_estimate} · Limited data available. Many lenders decline thin-file applicants.`
      };
    }
    return {
      bg: "bg-gray-50",
      border: "border-gray-200",
      icon: <CheckCircle2 className="w-8 h-8 text-gray-500 mb-2" />,
      title: "CIBIL Score",
      titleColor: "text-gray-800",
      desc: `Score: ${comparison.bureau_only_score_estimate}`
    };
  };

  const getConfidenceColor = () => {
    if (bureau_confidence === "NONE") return "bg-red-100 text-red-800";
    if (bureau_confidence === "LOW") return "bg-amber-100 text-amber-800";
    return "bg-green-100 text-green-800";
  };

  const bureauCard = getBureauCardConfig();

  // Find the risk band
  let currentBand = null;
  for (const [name, data] of Object.entries(RISK_BANDS)) {
    const [min, max] = data.range.split('–').map(Number);
    if (final_score >= min && final_score <= max) {
      currentBand = { name, ...data };
      break;
    }
  }

  // Determine if verdict should be shown
  const showVerdict = comparison.bureau_only_score_estimate === null || Math.abs(comparison.score_difference || 0) > 20;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column: Bureau Only */}
        <div className={`p-6 rounded-lg border flex flex-col items-center justify-center text-center ${bureauCard.bg} ${bureauCard.border}`}>
          <div className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Traditional Bureau</div>
          {bureauCard.icon}
          <h3 className={`text-lg font-medium mb-2 ${bureauCard.titleColor}`}>{bureauCard.title}</h3>
          <p className="text-sm text-gray-600 max-w-[200px]">{bureauCard.desc}</p>
        </div>

        {/* Right Column: ScoreSeva Alternative */}
        <div className="card flex flex-col">
          <div className="text-xs font-bold text-orange-600 uppercase tracking-widest mb-2 text-center">ScoreSeva Score</div>
          
          <div className="flex flex-col items-center justify-center flex-grow">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider ${getConfidenceColor()}`}>
                Bureau Conf: {bureau_confidence}
              </span>
            </div>
            
            <div className="text-5xl font-bold text-gray-900 mb-2 mt-2">
              {final_score}
            </div>
            
            {currentBand && (
              <div 
                className="px-3 py-1 rounded-full text-xs font-medium border"
                style={{ backgroundColor: currentBand.bg, color: currentBand.color, borderColor: currentBand.color }}
              >
                {currentBand.label}
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Alternative Data ({(alt_data_weight * 100).toFixed(0)}%)</span>
              <span>Bureau ({(cibil_weight * 100).toFixed(0)}%)</span>
            </div>
            <div className="w-full h-2 rounded-full overflow-hidden flex">
              <div 
                className="h-full bg-orange-500 transition-all duration-500" 
                style={{ width: `${alt_data_weight * 100}%` }}
              ></div>
              <div 
                className="h-full bg-gray-300 transition-all duration-500" 
                style={{ width: `${cibil_weight * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs font-bold mt-1 text-gray-700">
              <span>{score_breakdown.from_alternative_data} pts</span>
              <span>{score_breakdown.from_bureau_data} pts</span>
            </div>
          </div>
        </div>
      </div>

      {showVerdict && comparison.verdict && (
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl p-4 text-white shadow-md flex items-start gap-4">
          <Info className="w-6 h-6 text-orange-200 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-bold text-lg leading-tight">{comparison.verdict}</p>
          </div>
        </div>
      )}
    </div>
  );
}
