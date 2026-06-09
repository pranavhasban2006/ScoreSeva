import { useEffect, useState } from "react";
import { getHealth } from "../lib/api";
import { CheckCircle2, XCircle, RefreshCw, Activity } from "lucide-react";
import LoadingSpinner from "../components/LoadingSpinner";

const MODEL_LABELS = {
  xgboost_scorer:       "XGBoost Credit Scorer",
  feature_columns:      "Feature Columns",
  label_encoders:       "Label Encoders",
  nlp_psychometric:     "NLP Psychometric",
  fraud_detector:       "Fraud Detector",
  trajectory_predictor: "Trajectory Predictor",
};

export default function HealthPage() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getHealth();
      setData(res.data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchHealth(); }, []);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Activity className="w-6 h-6 text-brand-orange" />
            API Health
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Live status of the ScoreSeva backend and all 6 ML models
          </p>
        </div>
        <button
          onClick={fetchHealth}
          disabled={loading}
          className="btn-secondary flex items-center gap-2 text-sm py-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {loading && <LoadingSpinner message="Checking API health..." />}

      {error && (
        <div className="card border-red-100 bg-red-50">
          <p className="text-red-600 text-sm font-medium">
            ❌ Cannot reach backend: {error}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Make sure uvicorn is running on port 8000.
          </p>
        </div>
      )}

      {data && (
        <div className="space-y-4">
          {/* Overall status */}
          <div className={`card border-2 ${
            data.status === "healthy"
              ? "border-green-200 bg-green-50"
              : "border-yellow-200 bg-yellow-50"
          }`}>
            <div className="flex items-center gap-3">
              {data.status === "healthy"
                ? <CheckCircle2 className="w-8 h-8 text-green-500" />
                : <XCircle     className="w-8 h-8 text-yellow-500" />
              }
              <div>
                <p className="font-bold text-gray-900 text-lg capitalize">
                  {data.status}
                </p>
                <p className="text-sm text-gray-500">
                  {data.app_name} v{data.version} · {data.environment}
                </p>
              </div>
            </div>
          </div>

          {/* Model status grid */}
          <div className="card">
            <p className="section-title">ML Model Status</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {Object.entries(data.models || {}).map(([key, loaded]) => (
                <div
                  key={key}
                  className={`flex items-center gap-3 p-3 rounded-xl
                    ${loaded ? "bg-green-50" : "bg-red-50"}`}
                >
                  {loaded
                    ? <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                    : <XCircle      className="w-4 h-4 text-red-500  flex-shrink-0" />
                  }
                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      {MODEL_LABELS[key] || key}
                    </p>
                    <p className={`text-xs font-semibold
                      ${loaded ? "text-green-600" : "text-red-500"}`}>
                      {loaded ? "Loaded" : "Not loaded"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Backend info */}
          <div className="card">
            <p className="section-title">Backend Info</p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Base URL</span>
                <span className="font-mono text-gray-800 text-xs">
                  {import.meta.env.VITE_API_URL || "http://localhost:8000"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Swagger Docs</span>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="text-brand-orange hover:underline text-xs font-medium"
                >
                  localhost:8000/docs ↗
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
