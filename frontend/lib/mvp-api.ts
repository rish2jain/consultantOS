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
      const error = await response.json();
      throw new Error(error.detail || 'Forecast request failed');
    }

    return await response.json();
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
