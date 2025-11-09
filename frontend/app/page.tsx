'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  MetricCard,
  Button,
  Badge,
  DataTable,
  Alert,
  Spinner,
} from '@/app/components';
import { api, APIError } from '@/lib/api';
import {
  BarChart3,
  FileText,
  Briefcase,
  User,
  TrendingUp,
  Clock,
  CheckCircle,
  Plus,
  ArrowRight,
  FolderOpen,
  Settings,
  Layers,
} from 'lucide-react';
import { format } from 'date-fns';

// Types
interface DashboardMetrics {
  total: number;
  active: number;
  thisMonth: number;
  avgConfidence: number;
}

interface RecentReport {
  report_id: string;
  company: string;
  industry?: string;
  frameworks: string[];
  status: string;
  confidence_score?: number;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  
  // State
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    total: 0,
    active: 0,
    thisMonth: 0,
    avgConfidence: 0,
  });
  const [recentReports, setRecentReports] = useState<RecentReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load dashboard data
  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch recent reports
      const reportsResponse = await api.analysis.listReports({ limit: 5, sort_by: 'created_at', order: 'desc' });
      const reports = reportsResponse?.reports || [];
      setRecentReports(reports);

      // Fetch active jobs (handle errors gracefully)
      let activeJobs = [];
      try {
        const jobsResponse = await api.jobs.listJobs({ status: 'pending,running' });
        activeJobs = jobsResponse?.jobs || [];
      } catch (err) {
        // If jobs endpoint fails, just use empty array (non-critical)
        console.warn('Failed to fetch active jobs:', err);
        activeJobs = [];
      }

      // Calculate metrics
      const now = new Date();
      const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      const reportsThisMonth = reports.filter((r: RecentReport) => 
        new Date(r.created_at) >= firstDayOfMonth
      );

      const confidenceScores = reports
        .filter((r: RecentReport) => r.confidence_score != null)
        .map((r: RecentReport) => r.confidence_score!);
      
      const avgConfidence = confidenceScores.length > 0
        ? confidenceScores.reduce((sum, score) => sum + score, 0) / confidenceScores.length
        : 0;

      setMetrics({
        total: reports.length,
        active: activeJobs.length,
        thisMonth: reportsThisMonth.length,
        avgConfidence,
      });
    } catch (err) {
      console.error('Dashboard load error:', err);
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError('Failed to load dashboard data');
      }
    } finally {
      setLoading(false);
    }
  };

  // Table columns for recent reports
  const columns = [
    {
      key: 'company',
      label: 'Company',
      render: (report: RecentReport) => (
        <div>
          <div className="font-medium text-gray-900">{report.company}</div>
          {report.industry && (
            <div className="text-sm text-gray-500">{report.industry}</div>
          )}
        </div>
      ),
    },
    {
      key: 'frameworks',
      label: 'Frameworks',
      render: (report: RecentReport) => (
        <div className="flex flex-wrap gap-1">
          {(report.frameworks || []).map((f) => (
            <Badge key={f} variant="primary">
              {f}
            </Badge>
          ))}
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Date',
      render: (report: RecentReport) => {
        if (!report.created_at) return '-';
        try {
          const date = new Date(report.created_at);
          if (isNaN(date.getTime())) return '-';
          return format(date, 'MMM d, yyyy');
        } catch {
          return '-';
        }
      },
    },
    {
      key: 'status',
      label: 'Status',
      render: (report: RecentReport) => (
        <Badge variant={report.status === 'completed' ? 'success' : 'warning'}>
          {report.status}
        </Badge>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">
              Welcome to ConsultantOS
            </h1>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Generate McKinsey-grade business framework analyses in 30 minutes
              with our multi-agent AI system
            </p>
            <div className="flex justify-center gap-4">
              <Button
                variant="secondary"
                size="lg"
                onClick={() => router.push('/analysis')}
                className="bg-white text-blue-600 hover:bg-blue-50"
              >
                <Plus className="w-5 h-5 mr-2" />
                Create Analysis
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => router.push('/reports')}
                className="border-white text-white hover:bg-blue-700"
              >
                View Reports
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {/* Key Metrics Dashboard */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Dashboard Overview</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Reports Created"
              value={metrics.total}
              icon={<FileText className="w-6 h-6" />}
              trend={metrics.thisMonth > 0 ? { value: metrics.thisMonth, direction: 'up' } : undefined}
              className="bg-white"
            />
            <MetricCard
              title="Active Jobs"
              value={metrics.active}
              icon={<TrendingUp className="w-6 h-6" />}
              className="bg-white"
            />
            <MetricCard
              title="Reports This Month"
              value={metrics.thisMonth}
              icon={<BarChart3 className="w-6 h-6" />}
              className="bg-white"
            />
            <MetricCard
              title="Avg Confidence Score"
              value={`${(metrics.avgConfidence * 100).toFixed(0)}%`}
              icon={<CheckCircle className="w-6 h-6" />}
              className="bg-white"
            />
          </div>
        </section>

        {/* Recent Reports Section */}
        <section className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Recent Reports</h2>
            <Button
              variant="outline"
              onClick={() => router.push('/reports')}
            >
              View All
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
          <Card>
            <CardContent>
              {recentReports.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">No reports yet</p>
                  <Button onClick={() => router.push('/analysis')}>
                    Create Your First Analysis
                  </Button>
                </div>
              ) : (
                <DataTable
                  columns={columns}
                  data={recentReports}
                  rowKey={(report) => report.report_id}
                  onRowClick={(report) => router.push(`/reports/${report.report_id}`)}
                />
              )}
            </CardContent>
          </Card>
        </section>

        {/* Quick Actions Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/analysis')}>
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-blue-600" />
                </div>
                <CardTitle className="text-lg">Create Analysis</CardTitle>
                <CardDescription>
                  Generate a new business framework analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" className="w-full">
                  Get Started
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/templates')}>
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Layers className="w-6 h-6 text-green-600" />
                </div>
                <CardTitle className="text-lg">Browse Templates</CardTitle>
                <CardDescription>
                  Explore pre-built analysis templates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" className="w-full">
                  View Library
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/jobs')}>
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <Clock className="w-6 h-6 text-purple-600" />
                </div>
                <CardTitle className="text-lg">View Job Queue</CardTitle>
                <CardDescription>
                  Monitor active and pending analyses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" className="w-full">
                  View Queue
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push('/profile')}>
              <CardHeader>
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                  <User className="w-6 h-6 text-orange-600" />
                </div>
                <CardTitle className="text-lg">Manage Profile</CardTitle>
                <CardDescription>
                  Update your account settings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" className="w-full">
                  Settings
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Getting Started Guide */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Getting Started</h2>
          <Card>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 py-6">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-blue-600">1</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Create Your First Analysis
                  </h3>
                  <p className="text-sm text-gray-600">
                    Choose frameworks, enter company details, and let our AI agents
                    generate comprehensive insights
                  </p>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-green-600">2</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Review and Share Results
                  </h3>
                  <p className="text-sm text-gray-600">
                    Download professional PDF reports, share with stakeholders,
                    and export to multiple formats
                  </p>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-purple-600">3</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Collaborate with Comments
                  </h3>
                  <p className="text-sm text-gray-600">
                    Add comments, track versions, and collaborate with your team
                    on strategic insights
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}