import { useState } from "react";
import { fraudWithScore } from "../lib/api";
import { RISK_BANDS } from "../lib/constants";
import PersonaSelector from "../components/PersonaSelector";
import ScoreGauge from "../components/ScoreGauge";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorBanner from "../components/ErrorBanner";
import ApplicantForm from "../components/ApplicantForm";
import { CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react";

import { DEMO_PROFILES } from "../lib/demoData";

export default function ScorePage() {
  const [formData, setFormData] = useState(DEMO_PROFILES.ramesh);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSelectPersona = (id) => {
    if (DEMO_PROFILES[id]) {
      setFormData(DEMO_PROFILES[id]);
      setResult(null);
      setError(null);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : type === "number" ? Number(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fraudWithScore(formData);
      setResult(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <PersonaSelector onSelect={handleSelectPersona} loading={loading} />

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Form */}
        <div className="card">
          <p className="section-title">Applicant Profile</p>
          <ApplicantForm 
            formData={formData} 
            handleChange={handleChange} 
            handleSubmit={handleSubmit} 
            loading={loading} 
            buttonText="Generate Score" 
          />
        </div>

        {/* Right: Results */}
        <div>
          {loading && (
            <div className="card h-full flex items-center justify-center">
              <LoadingSpinner message="Evaluating 22 alternate data points..." />
            </div>
          )}

          {!loading && !result && (
            <div className="card h-full flex flex-col items-center justify-center text-center py-12">
              <p className="text-4xl mb-4">✨</p>
              <h3 className="text-lg font-bold text-gray-800">Ready to Score</h3>
              <p className="text-sm text-gray-500 mt-2 max-w-sm">
                Fill out the profile or load a persona above to generate an alternate credit score.
              </p>
            </div>
          )}

          {!loading && result && result.credit_score && (
            <div className="space-y-6">
              {/* Top Card: Score & Risk Band */}
              <div className="card text-center">
                <ScoreGauge score={result.credit_score.scoreseva_score} />
                
                <div className="mt-4 p-4 rounded-xl" style={{ backgroundColor: RISK_BANDS[result.credit_score.band].bg }}>
                  <p className="font-bold text-lg" style={{ color: RISK_BANDS[result.credit_score.band].color }}>
                    {result.credit_score.recommendation}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Suggested Rate: {result.credit_score.suggested_rate}
                  </p>
                </div>
              </div>

              {/* Fraud Badge */}
              <div className={`card flex items-center gap-4 ${result.fraud_check.action.includes('PROCEED') ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
                {result.fraud_check.action.includes('PROCEED') ? (
                  <CheckCircle2 className="w-8 h-8 text-green-500 flex-shrink-0" />
                ) : (
                  <ShieldAlert className="w-8 h-8 text-red-500 flex-shrink-0" />
                )}
                <div>
                  <p className="font-bold text-gray-900">Fraud Check: {result.fraud_check.action.split("—")[0].trim()}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {result.fraud_check.red_flags.length > 0 
                      ? result.fraud_check.red_flags.join(", ") 
                      : "No anomalies detected in digital footprint"}
                  </p>
                </div>
                <div className="ml-auto text-right">
                  <p className="text-2xl font-bold" style={{ color: result.fraud_check.action.includes('PROCEED') ? '#22C55E' : '#EF4444' }}>
                    {result.fraud_check.fraud_score}
                  </p>
                  <p className="text-xs text-gray-500">Risk / 100</p>
                </div>
              </div>

              {/* Top Factors */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="card">
                  <p className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500"></span>
                    Positive Factors
                  </p>
                  <div className="space-y-2">
                    {result.credit_score.top_positive_factors.map((factor, i) => (
                      <div key={i} className="text-xs font-medium bg-green-50 text-green-700 px-2 py-1.5 rounded-md border border-green-100">
                        + {factor}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card">
                  <p className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500"></span>
                    Negative Factors
                  </p>
                  <div className="space-y-2">
                    {result.credit_score.top_negative_factors.map((factor, i) => (
                      <div key={i} className="text-xs font-medium bg-red-50 text-red-700 px-2 py-1.5 rounded-md border border-red-100">
                        - {factor}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Default Probability Bar */}
              <div className="card">
                <div className="flex justify-between items-end mb-2">
                  <p className="text-sm font-bold text-gray-800">Default Probability</p>
                  <p className="text-lg font-bold" style={{ color: RISK_BANDS[result.credit_score.band].color }}>
                    {(result.credit_score.default_probability * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                  <div 
                    className="h-2.5 rounded-full transition-all duration-1000"
                    style={{ 
                      width: `${result.credit_score.default_probability * 100}%`,
                      backgroundColor: RISK_BANDS[result.credit_score.band].color
                    }}
                  ></div>
                </div>
                <p className="text-xs text-gray-400 mt-2 text-right">
                  Model confidence: High
                </p>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
