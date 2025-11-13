/**
 * API Integration for Strategic Intelligence Features
 * Handles data fetching, WebSocket connections, and real-time updates
 */

import {
  StrategicIntelligenceOverview,
  LiveIntelligenceUpdate,
  IntelligenceFeedData,
  SystemDynamicsData,
  FlywheelVelocity,
} from '@/types/strategic-intelligence';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://consultantos-api-187550875653.us-central1.run.app'
    : 'http://localhost:8080');
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 
  (process.env.NODE_ENV === 'production'
    ? 'wss://consultantos-api-187550875653.us-central1.run.app'
    : 'ws://localhost:8080');

// ============================================================================
// API Client Configuration
// ============================================================================

interface FetchOptions extends RequestInit {
  timeout?: number;
}

async function fetchWithTimeout(
  url: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { timeout = 30000, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout');
    }
    throw error;
  }
}

// ============================================================================
// Strategic Intelligence API
// ============================================================================

export class StrategicIntelligenceAPI {
  private static apiKey: string | null = null;

  static setApiKey(key: string) {
    this.apiKey = key;
  }

  private static getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    return headers;
  }

  /**
   * Fetch complete strategic intelligence overview
   */
  static async fetchOverview(
    company: string,
    industry?: string
  ): Promise<StrategicIntelligenceOverview> {
    const params = new URLSearchParams({ company });
    if (industry) params.append('industry', industry);

    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/strategic-intelligence/overview?${params}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    return response.json();
  }

  /**
   * Fetch system dynamics data only
   */
  static async fetchSystemDynamics(
    company: string
  ): Promise<SystemDynamicsData> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/strategic-intelligence/dynamics/${company}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    return response.json();
  }

  /**
   * Fetch flywheel velocity data only
   */
  static async fetchFlywheelVelocity(
    company: string
  ): Promise<FlywheelVelocity> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/strategic-intelligence/flywheel/${company}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    return response.json();
  }

  /**
   * Fetch intelligence feed
   */
  static async fetchIntelligenceFeed(
    company: string,
    filters?: string[]
  ): Promise<IntelligenceFeedData> {
    const params = new URLSearchParams({ company });
    if (filters && filters.length > 0) {
      params.append('filters', filters.join(','));
    }

    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/strategic-intelligence/feed?${params}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    return response.json();
  }

  /**
   * Mark intelligence card as read
   */
  static async markCardAsRead(cardId: string): Promise<void> {
    await fetchWithTimeout(
      `${API_BASE_URL}/api/strategic-intelligence/feed/${cardId}/read`,
      {
        method: 'POST',
        headers: this.getHeaders(),
      }
    );
  }

  /**
   * Handle decision action
   */
  static async handleDecision(
    decisionId: string,
    action: 'accept' | 'reject' | 'defer',
    optionId?: string
  ): Promise<void> {
    await fetchWithTimeout(
      `${API_BASE_URL}/api/strategic-intelligence/decisions/${decisionId}`,
      {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ action, option_id: optionId }),
      }
    );
  }

  /**
   * Trigger refresh of strategic intelligence data
   */
  static async refreshAnalysis(company: string): Promise<void> {
    await fetchWithTimeout(
      `${API_BASE_URL}/api/strategic-intelligence/refresh`,
      {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ company }),
        timeout: 60000, // 60 seconds for refresh
      }
    );
  }

  /**
   * Export strategic intelligence data
   */
  static async exportData(
    company: string,
    format: 'pdf' | 'excel' | 'json'
  ): Promise<Blob> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/strategic-intelligence/export/${company}?format=${format}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    return response.blob();
  }
}

// ============================================================================
// WebSocket Real-time Updates
// ============================================================================

export class IntelligenceFeedWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isIntentionallyClosed = false;

  constructor(
    private company: string,
    private onUpdate: (update: LiveIntelligenceUpdate) => void,
    private onError?: (error: Error) => void,
    private onConnect?: () => void,
    private onDisconnect?: () => void
  ) {}

  connect() {
    this.isIntentionallyClosed = false;
    this.ws = new WebSocket(
      `${WS_BASE_URL}/ws/strategic-intelligence/${this.company}`
    );

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.onConnect?.();
    };

    this.ws.onmessage = (event) => {
      try {
        const update: LiveIntelligenceUpdate = JSON.parse(event.data);
        this.onUpdate(update);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        this.onError?.(new Error('Invalid message format'));
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.onError?.(new Error('WebSocket connection error'));
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.onDisconnect?.();

      if (!this.isIntentionallyClosed && this.shouldReconnect()) {
        this.scheduleReconnect();
      }
    };
  }

  disconnect() {
    this.isIntentionallyClosed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.maxReconnectAttempts;
  }

  private scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(
      `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
    );

    setTimeout(() => {
      if (!this.isIntentionallyClosed) {
        this.connect();
      }
    }, delay);
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// ============================================================================
// React Hooks for API Integration
// ============================================================================

import { useState, useEffect, useCallback } from 'react';

/**
 * Hook for fetching strategic intelligence overview
 */
export function useStrategicIntelligence(company: string, industry?: string) {
  const [data, setData] = useState<StrategicIntelligenceOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const overview = await StrategicIntelligenceAPI.fetchOverview(
        company,
        industry
      );
      setData(overview);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, [company, industry]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refresh = useCallback(async () => {
    try {
      await StrategicIntelligenceAPI.refreshAnalysis(company);
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh data');
    }
  }, [company, fetchData]);

  return { data, loading, error, refresh };
}

/**
 * Hook for real-time intelligence feed
 */
export function useIntelligenceFeed(
  company: string,
  enableRealtime = false,
  filters?: string[]
) {
  const [feedData, setFeedData] = useState<IntelligenceFeedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let ws: IntelligenceFeedWebSocket | null = null;

    const fetchFeed = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await StrategicIntelligenceAPI.fetchIntelligenceFeed(
          company,
          filters
        );
        setFeedData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch feed');
      } finally {
        setLoading(false);
      }
    };

    fetchFeed();

    if (enableRealtime) {
      ws = new IntelligenceFeedWebSocket(
        company,
        (update) => {
          // Handle live updates
          if (update.type === 'new_card' && 'type' in update.data) {
            setFeedData((prev) =>
              prev
                ? {
                    ...prev,
                    cards: [update.data as any, ...prev.cards],
                    unread_count: prev.unread_count + 1,
                    last_updated: update.timestamp,
                  }
                : null
            );
          } else if (update.type === 'update_card') {
            // Handle card updates
            setFeedData((prev) =>
              prev
                ? {
                    ...prev,
                    cards: prev.cards.map((card) =>
                      card.id === (update.data as any).id
                        ? { ...card, ...(update.data as any) }
                        : card
                    ),
                    last_updated: update.timestamp,
                  }
                : null
            );
          } else if (update.type === 'delete_card') {
            setFeedData((prev) =>
              prev
                ? {
                    ...prev,
                    cards: prev.cards.filter(
                      (card) => card.id !== (update.data as any).card_id
                    ),
                    last_updated: update.timestamp,
                  }
                : null
            );
          }
        },
        (error) => setError(error.message),
        () => setConnected(true),
        () => setConnected(false)
      );

      ws.connect();
    }

    return () => {
      if (ws) {
        ws.disconnect();
      }
    };
  }, [company, enableRealtime, filters]);

  const markAsRead = useCallback(async (cardId: string) => {
    try {
      await StrategicIntelligenceAPI.markCardAsRead(cardId);
      setFeedData((prev) =>
        prev
          ? {
              ...prev,
              cards: prev.cards.map((card) =>
                card.id === cardId ? { ...card, read: true } : card
              ),
              unread_count: Math.max(0, prev.unread_count - 1),
            }
          : null
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark as read');
    }
  }, []);

  return { feedData, loading, error, connected, markAsRead };
}

/**
 * Hook for exporting data
 */
export function useExportData() {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportData = useCallback(
    async (company: string, format: 'pdf' | 'excel' | 'json') => {
      try {
        setExporting(true);
        setError(null);
        const blob = await StrategicIntelligenceAPI.exportData(company, format);

        // Trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `strategic-intelligence-${company}-${Date.now()}.${format === 'excel' ? 'xlsx' : format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Export failed');
      } finally {
        setExporting(false);
      }
    },
    []
  );

  return { exportData, exporting, error };
}
