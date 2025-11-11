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
  MetricCardSkeleton,
  Button,
  Badge,
  DataTable,
  DataTableSkeleton,
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
  const [isSampleData, setIsSampleData] = useState(false);

  // Load dashboard data
  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      let reports: RecentReport[] = [];
      try {
        const reportsResponse = await api.analysis.listReports({ limit: 5, sort_by: 'created_at', order: 'desc' });
        reports = reportsResponse?.reports || [];
        setIsSampleData(false);
      } catch (reportsErr) {
        console.warn('Falling back to sample dashboard reports', reportsErr);
        reports = [
          {
            report_id: 'sample-1',
            company: 'Contoso Retail',
            industry: 'Retail',
            frameworks: ['SWOT', '3C'],
            status: 'sample',
            confidence_score: 0.82,
            created_at: new Date().toISOString(),
          },
        ];
        setIsSampleData(true);
      }

      setRecentReports(reports);
      console.log('Loaded reports:', reports); // Debug: Check if data is loading

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
        setError(`Reports API unavailable: ${err.message}`);
      } else {
        setError('Failed to load dashboard data. Please check your connection and try again.');
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
      render: (value: any, report: RecentReport) => (
        <div>
          <div className="font-semibold text-black" style={{ color: '#000000' }}>{report.company || value || '-'}</div>
          {report.industry && (
            <div className="text-sm text-gray-800" style={{ color: '#1f2937' }}>{report.industry}</div>
          )}
        </div>
      ),
    },
    {
      key: 'frameworks',
      label: 'Frameworks',
      render: (value: any, report: RecentReport) => (
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
      render: (value: any, report: RecentReport) => {
        const dateStr = report.created_at || value;
        if (!dateStr) return <span style={{ color: '#000000' }}>-</span>;
        try {
          const date = new Date(dateStr);
          if (isNaN(date.getTime())) return <span style={{ color: '#000000' }}>-</span>;
          return <span style={{ color: '#000000' }}>{format(date, 'MMM d, yyyy')}</span>;
        } catch {
          return <span style={{ color: '#000000' }}>-</span>;
        }
      },
    },
    {
      key: 'status',
      label: 'Status',
      render: (value: any, report: RecentReport) => (
        <Badge variant={report.status === 'completed' ? 'success' : 'warning'}>
          {report.status || value || '-'}
        </Badge>
      ),
    },
  ];

  // No full-page loading - use skeleton loaders instead

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
              Generate professional-grade business framework analyses in 30 minutes
              with our multi-agent AI system
            </p>
            <div className="flex justify-center gap-4">
              <Button
                variant="outline"
                size="lg"
                onClick={() => router.push('/mvp-demo')}
                className="!bg-white !text-blue-900 !border-white hover:!bg-blue-50 hover:!text-blue-900 focus:ring-blue-300 shadow-md"
              >
                <Plus className="w-5 h-5 mr-2" />
                Try MVP Demo
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => router.push('/analysis')}
                className="!bg-white !text-blue-900 !border-white hover:!bg-blue-50 hover:!text-blue-900 focus:ring-blue-300 shadow-md"
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
        {/* Error Alert with Retry */}
        {error && (
          <Alert 
            variant="error" 
            className="mb-6"
            title="Data Fetch Error"
            actions={
              <div className="flex gap-2 mt-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={loadDashboard}
                  className="bg-white text-red-700 hover:bg-red-50"
                >
                  Retry
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => window.open('/help', '_blank')}
                  className="border-red-300 text-red-700 hover:bg-red-50"
                >
                  Contact Support
                </Button>
              </div>
            }
          >
            <div className="text-red-800">
              {error}
            </div>
          </Alert>
        )}

        {/* Key Metrics Dashboard */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Dashboard Overview</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {loading ? (
              <>
                <MetricCardSkeleton />
                <MetricCardSkeleton />
                <MetricCardSkeleton />
                <MetricCardSkeleton />
              </>
            ) : (
              <>
                <MetricCard
                  title="Total Reports Created"
                  value={metrics.total === 0 ? '—' : metrics.total}
                  icon={<FileText className="w-6 h-6" />}
                  trend={metrics.thisMonth > 0 ? 'up' : undefined}
                  trendValue={metrics.thisMonth > 0 ? `${metrics.thisMonth} this month` : undefined}
                  subtitle={metrics.total === 0 ? 'No reports yet—run your first analysis' : undefined}
                  onClick={metrics.total === 0 ? () => router.push('/analysis') : undefined}
                  className="bg-white shadow-sm hover:shadow-md transition-shadow"
                />
                <MetricCard
                  title="Active Jobs"
                  value={metrics.active === 0 ? '—' : metrics.active}
                  icon={<TrendingUp className="w-6 h-6" />}
                  subtitle={metrics.active === 0 ? 'No active jobs' : undefined}
                  className="bg-white shadow-sm hover:shadow-md transition-shadow"
                />
                <MetricCard
                  title="Reports This Month"
                  value={metrics.thisMonth === 0 ? '—' : metrics.thisMonth}
                  icon={<BarChart3 className="w-6 h-6" />}
                  subtitle={metrics.thisMonth === 0 ? 'No reports this month' : undefined}
                  className="bg-white shadow-sm hover:shadow-md transition-shadow"
                />
                <MetricCard
                  title="Avg Confidence Score"
                  value={metrics.avgConfidence === 0 ? '—' : `${(metrics.avgConfidence * 100).toFixed(0)}%`}
                  icon={<CheckCircle className="w-6 h-6" />}
                  subtitle={metrics.avgConfidence === 0 ? 'No confidence data available' : undefined}
                  className="bg-white shadow-sm hover:shadow-md transition-shadow"
                />
              </>
            )}
          </div>
        </section>

        {/* Recent Reports Section */}
        <section className="mb-8 border-t border-gray-200 pt-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Recent Reports</h2>
            <Button
              variant="outline"
              onClick={() => router.push('/reports')}
              disabled={recentReports.length === 0}
              aria-label={recentReports.length === 0 ? 'No reports available to view' : 'View all reports'}
            >
              View All
              <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
            </Button>
          </div>
          <Card className="bg-white shadow-sm">
            <CardContent>
              {loading ? (
                <DataTableSkeleton columns={4} rows={5} />
              ) : recentReports.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" aria-hidden="true" />
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
        <section className="mb-8 border-t border-gray-200 pt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer bg-white shadow-sm" onClick={() => router.push('/analysis')}>
              <CardHeader className="pb-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                  <BarChart3 className="w-6 h-6 text-blue-600" aria-hidden="true" />
                </div>
                <CardTitle className="text-lg">Create Analysis</CardTitle>
                <CardDescription className="text-sm">
                  Generate a new business framework analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <Button variant="ghost" className="w-full" aria-label="Create new analysis">
                  <span className="hidden sm:inline">Get Started</span>
                  <span className="sm:hidden">Create</span>
                  <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer bg-white shadow-sm" onClick={() => router.push('/templates')}>
              <CardHeader className="pb-3">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-3">
                  <Layers className="w-6 h-6 text-green-600" aria-hidden="true" />
                </div>
                <CardTitle className="text-lg">Browse Templates</CardTitle>
                <CardDescription className="text-sm">
                  Explore pre-built analysis templates
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <Button variant="ghost" className="w-full" aria-label="Browse templates">
                  <span className="hidden sm:inline">View Library</span>
                  <span className="sm:hidden">Templates</span>
                  <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer bg-white shadow-sm" onClick={() => router.push('/jobs')}>
              <CardHeader className="pb-3">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
                  <Clock className="w-6 h-6 text-purple-600" aria-hidden="true" />
                </div>
                <CardTitle className="text-lg">View Job Queue</CardTitle>
                <CardDescription className="text-sm">
                  Monitor active and pending analyses
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <Button variant="ghost" className="w-full" aria-label="View job queue">
                  <span className="hidden sm:inline">View Queue</span>
                  <span className="sm:hidden">Jobs</span>
                  <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer bg-white shadow-sm" onClick={() => router.push('/profile')}>
              <CardHeader className="pb-3">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-3">
                  <User className="w-6 h-6 text-orange-600" aria-hidden="true" />
                </div>
                <CardTitle className="text-lg">Manage Profile</CardTitle>
                <CardDescription className="text-sm">
                  Update your account settings
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <Button variant="ghost" className="w-full" aria-label="Manage profile settings">
                  <span className="hidden sm:inline">Settings</span>
                  <span className="sm:hidden">Profile</span>
                  <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Getting Started Guide */}
        <section className="border-t border-gray-200 pt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Getting Started</h2>
          <Card className="bg-white shadow-sm">
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-6">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-blue-600" aria-label="Step 1">1</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Create Your First Analysis
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Choose frameworks, enter company details, and let our AI agents generate comprehensive insights
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => router.push('/analysis')}
                    className="w-full"
                  >
                    Open Analysis Form
                  </Button>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-green-600" aria-label="Step 2">2</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Review and Share Results
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Download professional PDF reports, share with stakeholders, and export to multiple formats
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => router.push('/templates')}
                    className="w-full"
                  >
                    Download Sample PDF
                  </Button>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-purple-600" aria-label="Step 3">3</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Collaborate with Comments
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Add comments, track versions, and collaborate with your team on strategic insights
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => router.push('/reports')}
                    className="w-full"
                  >
                    View Reports
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}
