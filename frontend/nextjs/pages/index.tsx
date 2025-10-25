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
        <div className="mt-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border border-blue-200/50 shadow-lg">
          <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
            Trend Analysis
          </h4>
          <div className="h-80 bg-white/50 rounded-xl p-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="year" 
                  stroke="#64748b"
                  fontSize={12}
                  fontWeight={500}
                />
                <YAxis 
                  stroke="#64748b"
                  fontSize={12}
                  fontWeight={500}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="url(#colorGradient)" 
                  strokeWidth={3}
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
                />
                <defs>
                  <linearGradient id="colorGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#6366f1" />
                  </linearGradient>
                </defs>
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                🌾
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  Project Samarth
                </h1>
                <p className="text-sm text-gray-600 font-medium">
                  Intelligent Q&A for Indian Agriculture
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full shadow-md">
                ⚡ LIVE API
              </span>
              <span className="px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full shadow-md">
                PRODUCTION
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Sample Questions */}
        {messages.length === 0 && (
          <div className="mb-8">
            <div className="mb-8 p-6 bg-gradient-to-r from-emerald-50 via-blue-50 to-indigo-50 rounded-2xl border border-emerald-200/50 shadow-lg backdrop-blur-sm">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-xl flex items-center justify-center text-white text-lg shadow-md">
                  ⚡
                </div>
                <h2 className="text-xl font-bold bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent">
                  Live Data Integration Active
                </h2>
              </div>
              <p className="text-gray-700 leading-relaxed">
                System automatically fetches <span className="font-semibold text-emerald-700">real-time data</span> from data.gov.in API for current queries, 
                and uses <span className="font-semibold text-blue-700">historical data</span> for trend analysis.
              </p>
            </div>
            
            <h2 className="text-xl font-bold text-gray-800 mb-6">Try these sample questions:</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {SAMPLE_QUESTIONS.map((question, index) => {
                const isLive = LIVE_KEYWORDS.some(keyword => question.toLowerCase().includes(keyword));
                return (
                  <button
                    key={index}
                    onClick={() => handleSampleQuestion(question)}
                    className={`p-4 text-left rounded-xl border transition-all duration-300 transform hover:scale-[1.02] hover:shadow-lg ${
                      isLive 
                        ? 'bg-gradient-to-br from-emerald-50 to-green-50 border-emerald-200 hover:border-emerald-300 hover:shadow-emerald-200/50'
                        : 'bg-white/70 backdrop-blur-sm border-gray-200 hover:border-blue-300 hover:shadow-blue-200/50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <span className="text-sm text-gray-700">{question}</span>
                      {isLive && (
                        <span className="ml-2 px-2.5 py-1 text-xs font-semibold bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-full shadow-md">
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
        <div className="space-y-8 mb-8">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-4xl rounded-2xl px-6 py-4 shadow-lg ${
                  message.type === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-blue-200/50'
                    : 'bg-white/80 backdrop-blur-md border border-gray-200/50 shadow-gray-200/50'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Data Source Indicator */}
                {message.response && (
                  <div className="mt-3 flex items-center">
                    {message.response.processing_info.query_type === 'current' ? (
                      <span className="flex items-center px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-full shadow-md">
                        ⚡ Live API Data
                      </span>
                    ) : (
                      <span className="flex items-center px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full shadow-md">
                        📈 Historical Data
                      </span>
                    )}
                  </div>
                )}
                
                {/* Structured Results */}
                {message.response?.structured_results && message.response.structured_results.length > 0 && (
                  <div className="mt-6 p-4 bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-xl border border-gray-200/50 shadow-inner">
                    <h4 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                      <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
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
                {message.response && (
                  <div className="mt-4">
                    {renderChart(message.response)}
                  </div>
                )}

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
            <div className="bg-white/80 backdrop-blur-md border border-gray-200/50 shadow-lg rounded-2xl px-6 py-4">
              <div className="flex items-center text-gray-700">
                <Loader2 className="w-5 h-5 mr-3 animate-spin text-blue-600" />
                <span className="font-medium">Processing your question...</span>
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
      <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-gray-200/50 shadow-2xl">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about Indian agriculture and climate data..."
                className="w-full px-6 py-4 text-lg border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/80 backdrop-blur-sm shadow-lg transition-all duration-300"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center shadow-lg transition-all duration-300 transform hover:scale-105 disabled:hover:scale-100"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
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