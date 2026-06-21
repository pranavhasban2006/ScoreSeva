import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, X, Loader2 } from 'lucide-react';
import { getDemoStatement } from '../lib/api';
import ErrorBanner from './ErrorBanner';

export default function StatementUpload({ onAnalyze, loading, error }) {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  
  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) return;
    
    // Check extension
    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (!['pdf', 'csv'].includes(ext)) {
      alert("Invalid file type. Only PDF and CSV are supported.");
      return;
    }
    
    // Check size (10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert("File too large. Maximum size is 10MB.");
      return;
    }
    
    setFile(selectedFile);
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
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };
  
  const handleAnalyze = () => {
    if (file) {
      onAnalyze(file);
    }
  };

  const loadDemo = async (name) => {
    try {
      const response = await getDemoStatement(name);
      const blob = new Blob([response.data], { type: 'text/csv' });
      const demoFile = new File([blob], `${name}_statement.csv`, { type: 'text/csv' });
      setFile(demoFile);
      onAnalyze(demoFile);
    } catch (err) {
      alert("Failed to load demo statement.");
    }
  };

  return (
    <div className="card shadow-sm space-y-4">
      <h3 className="text-lg font-bold">Augment with Bank Statement (Optional)</h3>
      {error && <ErrorBanner message={error} onDismiss={() => {}} />}
      
      {!file ? (
        <>
          <div 
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${dragActive ? 'border-orange-500 bg-orange-50' : 'border-gray-300 hover:border-orange-400'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              ref={fileInputRef}
              type="file" 
              className="hidden" 
              accept=".pdf,.csv" 
              onChange={handleChange}
            />
            <UploadCloud className="w-12 h-12 mx-auto text-gray-400 mb-3" />
            <p className="font-medium text-gray-700">Drag & drop your bank statement (PDF or CSV)</p>
            <p className="text-sm text-gray-500 mt-1">Last 6 months recommended · Max 10MB</p>
          </div>
          
          <div className="text-sm text-gray-600">
            <span className="font-medium">No statement? Try a demo:</span>
            <div className="flex flex-wrap gap-2 mt-2">
              {['ramesh', 'priya', 'vikram', 'suresh', 'arjun', 'deepak'].map(persona => (
                <button
                  key={persona}
                  onClick={() => loadDemo(persona)}
                  className={`px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-xs font-medium transition-colors capitalize ${
                    persona === 'deepak' ? 'bg-purple-100 text-purple-800 hover:bg-purple-200 border border-purple-200' : ''
                  }`}
                >
                  {persona === 'arjun' ? 'Arjun (fraud)' : persona === 'deepak' ? 'Deepak (gaming)' : persona}
                </button>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="bg-gray-50 border rounded-xl p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-100 text-orange-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <p className="font-medium text-gray-900 truncate max-w-[200px]">{file.name}</p>
                <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
            <button 
              onClick={() => { setFile(null); }}
              className="p-1 text-gray-400 hover:text-red-500 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <button 
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-70"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Reading transactions...
              </>
            ) : (
              "Analyze Statement"
            )}
          </button>
        </div>
      )}
    </div>
  );
}
