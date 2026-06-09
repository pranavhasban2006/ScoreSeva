import { useState } from "react";
import { fraudWithScore } from "../lib/api";
import { DEMO_PROFILES } from "../lib/demoData";
import PersonaSelector from "../components/PersonaSelector";
import FraudGauge from "../components/FraudGauge";
import ApplicantForm from "../components/ApplicantForm";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorBanner from "../components/ErrorBanner";
import { ShieldCheck, ShieldAlert, AlertTriangle, AlertCircle, Fingerprint } from "lucide-react";

export default function FraudPage() {
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
          <div className="flex items-center gap-2 mb-4">
            <Fingerprint className="w-5 h-5 text-gray-500" />
            <p className="text-lg font-semibold text-gray-900">Fraud Analysis Input</p>
          </div>
          <ApplicantForm 
            formData={formData} 
            handleChange={handleChange} 
            handleSubmit={handleSubmit} 
            loading={loading} 
            buttonText="Run Fraud Check" 
          />
        </div>

        {/* Right: Results */}
        <div>
          {loading && (
            <div className="card h-full flex items-center justify-center">
              <LoadingSpinner message="Scanning digital footprint for anomalies..." />
            </div>
          )}

          {!loading && !result && (
            <div className="card h-full flex flex-col items-center justify-center text-center py-12">
              <p className="text-4xl mb-4">🕵️</p>
              <h3 className="text-lg font-bold text-gray-800">Fraud Detector Ready</h3>
              <p className="text-sm text-gray-500 mt-2 max-w-sm">
                Fill out the profile or load a persona to run isolation forest anomaly detection.
              </p>
            </div>
          )}

          {!loading && result && result.fraud_check && (
            <div className="space-y-6">
              
              {/* Top Banner Recommendation */}
              <div 
                className="rounded-xl p-4 text-center border font-semibold text-lg"
                style={{ 
                  backgroundColor: result.fraud_check.color + '10', 
                  borderColor: result.fraud_check.color + '30',
                  color: result.fraud_check.color 
                }}
              >
                {result.combined_recommendation}
              </div>

              {/* Gauge and Verdict Card */}
              <div className="card flex flex-col sm:flex-row items-center gap-6 justify-center text-center sm:text-left">
                <FraudGauge score={result.fraud_check.fraud_score} />
                <div className="flex-1 space-y-3">
                  <p className="text-sm text-gray-500 font-medium">System Verdict</p>
                  <div className="flex items-center justify-center sm:justify-start gap-2">
                    {result.fraud_check.action.includes('PROCEED') ? (
                      <ShieldCheck className="w-6 h-6 text-green-500" />
                    ) : result.fraud_check.action.includes('FLAG') ? (
                      <AlertTriangle className="w-6 h-6 text-yellow-500" />
                    ) : (
                      <ShieldAlert className="w-6 h-6 text-red-500" />
                    )}
                    <span 
                      className="text-xl font-bold" 
                      style={{ color: result.fraud_check.color }}
                    >
                      {result.fraud_check.action.split('—')[0].trim()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {result.fraud_check.action.split('—')[1]?.trim() || result.fraud_check.action}
                  </p>
                </div>
              </div>

              {/* Breakdown Bar */}
              <div className="card space-y-4">
                <p className="font-bold text-gray-800 text-sm">Risk Score Breakdown</p>
                
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Isolation Forest (AI Anomaly)</span>
                    <span className="font-medium text-gray-700">{result.fraud_check.isolation_risk.toFixed(1)} / 100</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${Math.min(100, result.fraud_check.isolation_risk)}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Rule-based Penalty</span>
                    <span className="font-medium text-gray-700">+{result.fraud_check.rule_penalty.toFixed(1)} points</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div className="bg-orange-500 h-2 rounded-full" style={{ width: `${Math.min(100, result.fraud_check.rule_penalty)}%` }}></div>
                  </div>
                </div>
              </div>

              {/* Red Flags List */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <p className="font-bold text-gray-800 text-sm">Triggered Red Flags</p>
                  <span className="badge bg-red-100 text-red-700">
                    {result.fraud_check.red_flag_count} Flags
                  </span>
                </div>
                
                {result.fraud_check.red_flags.length === 0 ? (
                  <div className="p-4 bg-green-50 border border-green-100 rounded-xl flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    <p className="text-sm text-green-700 font-medium">No red flags detected.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {result.fraud_check.red_flags.map((flag, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-3 bg-red-50 border border-red-100 rounded-xl">
                        <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-red-800 font-medium">{flag}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
