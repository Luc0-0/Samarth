/**
 * Citation Panel Component
 * Displays dataset citations with clickable links and provenance access
 */

import React from 'react';
import { ExternalLink, Database, Clock, Download } from 'lucide-react';
import { Citation } from '../lib/api';

interface CitationPanelProps {
  citations: Citation[];
  onShowProvenance: () => void;
  processingTime?: number;
}

export const CitationPanel: React.FC<CitationPanelProps> = ({
  citations,
  onShowProvenance,
  processingTime
}) => {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="mt-6 p-6 bg-gradient-to-br from-slate-50 to-gray-50 rounded-2xl border border-gray-200/50 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800 flex items-center">
          <Database className="w-5 h-5 mr-2 text-slate-600" />
          Data Sources ({citations.length})
        </h3>
        
        <div className="flex items-center space-x-4">
          {processingTime && (
            <span className="text-xs text-gray-600 flex items-center px-2 py-1 bg-white/60 rounded-full">
              <Clock className="w-3 h-3 mr-1" />
              {processingTime.toFixed(0)}ms
            </span>
          )}
          
          <button
            onClick={onShowProvenance}
            className="text-sm font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-4 py-2 rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-md"
          >
            Show Provenance
          </button>
        </div>
      </div>

      <div className="mb-4 text-sm text-blue-700 bg-gradient-to-r from-blue-50 to-indigo-50 p-3 rounded-xl border border-blue-200/50">
        💡 <strong>Tip:</strong> Links redirect to data.gov.in search if original files moved. Use PDF download for processed data samples.
      </div>
      
      <div className="space-y-2">
        {citations.map((citation, index) => (
          <div key={index} className="flex items-start justify-between p-4 bg-white/70 backdrop-blur-sm rounded-xl border border-gray-200/50 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="text-sm font-semibold text-gray-900">
                  {citation.dataset_title}
                </h4>
                {citation.status_badge && (
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    citation.status_color === 'green' ? 'bg-green-100 text-green-700' :
                    citation.status_color === 'amber' ? 'bg-amber-100 text-amber-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {citation.status_color === 'green' ? '⚡' : citation.status_color === 'amber' ? '🔍' : '🔍'} {citation.status_badge}
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-600 mb-1 font-medium">
                Publisher: <span className="text-blue-600">{citation.publisher}</span>
              </p>
              {citation.query_summary && (
                <p className="text-xs text-gray-500 italic">
                  {citation.query_summary}
                </p>
              )}
              {citation.status_description && (
                <p className="text-xs text-gray-500 mt-1">
                  {citation.status_description}
                </p>
              )}
            </div>
            
            <div className="ml-3 flex space-x-2">
              <button
                onClick={() => {
                  // Generate PDF report
                  const question = "Sample question for this dataset";
                  fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/export-pdf`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                  })
                  .then(response => response.blob())
                  .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'samarth-report.pdf';
                    a.click();
                    window.URL.revokeObjectURL(url);
                  })
                  .catch(err => console.error('PDF download failed:', err));
                }}
                className="text-green-600 hover:text-green-800 transition-colors"
                title="Download PDF report"
              >
                <Download className="w-4 h-4" />
              </button>
              <span className="text-gray-400">|</span>
              <a
                href={citation.resource_url || citation.search_url || `https://data.gov.in/search?title=${encodeURIComponent(citation.dataset_title)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 transition-colors"
                title={citation.status_description || "Search for dataset on data.gov.in"}
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};