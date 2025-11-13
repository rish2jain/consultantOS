'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { monitoringAPI } from '@/lib/api';
import { MetricCard, AlertCard, MonitorRow } from '@/app/components';
import { Activity, AlertCircle, CheckCircle2, Clock } from 'lucide-react';

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
  const router = useRouter();
  const loadInFlightRef = useRef(false);
  const isMountedRef = useRef(true);
  const hasLoadedRef = useRef(false);

  const loadDashboardData = useCallback(
    async ({ force = false }: { force?: boolean } = {}) => {
      if (loadInFlightRef.current) return;
      loadInFlightRef.current = true;

      if ((force || !hasLoadedRef.current) && isMountedRef.current) {
        setLoading(true);
      }

      try {
        const [monitorResponse, statsResponse] = await Promise.all([
          monitoringAPI.list(),
          monitoringAPI.getDashboardStats().catch(() => null),
        ]);

        if (!isMountedRef.current) return;

        const monitorList: Monitor[] = monitorResponse?.monitors ?? [];
        setMonitors(monitorList);

        if (statsResponse) {
          setStats(statsResponse);
        }

        if (monitorList.length > 0) {
          const alertsMatrix = await Promise.all(
            monitorList.map((monitor) =>
              monitoringAPI
                .listAlerts(monitor.id, 5)
                .then((res) => res.alerts || [])
                .catch(() => [])
            )
          );

          if (isMountedRef.current) {
            const flattened = alertsMatrix.flat();
            flattened.sort(
              (a, b) =>
                new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );
            setRecentAlerts(flattened.slice(0, 10));
          }
        } else if (isMountedRef.current) {
          setRecentAlerts([]);
        }

        if (isMountedRef.current) {
          setError(null);
        }
      } catch (err) {
        if (isMountedRef.current) {
          setError(
            err instanceof Error ? err.message : 'Failed to load dashboard'
          );
          setRecentAlerts([]);
        }
      } finally {
        hasLoadedRef.current = true;
        if (isMountedRef.current) {
          setLoading(false);
        }
        loadInFlightRef.current = false;
      }
    },
    []
  );

  // Load dashboard data
  useEffect(() => {
    isMountedRef.current = true;
    loadDashboardData({ force: true });

    // Refresh every 30 seconds
    const interval = setInterval(() => loadDashboardData(), 30000);
    return () => {
      isMountedRef.current = false;
      clearInterval(interval);
    };
  }, [loadDashboardData]);

  async function handleManualCheck(monitorId: string) {
    try {
      await monitoringAPI.runManualCheck(monitorId);
      await loadDashboardData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to check monitor');
    }
  }

  async function handleMarkAlertRead(alertId: string) {
    try {
      await monitoringAPI.markAlertRead(alertId);

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
      await monitoringAPI.updateMonitorStatus(monitorId, 'paused');
      await loadDashboardData({ force: true });
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to pause monitor');
    }
  }

  async function handleResumeMonitor(monitorId: string) {
    try {
      await monitoringAPI.updateMonitorStatus(monitorId, 'active');
      await loadDashboardData({ force: true });
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
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
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Stats Overview */}
        {stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          >
            <MetricCard
              title="Total Monitors"
              value={stats.total_monitors}
              icon={<Activity className="w-6 h-6" />}
              color="blue"
              trend="neutral"
            />
            <MetricCard
              title="Active Monitors"
              value={stats.active_monitors}
              icon={<CheckCircle2 className="w-6 h-6" />}
              color="green"
              trend="up"
              trendValue={`${stats.active_monitors}/${stats.total_monitors}`}
            />
            <MetricCard
              title="Unread Alerts"
              value={stats.unread_alerts}
              icon={<AlertCircle className="w-6 h-6" />}
              color="orange"
              trend={stats.unread_alerts > 0 ? 'up' : 'neutral'}
              subtitle={stats.unread_alerts > 0 ? 'Requires attention' : 'All caught up'}
            />
            <MetricCard
              title="Alerts (24h)"
              value={stats.total_alerts_24h}
              icon={<Clock className="w-6 h-6" />}
              color="blue"
              trend="neutral"
            />
          </motion.div>
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

              <div>
                {monitors.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="px-6 py-12 text-center"
                  >
                    <p className="text-gray-500 mb-4">
                      No monitors yet. Create your first monitor to start
                      tracking companies.
                    </p>
                    <button
                      onClick={() => router.push('/monitors/new')}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Create Monitor
                    </button>
                  </motion.div>
                ) : (
                  monitors.map((monitor, index) => (
                    <MonitorRow
                      key={monitor.id}
                      monitor={monitor}
                      onPause={() => handlePauseMonitor(monitor.id)}
                      onResume={() => handleResumeMonitor(monitor.id)}
                      onCheckNow={() => handleManualCheck(monitor.id)}
                    />
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

              <div className="max-h-[600px] overflow-y-auto p-4 space-y-3">
                {recentAlerts.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="px-6 py-8 text-center text-gray-500"
                  >
                    No alerts yet
                  </motion.div>
                ) : (
                  recentAlerts.map((alert, index) => (
                    <motion.div
                      key={alert.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <AlertCard
                        title={alert.title}
                        summary={alert.summary}
                        severity={
                          alert.confidence > 0.8
                            ? 'critical'
                            : alert.confidence > 0.6
                            ? 'warning'
                            : 'info'
                        }
                        confidence={alert.confidence}
                        timestamp={alert.created_at}
                        unread={!alert.read}
                        changes={alert.changes_detected}
                        sourceUrls={alert.changes_detected?.[0]?.source_urls}
                        onMarkRead={() => handleMarkAlertRead(alert.id)}
                        expandable={true}
                      />
                    </motion.div>
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
