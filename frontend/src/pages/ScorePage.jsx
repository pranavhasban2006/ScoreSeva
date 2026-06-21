import { useState, useEffect } from "react";
import { fraudWithScore, analyzeStatement, scoreWithStatement } from "../lib/api";
import PersonaSelector from "../components/PersonaSelector";
import ScoreGauge from "../components/ScoreGauge";
import StatementUpload from "../components/StatementUpload";
import StatementSummary from "../components/StatementSummary";
import ResultSkeleton from "../components/ResultSkeleton";
import ErrorBanner from "../components/ErrorBanner";
import ApplicantForm from "../components/ApplicantForm";
import CibilInput from "../components/CibilInput";
import CibilComparisonCard from "../components/CibilComparisonCard";
import GamingRiskPanel from "../components/GamingRiskPanel";
import DecisionLetter from "../components/DecisionLetter";
import PathToApproval from "../components/PathToApproval";
import { CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react";
import { scoreAugmented, scoreWithGamingCheck, generateLetter, getCounterfactual } from "../lib/api";
import { useScoreContext } from "../context/ScoreContext";

import { DEMO_PERSONAS, RISK_BANDS } from "../lib/constants";

export default function ScorePage() {
  const [formData, setFormData] = useState(DEMO_PERSONAS[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [statementData, setStatementData] = useState(null);
  const [statementFile, setStatementFile] = useState(null);
  const [statementLoading, setStatementLoading] = useState(false);
  const [cibilData, setCibilData] = useState(null);
  const [runAntiGamingCheck, setRunAntiGamingCheck] = useState(true);
  const [letterData, setLetterData] = useState(null);
  const [letterPayload, setLetterPayload] = useState(null);
  const [counterfactualData, setCounterfactualData] = useState(null);

  const { setCurrentContext } = useScoreContext();

  useEffect(() => {
    if (!result) {
      setCurrentContext(null);
      return;
    }

    const summary = {
      persona: formData?.name || "Custom applicant",
      final_score: result.credit_score?.scoreseva_score || null,
      decision: letterData?.decision || (result.credit_score?.scoreseva_score >= 650 ? "APPROVED" : (result.credit_score?.scoreseva_score < 500 ? "REJECTED" : "REVIEW")),
      bureau_confidence: result.augmentation?.bureau_confidence || null,
      gaming_risk_score: result.gaming_analysis?.risk_score || null,
      risk_tier: result.credit_score?.band || null,
      top_reasons: letterData?.reason_codes || [
        ...(result.credit_score?.top_positive_factors || []).map((f) => `+ ${f}`),
        ...(result.credit_score?.top_negative_factors || []).map((f) => `- ${f}`)
      ]
    };

    setCurrentContext(summary);
    
    // Cleanup on unmount
    return () => setCurrentContext(null);
  }, [formData, result, letterData, setCurrentContext]);

  const handleSelectPersona = (id) => {
    const persona = DEMO_PERSONAS.find((p) => p.id === id);
    if (persona) {
      setFormData(persona);
      setResult(null);
      setError(null);
      setStatementData(null);
      setStatementFile(null);
      setCibilData(null);
      setCounterfactualData(null);
    }
  };

  const handleAnalyzeStatement = async (file) => {
    setStatementFile(file);
    setStatementLoading(true);
    setError(null);
    try {
      const res = await analyzeStatement(file);
      setStatementData(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setStatementLoading(false);
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
      let res;
      if (runAntiGamingCheck && statementFile) {
        const payload = new FormData();
        payload.append('statement', statementFile);
        payload.append('applicant', JSON.stringify(formData));
        payload.append('previous_application_count', 0);
        
        res = await scoreWithGamingCheck(payload);
        // The endpoint returns {base_score, final_score, gaming_analysis, base_result}
        // Let's set result to base_result and attach gaming_analysis to it so the UI flows naturally
        const newResult = {
          ...res.data.base_result,
          gaming_analysis: res.data.gaming_analysis,
          penalty_applied: res.data.penalty_applied,
          score_capped: res.data.score_capped
        };
        if (res.data.penalty_applied > 0) {
           newResult.credit_score.scoreseva_score = res.data.final_score;
        }
        setResult(newResult);
      } else if (cibilData) {
        res = await scoreAugmented(formData, cibilData.data, cibilData.source);
        setResult(res.data);
      } else if (statementFile) {
        res = await scoreWithStatement(statementFile, formData);
        setResult(res.data);
      } else {
        res = await fraudWithScore(formData);
        setResult(res.data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Auto-generate letter when result comes back
  
  useEffect(() => {
    if (result && result.credit_score) {
      const score = result.credit_score.scoreseva_score;
      let decision = "REVIEW";
      if (score >= 650) decision = "APPROVED";
      else if (score < 500) decision = "REJECTED";
      
      const payload = {
        applicant_name: formData.name || "Applicant",
        decision,
        final_score: score,
        shap_values: result.credit_score.shap_values || {},
        feature_values: result.credit_score.feature_values || formData // fallback to form
      };
      
      setLetterPayload(payload);
      
      generateLetter(payload).then(res => {
        setLetterData(res.data);
      }).catch(err => {
        console.error("Failed to generate letter", err);
      });

      if (decision === "REJECTED" || decision === "REVIEW") {
        const cfPayload = {
          applicant_features: result.credit_score.feature_values || formData,
          current_score: score,
          decision,
          shap_values: result.credit_score.shap_values || {}
        };
        getCounterfactual(cfPayload).then(res => {
          setCounterfactualData(res.data);
        }).catch(err => {
          console.error("Failed to fetch counterfactual", err);
        });
      } else {
        setCounterfactualData(null);
      }
    } else {
      setLetterData(null);
      setLetterPayload(null);
      setCounterfactualData(null);
    }
  }, [result]);

  return (
    <div className="max-w-6xl mx-auto px-4 lg:px-8 space-y-6 pb-12">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl p-8 text-white shadow-lg relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -translate-y-1/2 translate-x-1/4 blur-2xl"></div>
        <div className="relative z-10 max-w-3xl">
          <h1 className="text-3xl md:text-4xl font-extrabold mb-3 leading-tight">
            190M credit-invisible Indians.<br/>Zero CIBIL scores.
          </h1>
          <p className="text-xl md:text-2xl text-orange-100 font-medium mb-6">
            ScoreSeva changes that.
          </p>
          <div className="flex flex-wrap gap-3">
            <span className="bg-white/20 backdrop-blur-sm border border-white/30 text-white px-3 py-1.5 rounded-full text-sm font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
              22 Features
            </span>
            <span className="bg-white/20 backdrop-blur-sm border border-white/30 text-white px-3 py-1.5 rounded-full text-sm font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
              6 ML Models
            </span>
            <span className="bg-white/20 backdrop-blur-sm border border-white/30 text-white px-3 py-1.5 rounded-full text-sm font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
              4 Fairness Dimensions
            </span>
          </div>
        </div>
      </div>

      <PersonaSelector onSelect={handleSelectPersona} loading={loading} />

      <StatementUpload 
        onAnalyze={handleAnalyzeStatement} 
        loading={statementLoading} 
        error={null} 
      />
      {statementData && (
        <StatementSummary 
          data={statementData} 
          scoreDelta={result?.statement_enhancement?.score_delta} 
        />
      )}

      <CibilInput 
        onSubmit={(data, source) => setCibilData({ data, source })}
        loading={loading}
        error={null}
      />

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Form */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <p className="section-title mb-0">Applicant Profile</p>
            <label className="flex items-center gap-2 cursor-pointer bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
              <input
                type="checkbox"
                checked={runAntiGamingCheck}
                onChange={(e) => setRunAntiGamingCheck(e.target.checked)}
                className="w-4 h-4 text-orange-600 rounded border-gray-300 focus:ring-orange-500"
              />
              <span className="text-xs font-bold text-gray-700">Anti-Gaming Check</span>
            </label>
          </div>
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
            <ResultSkeleton />
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

          {!loading && result && (
            <div className="space-y-6">
              
              {/* Anti-Gaming Panel */}
              {result.gaming_analysis && (
                <GamingRiskPanel result={result} />
              )}

              {/* CIBIL Comparison */}
              {result.augmentation && (
                <CibilComparisonCard result={result} />
              )}
              
              {/* Top Card: Score & Risk Band */}
              {result.credit_score && (
                <div className="card text-center">
                <ScoreGauge score={result.credit_score.scoreseva_score} />
                
                <div className="mt-4 p-4 rounded-xl" style={{ backgroundColor: RISK_BANDS[result.credit_score.band]?.bg || "#f3f4f6" }}>
                  <p className="font-bold text-lg" style={{ color: RISK_BANDS[result.credit_score.band]?.color || "#1f2937" }}>
                    {result.credit_score.recommendation}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Suggested Rate: {result.credit_score.suggested_rate}
                  </p>
                </div>
              </div>
              )}

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
              {result.credit_score && (
                <div className="card">
                  <div className="flex justify-between items-end mb-2">
                    <p className="text-sm font-bold text-gray-800">Default Probability</p>
                    <p className="text-lg font-bold" style={{ color: RISK_BANDS[result.credit_score.band]?.color || "#1f2937" }}>
                      {(result.credit_score.default_probability * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                    <div 
                      className="h-2.5 rounded-full transition-all duration-1000"
                      style={{ 
                        width: `${result.credit_score.default_probability * 100}%`,
                        backgroundColor: RISK_BANDS[result.credit_score.band]?.color || "#1f2937"
                      }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-400 mt-2 text-right">
                    Model confidence: High
                  </p>
                </div>
              )}

            </div>
          )}
        </div>
      </div>
      
      {/* Letter Section spanning full width below */}
      {letterData && (
        <div className="mt-8 pt-8 border-t border-gray-200">
          <DecisionLetter letterData={letterData} payload={letterPayload} />
          <PathToApproval counterfactualData={counterfactualData} decision={letterPayload?.decision} />
        </div>
      )}
    </div>
  );
}
