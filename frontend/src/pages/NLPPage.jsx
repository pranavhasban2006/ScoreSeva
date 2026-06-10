import { useState } from "react";
import { nlpScore, nlpDemo } from "../lib/api";
import { NLP_DEMO_PROFILES } from "../lib/constants";
import ResultSkeleton from "../components/ResultSkeleton";
import ErrorBanner from "../components/ErrorBanner";
import { MessageSquare, ShieldCheck, ShieldAlert, Sparkles, AlertCircle, ArrowRight } from "lucide-react";

export default function NLPPage() {
  const [formData, setFormData] = useState({
    why_loan: "",
    repayment_plan: "",
    financial_situation: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSelectDemo = async (id) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await nlpDemo(id);
      setResult(res.data);
      // Optional: fill form just to show what it looks like, but the backend demo text isn't returned in full.
      // So we just clear the form or leave it. The prompt says "no form fill needed".
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await nlpScore(formData);
      setResult(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper to render psychometric bars
  const renderSignalBar = (label, value, isNegativeSignal = false) => {
    const pct = Math.max(0, Math.min(100, value * 100));
    let color = isNegativeSignal ? 'bg-red-500' : 'bg-green-500';
    if (!isNegativeSignal && pct < 40) color = 'bg-orange-400';
    if (isNegativeSignal && pct > 40) color = 'bg-red-600';

    return (
      <div className="mb-3" key={label}>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-600 font-medium">{label}</span>
          <span className="text-gray-800 font-bold">{pct.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div className={`${color} h-2 rounded-full transition-all duration-700`} style={{ width: `${pct}%` }}></div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      
      {/* Top Demo Strip */}
      <div className="card bg-gray-50 border-dashed border-2">
        <p className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Load Demo Profile</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {NLP_DEMO_PROFILES.map((p) => (
            <button
              key={p.id}
              onClick={() => handleSelectDemo(p.id)}
              disabled={loading}
              className="text-left p-3 rounded-xl border bg-white hover:border-brand-orange-light hover:shadow-md transition-all flex flex-col gap-2"
              style={{ borderLeftWidth: '4px', borderLeftColor: p.color }}
            >
              <span className="font-bold text-gray-800 text-sm">{p.label}</span>
              <span className="text-xs text-gray-500 line-clamp-2 italic">"{p.preview}"</span>
            </button>
          ))}
        </div>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left: Input Form */}
        <div className="card flex flex-col h-full">
          <div className="flex items-center gap-2 mb-4">
            <MessageSquare className="w-5 h-5 text-brand-orange" />
            <p className="text-lg font-semibold text-gray-900">Psychometric Text Analysis</p>
          </div>
          <p className="text-sm text-gray-500 mb-6">
            Enter the applicant's free-text responses to analyze their borrowing intent, financial stress, and planning capabilities.
          </p>

          <form onSubmit={handleSubmit} className="space-y-5 flex-1 flex flex-col">
            <div className="flex-1 flex flex-col gap-5">
              <div>
                <label className="label">Why do you need this loan? (Required)</label>
                <textarea
                  name="why_loan"
                  value={formData.why_loan}
                  onChange={handleChange}
                  required
                  placeholder="E.g. I need this to buy inventory for my shop..."
                  className="input-field min-h-[100px] resize-y"
                ></textarea>
              </div>

              <div>
                <label className="label">How do you plan to repay? (Optional)</label>
                <textarea
                  name="repayment_plan"
                  value={formData.repayment_plan}
                  onChange={handleChange}
                  placeholder="E.g. My shop earns 20,000 per month..."
                  className="input-field min-h-[80px] resize-y"
                ></textarea>
              </div>

              <div>
                <label className="label">Describe your financial situation (Optional)</label>
                <textarea
                  name="financial_situation"
                  value={formData.financial_situation}
                  onChange={handleChange}
                  placeholder="E.g. Stable income but need capital for growth..."
                  className="input-field min-h-[80px] resize-y"
                ></textarea>
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full mt-4 flex justify-center items-center gap-2">
              <Sparkles className="w-4 h-4" />
              {loading ? "Analyzing Intent..." : "Run NLP Analysis"}
            </button>
          </form>
        </div>

        {/* Right: Results */}
        <div className="flex flex-col h-full">
          {loading && (
            <ResultSkeleton />
          )}

          {!loading && !result && (
            <div className="card flex-1 flex flex-col items-center justify-center text-center py-12">
              <p className="text-4xl mb-4">🧠</p>
              <h3 className="text-lg font-bold text-gray-800">Psychometric Analyzer</h3>
              <p className="text-sm text-gray-500 mt-2 max-w-sm">
                Submit text or load a demo profile to reveal hidden creditworthiness signals.
              </p>
            </div>
          )}

          {!loading && result && (
            <div className="space-y-4">
              
              {/* Score & Risk Badge Header */}
              <div className="card flex flex-col sm:flex-row items-center justify-between gap-4 bg-gradient-to-br from-white to-orange-50 border-orange-100">
                <div className="text-center sm:text-left">
                  <p className="text-sm text-gray-500 font-bold uppercase tracking-wider mb-1">NLP Credit Score</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-5xl font-extrabold text-brand-orange">{result.nlp_credit_score.toFixed(0)}</span>
                    <span className="text-xl text-gray-400 font-semibold">/ 100</span>
                  </div>
                </div>
                
                <div className="text-center sm:text-right">
                  <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold text-sm ${result.risk_label.includes('LOW') ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'}`}>
                    {result.risk_label.includes('LOW') ? <ShieldCheck className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
                    {result.risk_label}
                  </div>
                  <p className="text-xs text-gray-500 mt-2 font-medium">
                    Risk Probability: {(result.risk_probability * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Sentiment Score Bar */}
              <div className="card">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-bold text-gray-800">Financial Sentiment</span>
                  <span className={`text-sm font-bold ${result.sentiment_score > 0 ? 'text-green-600' : 'text-red-500'}`}>
                    {result.sentiment_score > 0 ? '+' : ''}{result.sentiment_score.toFixed(2)}
                  </span>
                </div>
                <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden flex">
                  {/* -1 to +1 scale. 0 is center. */}
                  <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-gray-400 z-10"></div>
                  {result.sentiment_score < 0 && (
                    <div className="absolute top-0 bottom-0 bg-red-500" style={{ left: `${(1 + result.sentiment_score) * 50}%`, right: '50%' }}></div>
                  )}
                  {result.sentiment_score >= 0 && (
                    <div className="absolute top-0 bottom-0 bg-green-500" style={{ left: '50%', width: `${result.sentiment_score * 50}%` }}></div>
                  )}
                </div>
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>Negative (-1)</span>
                  <span>Neutral (0)</span>
                  <span>Positive (+1)</span>
                </div>
              </div>

              {/* Main Content Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Psychometric Signals */}
                <div className="card">
                  <p className="font-bold text-gray-800 text-sm mb-4">Psychometric Signals</p>
                  
                  {renderSignalBar("Planning Orientation", result.psychometric_signals.planning_orientation || result.psychometric_signals.planning_score, false)}
                  {renderSignalBar("Future Focus", result.psychometric_signals.future_orientation, false)}
                  {renderSignalBar("Productive Use", result.psychometric_signals.productive_use || result.psychometric_signals.productive_use_score, false)}
                  {renderSignalBar("Responsibility", result.psychometric_signals.responsibility || result.psychometric_signals.responsibility_score, false)}
                  {renderSignalBar("Detail Specificity", result.psychometric_signals.specificity || result.psychometric_signals.specificity_score, false)}
                  {renderSignalBar("Numeric Confidence", result.psychometric_signals.numeric_confidence, false)}
                  
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-xs font-bold text-gray-400 uppercase mb-3">Red Flags</p>
                    {renderSignalBar("Urgency / Desperation", result.psychometric_signals.urgency_flag, true)}
                    {renderSignalBar("Debt Stress", result.psychometric_signals.stress_flag, true)}
                  </div>
                </div>

                {/* Text Insights */}
                <div className="card bg-gray-50 border-gray-100">
                  <p className="font-bold text-gray-800 text-sm mb-4">Key NLP Insights</p>
                  <ul className="space-y-3">
                    {result.text_insights.map((insight, idx) => {
                      const isWarning = insight.includes('⚠️');
                      return (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                          {isWarning ? (
                            <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                          ) : (
                            <ArrowRight className="w-4 h-4 text-brand-orange mt-0.5 flex-shrink-0" />
                          )}
                          <span>{insight.replace('⚠️ ', '')}</span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
