'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

// Types matching backend models
interface MonitoringConfig {
  frequency: 'hourly' | 'daily' | 'weekly' | 'monthly';
  frameworks: string[];
  alert_threshold: number;
  notification_channels: string[];
  keywords?: string[];
  competitors?: string[];
}

interface Monitor {
  id: string;
  user_id: string;
  company: string;
  industry: string;
  config: MonitoringConfig;
  status: 'active' | 'paused' | 'deleted' | 'error';
  created_at: string;
  last_check?: string;
  next_check?: string;
  last_alert_id?: string;
  total_alerts: number;
  error_count: number;
  last_error?: string;
}

interface Change {
  change_type: string;
  title: string;
  description: string;
  confidence: number;
  source_urls?: string[];
  detected_at: string;
  previous_value?: string;
  current_value?: string;
}

interface Alert {
  id: string;
  monitor_id: string;
  title: string;
  summary: string;
  confidence: number;
  changes_detected: Change[];
  created_at: string;
  read: boolean;
  read_at?: string;
  user_feedback?: string;
  action_taken?: string;
}

interface MonitoringStats {
  total_monitors: number;
  active_monitors: number;
  paused_monitors: number;
  total_alerts_24h: number;
  unread_alerts: number;
  avg_alert_confidence: number;
  top_change_types: [string, number][];
}

export default function DashboardPage() {
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<MonitoringStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMonitor, setSelectedMonitor] = useState<Monitor | null>(null);
  const router = useRouter();

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  // Load dashboard data
  useEffect(() => {
    loadDashboardData();

    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  async function loadDashboardData() {
    try {
      setLoading(true);

      // Load monitors
      const monitorsRes = await fetch(`${API_URL}/monitors`, {
        headers: {
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
      });

      if (!monitorsRes.ok) {
        throw new Error('Failed to load monitors');
      }

      const monitorsData = await monitorsRes.json();
      setMonitors(monitorsData.monitors || []);

      // Load stats
      const statsRes = await fetch(`${API_URL}/monitors/stats/dashboard`, {
        headers: {
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
      });

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }

      // Load recent alerts - use batch endpoint if available, otherwise concurrent fetches
      if (monitorsData.monitors && monitorsData.monitors.length > 0) {
        try {
          // Preferred: Use batch endpoint for better performance
          const batchRes = await fetch(
            `${API_URL}/monitors/alerts/recent?limit=10`,
            {
              headers: {
                'X-API-Key': localStorage.getItem('api_key') || '',
              },
            }
          );

          if (batchRes.ok) {
            const batchData = await batchRes.json();
            setRecentAlerts(batchData.alerts || []);
          } else {
            // Fallback: Concurrent fetches for all monitors (not just first 5)
            const apiKey = localStorage.getItem('api_key') || '';
            const alertPromises = monitorsData.monitors.map((monitor: Monitor) =>
              fetch(`${API_URL}/monitors/${monitor.id}/alerts?limit=5`, {
                headers: { 'X-API-Key': apiKey },
              })
                .then(async (res) => {
                  if (!res.ok) return [];
                  const data = await res.json();
                  return data.alerts || [];
                })
                .catch(() => []) // Return empty array on error
            );

            // Fetch all alerts concurrently
            const alertResults = await Promise.all(alertPromises);
            const allAlerts: Alert[] = alertResults.flat();

            // Sort by created_at descending and limit to 10 most recent
            allAlerts.sort(
              (a, b) =>
                new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );

            setRecentAlerts(allAlerts.slice(0, 10));
          }
        } catch (err) {
          // Silently fail - alerts are not critical for dashboard load
          console.error('Failed to load alerts:', err);
          setRecentAlerts([]);
        }
      }

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }

  async function handleManualCheck(monitorId: string) {
    try {
      const res = await fetch(`${API_URL}/monitors/${monitorId}/check`, {
        method: 'POST',
        headers: {
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
      });

      if (!res.ok) {
        throw new Error('Failed to trigger check');
      }

      // Refresh dashboard
      await loadDashboardData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to check monitor');
    }
  }

  async function handleMarkAlertRead(alertId: string) {
    try {
      const res = await fetch(`${API_URL}/monitors/alerts/${alertId}/read`, {
        method: 'POST',
        headers: {
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
      });

      if (!res.ok) {
        throw new Error('Failed to mark as read');
      }

      // Update local state
      setRecentAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, read: true } : a))
      );
    } catch (err) {
      console.error('Failed to mark alert as read:', err);
    }
  }

  async function handlePauseMonitor(monitorId: string) {
    try {
      const res = await fetch(`${API_URL}/monitors/${monitorId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
        body: JSON.stringify({ status: 'paused' }),
      });

      if (!res.ok) {
        throw new Error('Failed to pause monitor');
      }

      await loadDashboardData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to pause monitor');
    }
  }

  async function handleResumeMonitor(monitorId: string) {
    try {
      const res = await fetch(`${API_URL}/monitors/${monitorId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
        body: JSON.stringify({ status: 'active' }),
      });

      if (!res.ok) {
        throw new Error('Failed to resume monitor');
      }

      await loadDashboardData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to resume monitor');
    }
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  }

  if (loading && monitors.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              Intelligence Dashboard
            </h1>
            <button
              onClick={() => router.push('/monitors/new')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              + New Monitor
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Total Monitors</div>
              <div className="text-3xl font-bold text-gray-900 mt-2">
                {stats.total_monitors}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Active Monitors</div>
              <div className="text-3xl font-bold text-green-600 mt-2">
                {stats.active_monitors}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Unread Alerts</div>
              <div className="text-3xl font-bold text-orange-600 mt-2">
                {stats.unread_alerts}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Alerts (24h)</div>
              <div className="text-3xl font-bold text-blue-600 mt-2">
                {stats.total_alerts_24h}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Active Monitors */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">
                  Active Monitors
                </h2>
              </div>

              <div className="divide-y divide-gray-200">
                {monitors.length === 0 ? (
                  <div className="px-6 py-12 text-center">
                    <p className="text-gray-500">
                      No monitors yet. Create your first monitor to start
                      tracking companies.
                    </p>
                    <button
                      onClick={() => router.push('/monitors/new')}
                      className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                    >
                      Create Monitor
                    </button>
                  </div>
                ) : (
                  monitors.map((monitor) => (
                    <div key={monitor.id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <h3 className="text-lg font-medium text-gray-900">
                              {monitor.company}
                            </h3>
                            <span
                              className={`px-2 py-1 text-xs rounded-full ${
                                monitor.status === 'active'
                                  ? 'bg-green-100 text-green-800'
                                  : monitor.status === 'paused'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {monitor.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1">
                            {monitor.industry}
                          </p>

                          <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
                            <span>
                              {monitor.config.frequency} checks
                            </span>
                            <span>
                              {monitor.total_alerts} alerts
                            </span>
                            {monitor.last_check && (
                              <span>
                                Last check: {formatDate(monitor.last_check)}
                              </span>
                            )}
                          </div>

                          {monitor.error_count > 0 && monitor.last_error && (
                            <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                              {monitor.last_error}
                            </div>
                          )}
                        </div>

                        <div className="flex gap-2 ml-4">
                          <button
                            onClick={() => handleManualCheck(monitor.id)}
                            className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                          >
                            Check Now
                          </button>

                          {monitor.status === 'active' ? (
                            <button
                              onClick={() => handlePauseMonitor(monitor.id)}
                              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                            >
                              Pause
                            </button>
                          ) : (
                            <button
                              onClick={() => handleResumeMonitor(monitor.id)}
                              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                            >
                              Resume
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Recent Alerts */}
          <div>
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">
                  Recent Alerts
                </h2>
              </div>

              <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
                {recentAlerts.length === 0 ? (
                  <div className="px-6 py-8 text-center text-gray-500">
                    No alerts yet
                  </div>
                ) : (
                  recentAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`px-6 py-4 hover:bg-gray-50 cursor-pointer ${
                        !alert.read ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => handleMarkAlertRead(alert.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900">
                            {alert.title}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {alert.summary}
                          </p>

                          <div className="mt-2 flex items-center gap-3">
                            <span className="text-xs text-gray-500">
                              {formatDate(alert.created_at)}
                            </span>
                            <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                              {(alert.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                        </div>

                        {!alert.read && (
                          <div className="w-2 h-2 bg-blue-600 rounded-full ml-2"></div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
