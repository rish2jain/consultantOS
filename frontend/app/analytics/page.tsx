'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getApiKey } from '@/lib/auth';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  FunnelChart,
  Funnel,
  LabelList,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Clock,
  Users,
  FileText,
  Zap,
  AlertCircle,
  CheckCircle,
  XCircle,
  Activity,
  Calendar,
  Target,
  BarChart3,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon,
} from 'lucide-react';
import { Card } from '@/app/components/Card';
import { Button } from '@/app/components/Button';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// Color schemes
const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
const STATUS_COLORS = {
  completed: '#10b981',
  processing: '#3b82f6',
  pending: '#f59e0b',
  failed: '#ef4444',
  archived: '#6b7280',
};

interface ProductivityMetrics {
  period_days: number;
  reports_per_user: Record<string, number>;
  total_reports: number;
  templates_used: number;
  templates_created: number;
  template_adoption_rate: number;
  estimated_time_saved_hours: number;
  avg_batch_processing_time_seconds: number;
  total_batch_jobs: number;
}

interface BusinessMetrics {
  period_days: number;
  top_industries: Array<{ industry: string; count: number }>;
  most_used_frameworks: Array<{ framework: string; count: number }>;
  peak_usage_times: {
    by_hour: Record<number, number>;
    peak_hour: number | null;
  };
  user_adoption: {
    total_unique_users: number;
    new_users_this_period: number;
    users_by_date: Record<string, number>;
  };
}

interface DashboardAnalytics {
  period_days: number;
  report_status_pipeline: {
    submitted: number;
    processing: number;
    completed: number;
    archived: number;
    failed: number;
  };
  confidence_score_distribution: {
    mean: number;
    median: number;
    min: number;
    max: number;
    scores: number[];
  };
  analysis_type_breakdown: {
    quick: number;
    standard: number;
    deep: number;
  };
  industries_breakdown: Record<string, number>;
  job_queue_performance: {
    avg_wait_time_seconds: number;
    avg_processing_time_seconds: number;
    queue_length: number;
    throughput_per_hour: number;
  };
  framework_effectiveness: Record<string, Record<string, number>>;
  user_activity_calendar: Record<string, number>;
}

interface Insight {
  type: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  recommendation: string;
}

export default function AnalyticsPage() {
  const router = useRouter();
  const [productivity, setProductivity] = useState<ProductivityMetrics | null>(null);
  const [business, setBusiness] = useState<BusinessMetrics | null>(null);
  const [dashboard, setDashboard] = useState<DashboardAnalytics | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    loadAnalytics();
    // Auto-refresh every 60 seconds
    const interval = setInterval(loadAnalytics, 60000);
    return () => clearInterval(interval);
  }, [period]);

  async function loadAnalytics() {
    try {
      setLoading(true);
      const apiKey = getApiKey() || '';

      const [prodRes, busRes, dashRes, insightsRes] = await Promise.all([
        fetch(`${API_URL}/analytics/productivity?days=${period}`, {
          headers: { 'X-API-Key': apiKey },
        }),
        fetch(`${API_URL}/analytics/business?days=${period}`, {
          headers: { 'X-API-Key': apiKey },
        }),
        fetch(`${API_URL}/analytics/dashboard?days=${period}`, {
          headers: { 'X-API-Key': apiKey },
        }),
        fetch(`${API_URL}/analytics/insights?days=7`, {
          headers: { 'X-API-Key': apiKey },
        }),
      ]);

      if (!prodRes.ok || !busRes.ok || !dashRes.ok || !insightsRes.ok) {
        throw new Error('Failed to load analytics');
      }

      setProductivity(await prodRes.json());
      setBusiness(await busRes.json());
      setDashboard(await dashRes.json());
      const insightsData = await insightsRes.json();
      setInsights(insightsData.insights || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
      console.error('Analytics load error:', err);
    } finally {
      setLoading(false);
    }
  }

  // Prepare chart data
  const funnelData = dashboard
    ? [
        { name: 'Submitted', value: dashboard.report_status_pipeline.submitted, fill: STATUS_COLORS.pending },
        { name: 'Processing', value: dashboard.report_status_pipeline.processing, fill: STATUS_COLORS.processing },
        { name: 'Completed', value: dashboard.report_status_pipeline.completed, fill: STATUS_COLORS.completed },
        { name: 'Archived', value: dashboard.report_status_pipeline.archived, fill: STATUS_COLORS.archived },
        { name: 'Failed', value: dashboard.report_status_pipeline.failed, fill: STATUS_COLORS.failed },
      ]
    : [];

  const analysisTypeData = dashboard
    ? [
        { name: 'Quick', value: dashboard.analysis_type_breakdown.quick },
        { name: 'Standard', value: dashboard.analysis_type_breakdown.standard },
        { name: 'Deep', value: dashboard.analysis_type_breakdown.deep },
      ]
    : [];

  const industriesData = business
    ? business.top_industries.slice(0, 10).map((ind) => ({
        name: ind.industry,
        value: ind.count,
      }))
    : [];

  const frameworksData = business
    ? business.most_used_frameworks.slice(0, 10).map((fw) => ({
        name: fw.framework,
        value: fw.count,
      }))
    : [];

  const peakUsageData = business
    ? Object.entries(business.peak_usage_times.by_hour)
        .map(([hour, count]) => ({
          hour: `${hour}:00`,
          requests: count,
        }))
        .sort((a, b) => parseInt(a.hour) - parseInt(b.hour))
    : [];

  const confidenceDistribution = dashboard?.confidence_score_distribution.scores || [];
  const confidenceBins = Array.from({ length: 10 }, (_, i) => {
    const min = i * 0.1;
    const max = (i + 1) * 0.1;
    return {
      range: `${(min * 100).toFixed(0)}-${(max * 100).toFixed(0)}%`,
      count: confidenceDistribution.filter((s) => s >= min && s < max).length,
    };
  });

  if (loading && !productivity && !business && !dashboard) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Comprehensive insights into your ConsultantOS usage</p>
          </div>
          <div className="flex gap-2">
            <select
              value={period}
              onChange={(e) => setPeriod(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
            <Button onClick={loadAnalytics}>Refresh</Button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Quick Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4 cursor-pointer hover:shadow-lg transition" onClick={() => router.push('/analysis')}>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Zap className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Create Quick Analysis</p>
                <p className="text-xs text-gray-400">Fast path to new analysis</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 cursor-pointer hover:shadow-lg transition" onClick={() => router.push('/jobs')}>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">View Pending Reviews</p>
                <p className="text-xs text-gray-400">Reports needing attention</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 cursor-pointer hover:shadow-lg transition" onClick={() => router.push('/reports')}>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <FileText className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Export Latest Report</p>
                <p className="text-xs text-gray-400">Quick access to most recent</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 cursor-pointer hover:shadow-lg transition" onClick={() => router.push('/jobs')}>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Activity className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Check Job Status</p>
                <p className="text-xs text-gray-400">Monitor active processing</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Productivity Metrics */}
        {productivity && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Reports</p>
                  <p className="text-2xl font-bold text-gray-900">{productivity.total_reports}</p>
                </div>
                <FileText className="h-8 w-8 text-blue-600" />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Templates Used</p>
                  <p className="text-2xl font-bold text-gray-900">{productivity.templates_used}</p>
                  <p className="text-xs text-gray-500">
                    {productivity.template_adoption_rate > 0
                      ? `${(productivity.template_adoption_rate * 100).toFixed(1)}% adoption`
                      : 'No adoption data'}
                  </p>
                </div>
                <Target className="h-8 w-8 text-green-600" />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Time Saved</p>
                  <p className="text-2xl font-bold text-gray-900">{productivity.estimated_time_saved_hours.toFixed(1)}h</p>
                  <p className="text-xs text-gray-500">From templates</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Avg Processing</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {productivity.avg_batch_processing_time_seconds > 60
                      ? `${(productivity.avg_batch_processing_time_seconds / 60).toFixed(1)}m`
                      : `${productivity.avg_batch_processing_time_seconds.toFixed(0)}s`}
                  </p>
                </div>
                <Zap className="h-8 w-8 text-purple-600" />
              </div>
            </Card>
          </div>
        )}

        {/* AI Insights */}
        {insights.length > 0 && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-blue-600" />
              Intelligent Insights
            </h2>
            <div className="space-y-3">
              {insights.map((insight, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-l-4 ${
                    insight.severity === 'warning'
                      ? 'bg-yellow-50 border-yellow-400'
                      : insight.severity === 'error'
                      ? 'bg-red-50 border-red-400'
                      : 'bg-blue-50 border-blue-400'
                  }`}
                >
                  <p className="font-medium text-gray-900">{insight.message}</p>
                  <p className="text-sm text-gray-600 mt-1">{insight.recommendation}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Report Status Pipeline (Funnel) */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Report Status Pipeline</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={funnelData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Confidence Score Distribution */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Confidence Score Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={confidenceBins}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
            {dashboard && (
              <div className="mt-4 grid grid-cols-4 gap-2 text-sm">
                <div>
                  <p className="text-gray-600">Mean</p>
                  <p className="font-semibold">{(dashboard.confidence_score_distribution.mean * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-600">Median</p>
                  <p className="font-semibold">{(dashboard.confidence_score_distribution.median * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-600">Min</p>
                  <p className="font-semibold">{(dashboard.confidence_score_distribution.min * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-600">Max</p>
                  <p className="font-semibold">{(dashboard.confidence_score_distribution.max * 100).toFixed(1)}%</p>
                </div>
              </div>
            )}
          </Card>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Analysis Type Breakdown */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Analysis Type Breakdown</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analysisTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {analysisTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>

          {/* Top Industries */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Top Industries Analyzed</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={industriesData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Charts Row 3 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Peak Usage Times */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Peak Usage Times</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={peakUsageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
            {business && business.peak_usage_times.peak_hour !== null && (
              <p className="mt-2 text-sm text-gray-600">
                Peak hour: {business.peak_usage_times.peak_hour}:00
              </p>
            )}
          </Card>

          {/* Most Used Frameworks */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Most Used Frameworks</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={frameworksData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {frameworksData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Business Metrics Summary */}
        {business && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Business Metrics Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Unique Users</p>
                <p className="text-2xl font-bold text-gray-900">{business.user_adoption.total_unique_users}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">New Users This Period</p>
                <p className="text-2xl font-bold text-gray-900">{business.user_adoption.new_users_this_period}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Top Industry</p>
                <p className="text-2xl font-bold text-gray-900">
                  {business.top_industries[0]?.industry || 'N/A'}
                </p>
                <p className="text-xs text-gray-500">{business.top_industries[0]?.count || 0} analyses</p>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

