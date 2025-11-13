'use client';

/**
 * Interactive Dashboard Component
 *
 * Real-time dashboard with WebSocket updates, interactive charts,
 * and responsive grid layout.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWebSocket } from '@/app/hooks/useWebSocket';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Badge } from '@/app/components/ui/badge';
import { Button } from '@/app/components/ui/button';
import { MetricCard } from '@/app/components';
import { RefreshCw, Download, Settings } from 'lucide-react';
import { getApiKey } from '@/lib/auth';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface DashboardProps {
  dashboardId: string;
  apiUrl?: string;
}

interface DashboardData {
  id: string;
  company: string;
  industry: string;
  last_updated: string;
  sections: DashboardSection[];
  alerts: Alert[];
  metrics: Metric[];
}

interface DashboardSection {
  id: string;
  title: string;
  type: string;
  data: any;
  last_updated: string;
  size: string;
  order: number;
}

interface Alert {
  id: string;
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  timestamp: string;
  action_required: boolean;
}

interface Metric {
  id: string;
  name: string;
  value: number;
  unit: string;
  change: number;
  trend: 'up' | 'down' | 'stable';
  confidence: number;
}

export function InteractiveDashboard({ dashboardId, apiUrl = '/api' }: DashboardProps) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(() => getApiKey());
  const apiKeyRef = useRef(apiKey);

  useEffect(() => {
    apiKeyRef.current = apiKey;
  }, [apiKey]);

  const resolveHeaders = useCallback(() => {
    const key = getApiKey();
    if (key !== apiKeyRef.current) {
      apiKeyRef.current = key;
      setApiKey(key);
    }
    return {
      'Content-Type': 'application/json',
      ...(key ? { 'X-API-Key': key } : {}),
    };
  }, []);

  // WebSocket connection for real-time updates
  const wsPath = apiKey
    ? `/dashboards/${dashboardId}/ws?api_key=${encodeURIComponent(apiKey)}`
    : null;

  const { isConnected } = useWebSocket(
    wsPath,
    {
      onMessage: (message) => {
        if (message.type === 'initial' || message.type === 'update') {
          setData(message.data);
        } else if (message.type === 'metric') {
          // Update specific metric
          updateMetric(message.data);
        } else if (message.type === 'alert') {
          // Add new alert
          addAlert(message.data);
        }
      },
      onOpen: () => {
        console.log('Dashboard WebSocket connected');
      },
      onError: (error) => {
        console.error('Dashboard WebSocket error:', error);
        setError('Connection error - retrying...');
      },
    }
  );

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/dashboards/${dashboardId}`, {
        headers: resolveHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch dashboard');
      const dashboardData = await response.json();
      setData(dashboardData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }, [apiUrl, dashboardId, resolveHeaders]);

  // Fetch initial dashboard data
  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const refreshDashboard = async () => {
    try {
      const response = await fetch(`${apiUrl}/dashboards/${dashboardId}/refresh`, {
        method: 'POST',
        headers: resolveHeaders(),
      });
      if (!response.ok) throw new Error('Failed to refresh dashboard');
      const dashboardData = await response.json();
      setData(dashboardData);
    } catch (err) {
      console.error('Refresh error:', err);
    }
  };

  const updateMetric = (metricUpdate: any) => {
    if (!data) return;
    const updatedMetrics = data.metrics.map((m) =>
      m.id === metricUpdate.id ? metricUpdate : m
    );
    setData({ ...data, metrics: updatedMetrics });
  };

  const addAlert = (alert: Alert) => {
    if (!data) return;
    setData({ ...data, alerts: [alert, ...data.alerts].slice(0, 10) });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Dashboard</h3>
        <p className="text-red-600">{error || 'Dashboard not found'}</p>
        <Button onClick={fetchDashboard} className="mt-4">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Header */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{data.company}</h1>
          <p className="text-gray-600">{data.industry}</p>
          <p className="text-sm text-gray-500 mt-1">
            Last updated: {new Date(data.last_updated).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <motion.div
            animate={{
              scale: isConnected ? [1, 1.1, 1] : 1,
            }}
            transition={{
              duration: 2,
              repeat: isConnected ? Infinity : 0,
              repeatDelay: 1,
            }}
          >
            <Badge variant={isConnected ? 'default' : 'destructive'}>
              {isConnected ? 'Live' : 'Disconnected'}
            </Badge>
          </motion.div>
          <Button onClick={refreshDashboard} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </motion.div>

      {/* Key Metrics */}
      {data.metrics.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {data.metrics.map((metric, index) => (
            <motion.div
              key={metric.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <MetricCard
                title={metric.name}
                value={`${metric.value.toLocaleString()} ${metric.unit}`}
                trend={metric.trend}
                trendValue={`${Math.abs(metric.change).toFixed(1)}%`}
                subtitle={`${(metric.confidence * 100).toFixed(0)}% confidence`}
                color={
                  metric.trend === 'up' ? 'green' :
                  metric.trend === 'down' ? 'red' : 'blue'
                }
              />
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Alerts */}
      <AnimatePresence>
        {data.alerts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Critical Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {data.alerts.slice(0, 5).map((alert, index) => (
                    <motion.div
                      key={alert.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <AlertItem alert={alert} />
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Dashboard Sections */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        {data.sections
          .sort((a, b) => a.order - b.order)
          .map((section, index) => (
            <motion.div
              key={section.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <DashboardSectionComponent section={section} />
            </motion.div>
          ))}
      </motion.div>
    </motion.div>
  );
}

function AlertItem({ alert }: { alert: Alert }) {
  const severityColors = {
    info: 'bg-blue-50 border-blue-200 text-blue-900',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    critical: 'bg-red-50 border-red-200 text-red-900',
  };

  return (
    <div className={`border rounded-lg p-3 ${severityColors[alert.severity]}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-semibold text-sm">{alert.title}</h4>
          <p className="text-sm mt-1">{alert.message}</p>
          <p className="text-xs mt-2 opacity-75">
            {new Date(alert.timestamp).toLocaleString()}
          </p>
        </div>
        {alert.action_required && (
          <Badge variant="destructive" className="ml-2">
            Action Required
          </Badge>
        )}
      </div>
    </div>
  );
}

function DashboardSectionComponent({ section }: { section: DashboardSection }) {
  const sizeClasses = {
    small: 'col-span-1',
    medium: 'col-span-1',
    large: 'col-span-2',
    'full-width': 'col-span-2',
  };

  return (
    <Card className={sizeClasses[section.size as keyof typeof sizeClasses] || 'col-span-1'}>
      <CardHeader>
        <CardTitle>{section.title}</CardTitle>
        <p className="text-xs text-gray-500">
          Updated: {new Date(section.last_updated).toLocaleString()}
        </p>
      </CardHeader>
      <CardContent>
        <SectionContent section={section} />
      </CardContent>
    </Card>
  );
}

function SectionContent({ section }: { section: DashboardSection }) {
  if (section.type === 'chart' && section.data.chart_type) {
    return <ChartSection data={section.data} />;
  }

  if (section.type === 'table') {
    return <TableSection data={section.data} />;
  }

  if (section.type === 'metric') {
    return <div>Metrics section</div>;
  }

  return (
    <div className="text-gray-500">
      Section type "{section.type}" not yet implemented
    </div>
  );
}

function ChartSection({ data }: { data: any }) {
  if (!data.x || !data.y) {
    return <div className="text-gray-500">No chart data available</div>;
  }

  const plotData = [
    {
      x: data.x,
      y: data.y,
      type: data.chart_type === 'line' ? 'scatter' : data.chart_type,
      mode: data.chart_type === 'line' ? 'lines+markers' : undefined,
      marker: { color: '#3b82f6' },
    },
  ];

  const layout = {
    autosize: true,
    margin: { l: 40, r: 20, t: 20, b: 40 },
    xaxis: { title: data.labels?.x },
    yaxis: { title: data.labels?.y },
  };

  return (
    <Plot
      data={plotData}
      layout={layout}
      useResizeHandler
      style={{ width: '100%', height: '300px' }}
      config={{ displayModeBar: false, responsive: true }}
    />
  );
}

function TableSection({ data }: { data: any }) {
  if (!data.columns || !data.rows) {
    return <div className="text-gray-500">No table data available</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {data.columns.map((column: string) => (
              <th
                key={column}
                className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.rows.map((row: any, idx: number) => (
            <tr key={idx}>
              {data.columns.map((column: string) => (
                <td key={column} className="px-4 py-2 text-sm text-gray-900">
                  {row[column]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
