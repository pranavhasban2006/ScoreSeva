import { useState } from 'react';
import { UploadCloud, FileJson, AlertCircle } from 'lucide-react';
import { getDemoCibil } from '../lib/api';

const DEMO_PERSONAS = [
  { id: 'ramesh', label: 'Ramesh' },
  { id: 'priya', label: 'Priya' },
  { id: 'vikram', label: 'Vikram' },
  { id: 'suresh', label: 'Suresh' },
  { id: 'arjun', label: 'Arjun' },
  { id: 'deepak', label: 'Deepak (gaming)' },
];

export default function CibilInput({ onSubmit, loading, error }) {
  const [tab, setTab] = useState('upload');
  const [manualData, setManualData] = useState({
    cibil_score: '',
    has_credit_history: false,
    num_active_loans: 0,
    num_overdue_accounts: 0,
    oldest_account_age_months: 0,
  });
  const [noHistory, setNoHistory] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [fileError, setFileError] = useState(null);

  const handleManualSubmit = (e) => {
    e.preventDefault();
    if (noHistory) {
      onSubmit({
        cibil_score: null,
        has_credit_history: false,
        num_active_loans: 0,
        num_overdue_accounts: 0,
        oldest_account_age_months: 0,
      }, 'manual');
    } else {
      onSubmit({
        cibil_score: manualData.cibil_score ? Number(manualData.cibil_score) : null,
        has_credit_history: manualData.has_credit_history,
        num_active_loans: Number(manualData.num_active_loans),
        num_overdue_accounts: Number(manualData.num_overdue_accounts),
        oldest_account_age_months: Number(manualData.oldest_account_age_months)
      }, 'manual');
    }
  };

  const loadDemo = async (persona) => {
    try {
      const res = await getDemoCibil(persona);
      onSubmit(res.data, 'report');
    } catch (err) {
      setFileError('Failed to load demo profile');
    }
  };

  const handleFileUpload = (file) => {
    setFileError(null);
    if (!file) return;
    if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
      setFileError('Please upload a valid JSON file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        onSubmit(json, 'report');
      } catch (err) {
        setFileError('Invalid JSON format');
      }
    };
    reader.readAsText(file);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="card shadow-sm space-y-4">
      <div className="flex justify-between items-center mb-4">
        <p className="section-title mb-0">CIBIL Report Integration</p>
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setTab('upload')}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${tab === 'upload' ? 'bg-white shadow-sm font-semibold text-orange-600' : 'text-gray-600 font-medium'}`}
          >
            Upload Report
          </button>
          <button
            onClick={() => setTab('manual')}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${tab === 'manual' ? 'bg-white shadow-sm font-semibold text-orange-600' : 'text-gray-600 font-medium'}`}
          >
            Manual Entry
          </button>
        </div>
      </div>

      {tab === 'upload' ? (
        <div className="space-y-4">
          <div 
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors
              ${dragActive ? 'border-orange-500 bg-orange-50' : 'border-gray-300 hover:border-orange-400'}
            `}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <FileJson className="w-10 h-10 mx-auto text-gray-400 mb-3" />
            <p className="text-gray-700 font-medium mb-1">Drag and drop CIBIL JSON report</p>
            <p className="text-sm text-gray-500 mb-4">or click to browse files</p>
            <input 
              type="file" 
              accept=".json" 
              className="hidden" 
              id="cibil-upload"
              onChange={(e) => handleFileUpload(e.target.files[0])}
            />
            <label 
              htmlFor="cibil-upload"
              className="btn-primary inline-flex items-center gap-2 cursor-pointer"
            >
              <UploadCloud className="w-4 h-4" />
              Select File
            </label>
          </div>
          
          {(error || fileError) && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error || fileError}
            </div>
          )}

          <div className="bg-orange-50/50 rounded-lg p-4 border border-orange-100">
            <p className="text-xs font-bold text-orange-800 uppercase tracking-wider mb-2">Try a demo profile</p>
            <div className="flex flex-wrap gap-2">
              {DEMO_PERSONAS.map(p => (
                <button
                  key={p.id}
                  onClick={() => loadDemo(p.id)}
                  className="px-3 py-1.5 bg-white border border-orange-200 text-orange-700 text-sm rounded-full hover:bg-orange-50 transition-colors shadow-sm font-medium"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <form onSubmit={handleManualSubmit} className="space-y-4">
          <div className="flex items-center gap-2 bg-gray-50 p-3 rounded-lg border border-gray-200">
            <input
              type="checkbox"
              id="noHistory"
              checked={noHistory}
              onChange={(e) => setNoHistory(e.target.checked)}
              className="w-4 h-4 text-orange-600 rounded border-gray-300 focus:ring-orange-500"
            />
            <label htmlFor="noHistory" className="text-sm font-medium text-gray-700">
              Applicant has no CIBIL history (Credit Invisible)
            </label>
          </div>

          <div className={`grid grid-cols-2 gap-4 transition-opacity ${noHistory ? 'opacity-50 pointer-events-none' : ''}`}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">CIBIL Score (Optional)</label>
              <input
                type="number"
                value={manualData.cibil_score}
                onChange={(e) => setManualData({...manualData, cibil_score: e.target.value})}
                className="input-field"
                placeholder="e.g. 650"
                min="300"
                max="900"
              />
            </div>
            
            <div className="flex flex-col justify-end">
              <label className="flex items-center gap-2 mb-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={manualData.has_credit_history}
                  onChange={(e) => setManualData({...manualData, has_credit_history: e.target.checked})}
                  className="w-4 h-4 text-orange-600 rounded border-gray-300 focus:ring-orange-500"
                />
                <span className="text-sm text-gray-700">Has past credit history</span>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Active Loans</label>
              <input
                type="number"
                value={manualData.num_active_loans}
                onChange={(e) => setManualData({...manualData, num_active_loans: e.target.value})}
                className="input-field"
                min="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Overdue Accounts</label>
              <input
                type="number"
                value={manualData.num_overdue_accounts}
                onChange={(e) => setManualData({...manualData, num_overdue_accounts: e.target.value})}
                className="input-field"
                min="0"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Oldest Account Age (months)</label>
              <input
                type="number"
                value={manualData.oldest_account_age_months}
                onChange={(e) => setManualData({...manualData, oldest_account_age_months: e.target.value})}
                className="input-field"
                min="0"
              />
            </div>
          </div>
          
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? 'Processing...' : 'Apply CIBIL Data'}
          </button>
        </form>
      )}
    </div>
  );
}
