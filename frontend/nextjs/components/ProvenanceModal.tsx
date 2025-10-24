/**
 * Provenance Modal Component
 * Shows detailed data lineage, SQL queries, and sample data
 */

import React, { useState, useEffect } from 'react';
import { X, Download, Code, Database, Calendar, ExternalLink } from 'lucide-react';
import { ProvenanceData, RawDataResponse, apiClient } from '../lib/api';

interface ProvenanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  provenance: ProvenanceData;
  requestId: string;
}

export const ProvenanceModal: React.FC<ProvenanceModalProps> = ({
  isOpen,
  onClose,
  provenance,
  requestId
}) => {
  const [rawData, setRawData] = useState<Record<string, RawDataResponse>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});

  const loadRawData = async (datasetId: string) => {
    if (rawData[datasetId] || loading[datasetId]) return;
    
    setLoading(prev => ({ ...prev, [datasetId]: true }));
    
    try {
      const data = await apiClient.getRawData(datasetId);
      setRawData(prev => ({ ...prev, [datasetId]: data }));
    } catch (error) {
      console.error('Failed to load raw data:', error);
    } finally {
      setLoading(prev => ({ ...prev, [datasetId]: false }));
    }
  };

  const downloadSampleCSV = (datasetId: string) => {
    const data = rawData[datasetId];
    if (!data) return;

    const csv = [
      Object.keys(data.sample_rows[0] || {}).join(','),
      ...data.sample_rows.map(row => 
        Object.values(row).map(val => 
          typeof val === 'string' && val.includes(',') ? `"${val}"` : val
        ).join(',')
      )
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${datasetId}_sample.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Database className="w-5 h-5 mr-2" />
            Data Provenance & Audit Trail
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Request Info */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2 flex items-center">
              <Calendar className="w-4 h-4 mr-2" />
              Request Information
            </h3>
            <div className="text-sm text-blue-800">
              <p><strong>Request ID:</strong> {requestId}</p>
              <p><strong>Timestamp:</strong> {new Date().toLocaleString()}</p>
              <p><strong>Audit Trail:</strong> Available in logs/query_log.jsonl</p>
            </div>
          </div>

          {/* SQL Queries */}
          <div className="mb-6">
            <h3 className="font-medium text-gray-900 mb-3 flex items-center">
              <Code className="w-4 h-4 mr-2" />
              SQL Queries Executed
            </h3>
            {provenance.sql_queries.map((query, index) => (
              <div key={index} className="mb-3">
                <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
                  <code>{query}</code>
                </pre>
              </div>
            ))}
          </div>

          {/* Datasets Used */}
          <div className="mb-6">
            <h3 className="font-medium text-gray-900 mb-3 flex items-center">
              <Database className="w-4 h-4 mr-2" />
              Datasets Used ({provenance.datasets_used.length})
            </h3>
            
            <div className="space-y-4">
              {provenance.datasets_used.map((dataset, index) => {
                const datasetId = dataset.sample_endpoint.split('/').pop() || '';
                const hasRawData = rawData[datasetId];
                const isLoading = loading[datasetId];

                return (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">
                          {dataset.dataset_title}
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">
                          Table: {dataset.table_name}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <a
                          href={dataset.resource_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 transition-colors"
                          title="Open original dataset"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                        
                        <button
                          onClick={() => loadRawData(datasetId)}
                          disabled={isLoading}
                          className="text-sm bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200 transition-colors disabled:opacity-50"
                        >
                          {isLoading ? 'Loading...' : hasRawData ? 'Loaded' : 'Load Sample'}
                        </button>
                        
                        {hasRawData && (
                          <button
                            onClick={() => downloadSampleCSV(datasetId)}
                            className="text-sm bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200 transition-colors flex items-center"
                          >
                            <Download className="w-3 h-3 mr-1" />
                            CSV
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Sample Data */}
                    {hasRawData && (
                      <div className="mt-3 p-3 bg-gray-50 rounded">
                        <h5 className="text-sm font-medium text-gray-700 mb-2">
                          Sample Data ({hasRawData.total_sample_rows} rows)
                        </h5>
                        <div className="overflow-x-auto">
                          <table className="min-w-full text-xs">
                            <thead>
                              <tr className="bg-gray-100">
                                {Object.keys(hasRawData.sample_rows[0] || {}).map(key => (
                                  <th key={key} className="px-2 py-1 text-left font-medium text-gray-700">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {hasRawData.sample_rows.slice(0, 5).map((row, rowIndex) => (
                                <tr key={rowIndex} className="border-t">
                                  {Object.values(row).map((value, colIndex) => (
                                    <td key={colIndex} className="px-2 py-1 text-gray-600">
                                      {String(value)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                          {hasRawData.sample_rows.length > 5 && (
                            <p className="text-xs text-gray-500 mt-2">
                              ... and {hasRawData.sample_rows.length - 5} more rows
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t p-4 bg-gray-50">
          <p className="text-xs text-gray-600">
            This provenance information ensures full traceability from question to source data. 
            All queries are logged for audit purposes.
          </p>
        </div>
      </div>
    </div>
  );
};