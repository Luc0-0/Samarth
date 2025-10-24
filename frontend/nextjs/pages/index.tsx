/**
 * Main Chat Interface for Project Samarth
 * Production-ready Q&A interface with provenance tracking
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, BarChart3, TrendingUp, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { apiClient, QuestionResponse } from '../lib/api';
import { CitationPanel } from '../components/CitationPanel';
import { ProvenanceModal } from '../components/ProvenanceModal';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  response?: QuestionResponse;
  timestamp: Date;
}

const SAMPLE_QUESTIONS = [
  "Compare the average annual rainfall in Maharashtra and Punjab",
  "What are the current crop prices in Maharashtra?", 
  "Show me latest market rates for Punjab",
  "Which state has the highest rice production?",
  "Analyze the production trend of cotton from 2010 to 2014"
];

const LIVE_KEYWORDS = ['current', 'latest', 'recent', 'live', 'today', 'now', 'market', 'price'];

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showProvenance, setShowProvenance] = useState(false);
  const [selectedResponse, setSelectedResponse] = useState<QuestionResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.askQuestion(input.trim());
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer_text,
        response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'I apologize, but I encountered an error processing your question. Please try again.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSampleQuestion = (question: string) => {
    setInput(question);
  };

  const openProvenance = (response: QuestionResponse) => {
    setSelectedResponse(response);
    setShowProvenance(true);
  };

  const renderChart = (response: QuestionResponse) => {
    if (!response.structured_results || response.structured_results.length === 0) return null;
    
    const queryType = response.processing_info.query_type;
    
    if (queryType === 'trend' && response.structured_results[0]?.year) {
      const chartData = response.structured_results.map(row => ({
        year: row.year,
        value: row.avg_value || row.value || 0
      }));

      return (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2" />
            Trend Analysis
          </h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            🌾 Project Samarth
            <span className="ml-3 text-sm font-normal text-gray-600">
              Intelligent Q&A for Indian Agriculture
            </span>
            <span className="ml-3 px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
              LIVE API
            </span>
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        {/* Sample Questions */}
        {messages.length === 0 && (
          <div className="mb-8">
            <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
              <h2 className="text-lg font-semibold text-gray-800 mb-2 flex items-center">
                ⚡ Live Data Integration Active
              </h2>
              <p className="text-sm text-gray-600">
                System automatically fetches <strong>real-time data</strong> from data.gov.in API for current queries, 
                and uses historical data for trend analysis.
              </p>
            </div>
            
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Try these sample questions:</h2>
            <div className="grid gap-3 md:grid-cols-2">
              {SAMPLE_QUESTIONS.map((question, index) => {
                const isLive = LIVE_KEYWORDS.some(keyword => question.toLowerCase().includes(keyword));
                return (
                  <button
                    key={index}
                    onClick={() => handleSampleQuestion(question)}
                    className={`p-3 text-left rounded-lg border transition-colors ${
                      isLive 
                        ? 'bg-green-50 border-green-200 hover:border-green-300 hover:bg-green-100'
                        : 'bg-white hover:border-blue-300 hover:bg-blue-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <span className="text-sm text-gray-700">{question}</span>
                      {isLive && (
                        <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                          LIVE
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="space-y-6 mb-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-lg px-4 py-3 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border shadow-sm'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Data Source Indicator */}
                {message.response && (
                  <div className="mt-2 flex items-center text-xs text-gray-500">
                    {message.response.processing_info.query_type === 'current' ? (
                      <span className="flex items-center px-2 py-1 bg-green-100 text-green-700 rounded-full">
                        ⚡ Live API Data
                      </span>
                    ) : (
                      <span className="flex items-center px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                        📈 Historical Data
                      </span>
                    )}
                  </div>
                )}
                
                {/* Structured Results */}
                {message.response?.structured_results && message.response.structured_results.length > 0 && (
                  <div className="mt-4 p-3 bg-gray-50 rounded border">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Data Results ({message.response.structured_results.length} records)
                    </h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full text-sm">
                        <thead>
                          <tr className="bg-gray-100">
                            {Object.keys(message.response.structured_results[0]).map(key => (
                              <th key={key} className="px-2 py-1 text-left font-medium text-gray-700">
                                {key.replace('_', ' ').toUpperCase()}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {message.response.structured_results.slice(0, 10).map((row, index) => (
                            <tr key={index} className="border-t">
                              {Object.values(row).map((value, colIndex) => (
                                <td key={colIndex} className="px-2 py-1 text-gray-600">
                                  {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {message.response.structured_results.length > 10 && (
                        <p className="text-xs text-gray-500 mt-2">
                          ... and {message.response.structured_results.length - 10} more rows
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Chart */}
                {message.response && renderChart(message.response)}

                {/* Citations */}
                {message.response?.citations && (
                  <CitationPanel
                    citations={message.response.citations}
                    onShowProvenance={() => openProvenance(message.response!)}
                    processingTime={message.response.processing_info.processing_time_ms}
                  />
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm rounded-lg px-4 py-3">
              <div className="flex items-center text-gray-600">
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing your question...
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex justify-start">
            <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3">
              <div className="flex items-center text-red-700">
                <AlertCircle className="w-4 h-4 mr-2" />
                {error}
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Input Form */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="flex space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about Indian agriculture and climate data..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Provenance Modal */}
      {selectedResponse && (
        <ProvenanceModal
          isOpen={showProvenance}
          onClose={() => setShowProvenance(false)}
          provenance={selectedResponse.provenance}
          requestId={selectedResponse.request_id}
        />
      )}
    </div>
  );
}