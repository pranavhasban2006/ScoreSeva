import { useState } from 'react';
import { Download, ChevronDown, ChevronUp, FileText } from 'lucide-react';
import { downloadLetterPdf } from '../lib/api';

export default function DecisionLetter({ letterData, payload }) {
  const [expanded, setExpanded] = useState(false);
  const [downloading, setDownloading] = useState(false);

  if (!letterData) return null;

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const response = await downloadLetterPdf(payload);
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ScoreSeva_Notice_${payload.applicant_name.replace(/ /g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download PDF", error);
      alert("Failed to download PDF letter.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="card max-w-3xl mx-auto border-t-4 border-t-orange-500 shadow-md">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-xl font-black tracking-tight flex items-center gap-2">
            <span className="text-orange-600">Score</span>Seva
          </h2>
          <p className="text-xs text-gray-400 mt-1 uppercase tracking-widest">Decision Notice</p>
        </div>
        <button 
          onClick={handleDownload}
          disabled={downloading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm font-medium transition-colors disabled:opacity-50"
        >
          <Download className="w-4 h-4" />
          {downloading ? "Generating..." : "Download PDF"}
        </button>
      </div>

      <div className="bg-white p-2 rounded prose prose-sm max-w-none prose-p:leading-relaxed text-gray-800" style={{ whiteSpace: 'pre-wrap' }}>
        {letterData.letter_text}
      </div>

      {letterData.technical_appendix && letterData.technical_appendix.length > 0 && (
        <div className="mt-8 pt-4 border-t border-gray-100">
          <button 
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 font-medium transition-colors"
          >
            <FileText className="w-4 h-4" />
            Technical Appendix
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          {expanded && (
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-gray-50 text-gray-600 uppercase">
                  <tr>
                    <th className="px-3 py-2 rounded-tl-lg">Feature</th>
                    <th className="px-3 py-2 text-right">SHAP Value</th>
                    <th className="px-3 py-2 text-right rounded-tr-lg">Contribution %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {letterData.technical_appendix.map((item, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-3 py-2 font-mono text-gray-700">{item.feature}</td>
                      <td className="px-3 py-2 text-right text-gray-600">{item.shap_value.toFixed(3)}</td>
                      <td className="px-3 py-2 text-right text-gray-600">{item.contribution_pct.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
