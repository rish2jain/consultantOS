/**
 * MVP API Client for ConsultantOS Hackathon Demo
 * Handles chat and forecast API calls
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  timestamp: string;
}

export interface ForecastData {
  dates: string[];
  predictions: number[];
  lower_bound: number[];
  upper_bound: number[];
  confidence: number;
}

// Backend response structure
interface ForecastPrediction {
  date: string;
  value: number;
  lower_bound: number;
  upper_bound: number;
}

interface ForecastResult {
  metric_name: string;
  predictions: ForecastPrediction[];
  confidence_level: number;
  generated_at: string;
}

/**
 * Send a chat message to the MVP backend
 */
export async function chatApi(
  query: string,
  conversationId?: string
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/mvp/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        conversation_id: conversationId || `conv_${Date.now()}`,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Chat request failed');
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Chat API error: ${error.message}`);
    }
    throw new Error('Unknown chat API error');
  }
}

/**
 * Fetch forecast data from MVP backend
 */
export async function forecastApi(periods: number = 30): Promise<ForecastData> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/mvp/forecast?periods=${periods}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      let errorMessage = 'Forecast request failed';
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch {
        errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    let data;
    try {
      data = await response.json();
    } catch (parseError) {
      throw new Error('Failed to parse forecast response as JSON');
    }
    
    // Validate response structure
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid forecast response: response is not an object');
    }
    
    // Transform backend response to frontend format
    // Backend returns: { predictions: [{ date, value, lower_bound, upper_bound }], confidence_level, ... }
    // Frontend expects: { dates: string[], predictions: number[], lower_bound: number[], upper_bound: number[], confidence: number }
    if (!data.predictions || !Array.isArray(data.predictions) || data.predictions.length === 0) {
      console.error('Invalid forecast response:', data);
      throw new Error('Invalid forecast response: predictions array is missing or empty');
    }

    // Validate each prediction object
    const validPredictions = data.predictions.filter((p: any) => 
      p && 
      typeof p === 'object' && 
      typeof p.date === 'string' && 
      typeof p.value === 'number' && 
      typeof p.lower_bound === 'number' && 
      typeof p.upper_bound === 'number'
    );

    if (validPredictions.length === 0) {
      console.error('No valid predictions found:', data.predictions);
      throw new Error('Invalid forecast response: no valid prediction objects found');
    }

    const transformed: ForecastData = {
      dates: validPredictions.map((p: any) => p.date),
      predictions: validPredictions.map((p: any) => p.value),
      lower_bound: validPredictions.map((p: any) => p.lower_bound),
      upper_bound: validPredictions.map((p: any) => p.upper_bound),
      confidence: (data.confidence_level || 0.95) * 100, // Convert 0.95 to 95
    };

    return transformed;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Forecast API error: ${error.message}`);
    }
    throw new Error('Unknown forecast API error');
  }
}

/**
 * Health check for MVP backend
 */
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/mvp/health`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return await response.json();
  } catch (error) {
    throw new Error('Backend is not available');
  }
}
