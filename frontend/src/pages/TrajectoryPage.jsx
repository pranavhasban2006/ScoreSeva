import { useState } from "react";
import { getTrajectory, getDemoTrajectory } from "../lib/api";
import { DEMO_PERSONAS } from "../lib/constants";
import PersonaSelector from "../components/PersonaSelector";
import ApplicantForm from "../components/ApplicantForm";
import ResultSkeleton from "../components/ResultSkeleton";
import ErrorBanner from "../components/ErrorBanner";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, ArrowRight, Target, Clock, Zap } from "lucide-react";

export default function TrajectoryPage() {
  const [formData, setFormData] = useState(DEMO_PERSONAS[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSelectPersona = async (id) => {
    const persona = DEMO_PERSONAS.find((p) => p.id === id);
    if (persona) {
      setFormData(persona);
      setLoading(true);
      setError(null);
      setResult(null);
      try {
        const res = await getDemoTrajectory(id);
        setResult(res.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
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
      const res = await getTrajectory(formData);
      setResult(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Convert trajectory object to recharts format
  const chartData = result ? [
    { name: "Current", Natural: result.current_score, Improved: result.current_score },
    { name: "T+6m", Natural: result.trajectory["T+6m"].natural, Improved: result.trajectory["T+6m"].improved },
    { name: "T+12m", Natural: result.trajectory["T+12m"].natural, Improved: result.trajectory["T+12m"].improved },
    { name: "T+24m", Natural: result.trajectory["T+24m"].natural, Improved: result.trajectory["T+24m"].improved },
  ] : [];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <PersonaSelector onSelect={handleSelectPersona} loading={loading} />

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Form */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-brand-orange" />
            <p className="text-lg font-semibold text-gray-900">Score Roadmap Input</p>
          </div>
          <ApplicantForm 
            formData={formData} 
            handleChange={handleChange} 
            handleSubmit={handleSubmit} 
            loading={loading} 
            buttonText="Predict Score Trajectory" 
          />
        </div>

        {/* Right: Results */}
        <div>
          {loading && (
            <ResultSkeleton />
          )}

          {!loading && !result && (
            <div className="card h-full flex flex-col items-center justify-center text-center py-12">
              <p className="text-4xl mb-4">📈</p>
              <h3 className="text-lg font-bold text-gray-800">Trajectory Predictor</h3>
              <p className="text-sm text-gray-500 mt-2 max-w-sm">
                Run a simulation to see how specific behaviors can increase the score over 24 months.
              </p>
            </div>
          )}

          {!loading && result && (
            <div className="space-y-6">
              
              {/* Summary Banner */}
              <div className="card bg-brand-orange-bg border-brand-orange-light flex items-center justify-between">
                <div>
                  <p className="text-sm text-brand-orange font-semibold uppercase tracking-wider">Current Score</p>
                  <p className="text-3xl font-bold text-gray-900">{result.current_score}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-brand-orange font-semibold uppercase tracking-wider">24m Potential</p>
                  <div className="flex items-center justify-end gap-1 text-green-600">
                    <TrendingUp className="w-6 h-6" />
                    <span className="text-3xl font-bold">+{result.total_potential_gain}</span>
                  </div>
                </div>
              </div>

              {/* Chart */}
              <div className="card">
                <p className="font-bold text-gray-800 text-sm mb-4">Score Trajectory Simulation</p>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                      <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#6B7280' }} tickLine={false} axisLine={false} />
                      <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12, fill: '#6B7280' }} tickLine={false} axisLine={false} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                        itemStyle={{ fontSize: '14px', fontWeight: 600 }}
                      />
                      <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                      <Line type="monotone" dataKey="Natural" stroke="#9CA3AF" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                      <Line type="monotone" dataKey="Improved" stroke="#F97316" strokeWidth={3} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Recommendations */}
              <div className="card">
                <p className="font-bold text-gray-800 text-sm mb-4">Top Actions to Improve Score</p>
                <div className="space-y-3">
                  {result.recommendations.map((rec, idx) => (
                    <div key={idx} className="p-4 border border-gray-100 rounded-xl hover:border-brand-orange-light transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <p className="font-semibold text-gray-800 text-sm">{rec.action}</p>
                        <span className="badge bg-green-100 text-green-700 ml-2 whitespace-nowrap">
                          {rec.score_impact}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mt-3">
                        <div>
                          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Current</p>
                          <p className="text-sm font-medium text-gray-700">{rec.current}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Target</p>
                          <div className="flex items-center gap-1">
                            <Target className="w-3.5 h-3.5 text-brand-orange" />
                            <p className="text-sm font-medium text-gray-700">{rec.target}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-1.5 mt-3 pt-3 border-t border-gray-50 text-xs text-gray-500 font-medium">
                        <Clock className="w-3.5 h-3.5" />
                        Est. Timeframe: {rec.timeframe}
                      </div>
                    </div>
                  ))}
                  
                  {result.recommendations.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-4">No specific recommendations at this time.</p>
                  )}
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
