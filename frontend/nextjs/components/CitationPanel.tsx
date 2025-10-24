/**
 * Citation Panel Component
 * Displays dataset citations with clickable links and provenance access
 */

import React from 'react';
import { ExternalLink, Database, Clock } from 'lucide-react';
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
    <div className="mt-6 p-4 bg-gray-50 rounded-lg border">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700 flex items-center">
          <Database className="w-4 h-4 mr-2" />
          Data Sources ({citations.length})
        </h3>
        
        <div className="flex items-center space-x-4">
          {processingTime && (
            <span className="text-xs text-gray-500 flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {processingTime.toFixed(0)}ms
            </span>
          )}
          
          <button
            onClick={onShowProvenance}
            className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 transition-colors"
          >
            Show Provenance
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {citations.map((citation, index) => (
          <div key={index} className="flex items-start justify-between p-2 bg-white rounded border">
            <div className="flex-1">
              <h4 className="text-sm font-medium text-gray-900 mb-1">
                {citation.dataset_title}
              </h4>
              <p className="text-xs text-gray-600 mb-1">
                Publisher: {citation.publisher}
              </p>
              {citation.query_summary && (
                <p className="text-xs text-gray-500">
                  {citation.query_summary}
                </p>
              )}
            </div>
            
            <a
              href={citation.resource_url}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-3 text-blue-600 hover:text-blue-800 transition-colors"
              title="Open original dataset"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};