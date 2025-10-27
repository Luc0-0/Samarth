/**
 * API client for Project Samarth backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface QuestionRequest {
  question: string;
}

export interface Citation {
  dataset_title: string;
  resource_url: string;
  search_url?: string;
  publisher: string;
  query_summary: string;
  status_badge?: string;
  status_description?: string;
  status_color?: string;
}

export interface ProvenanceData {
  datasets_used: Array<{
    dataset_title: string;
    resource_url: string;
    table_name: string;
    sample_endpoint: string;
  }>;
  sql_queries: string[];
  sample_data_available: boolean;
  audit_trail_id: string;
}

export interface QuestionResponse {
  request_id: string;
  answer_text: string;
  structured_results: any[];
  citations: Citation[];
  processing_info: {
    intent: any;
    sources_used: number;
    processing_time_ms: number;
    query_type: string;
  };
  provenance: ProvenanceData;
}

export interface RawDataResponse {
  dataset_id: string;
  dataset_title: string;
  resource_url: string;
  sample_rows: any[];
  total_sample_rows: number;
  query_used: string;
  timestamp: string;
}

class ApiClient {
  private async fetchWithRetry(
    url: string, 
    options: RequestInit = {}, 
    maxRetries = 3
  ): Promise<Response> {
    let lastError: Error;
    
    for (let i = 0; i <= maxRetries; i++) {
      try {
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            'X-Request-ID': crypto.randomUUID(),
            ...options.headers,
          },
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response;
      } catch (error) {
        lastError = error as Error;
        
        if (i < maxRetries) {
          // Exponential backoff: 1s, 2s, 4s
          const delay = Math.pow(2, i) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw lastError!;
  }

  async askQuestion(question: string): Promise<QuestionResponse> {
    const response = await this.fetchWithRetry(`${API_BASE}/ask`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
    
    return response.json();
  }

  async getRawData(datasetId: string): Promise<RawDataResponse> {
    const response = await this.fetchWithRetry(`${API_BASE}/raw/${datasetId}`);
    return response.json();
  }

  async getDatasets(): Promise<any> {
    const response = await this.fetchWithRetry(`${API_BASE}/datasets`);
    return response.json();
  }

  async getHealth(): Promise<any> {
    const response = await this.fetchWithRetry(`${API_BASE}/health`);
    return response.json();
  }
}

export const apiClient = new ApiClient();