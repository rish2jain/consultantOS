'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
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
  metadata?: Record<string, any>;
  partial_results?: boolean;
  errors?: Record<string, unknown> | string[];
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
  const isMountedRef = useRef(true);
  const getPartialStatus = useCallback((report: RecentReport) => {
    if (typeof report.partial_results === 'boolean') {
      return report.partial_results;
    }
    const metaFlag = report.metadata?.partial_results;
    if (typeof metaFlag === 'boolean') {
      return metaFlag;
    }
    return report.status === 'partial_success';
  }, []);

  const loadDashboard = useCallback(async () => {
    try {
      if (isMountedRef.current) {
        setLoading(true);
        setError(null);
      }

      const jobsPromise = api.jobs
        .listJobs({ status: 'pending,running' })
        .catch((err) => {
          console.warn('Failed to fetch active jobs:', err);
          return { jobs: [] };
        });

      let reports: RecentReport[] = [];
      try {
        const reportsResponse = await api.analysis.listReports({ limit: 5, sort_by: 'created_at', order: 'desc' });
        reports = reportsResponse?.reports || [];
        if (isMountedRef.current) {
          setIsSampleData(false);
          setError(null); // Clear any previous errors
        }
      } catch (reportsErr) {
        console.error('Failed to fetch reports:', reportsErr);
        
        // Log detailed error information
        if (reportsErr instanceof Error) {
          console.error('Error message:', reportsErr.message);
          console.error('Error stack:', reportsErr.stack);
        }
        
        // Check if it's an APIError for better messaging
        if (reportsErr instanceof APIError) {
          console.error('API Error status:', reportsErr.status);
          console.error('API Error data:', reportsErr.data);
          
          if (isMountedRef.current) {
            // Set a more specific error message
            if (reportsErr.status === 0) {
              setError(`Cannot connect to backend API. Please ensure the backend is running at ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}`);
            } else {
              setError(`API Error (${reportsErr.status}): ${reportsErr.message}`);
            }
          }
        } else {
          if (isMountedRef.current) {
            setError(`Failed to load reports: ${reportsErr instanceof Error ? reportsErr.message : 'Unknown error'}`);
          }
        }
        
        // Fall back to sample data
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
        if (isMountedRef.current) {
          setIsSampleData(true);
        }
      }

      const jobsResponse = await jobsPromise;
      const activeJobs = jobsResponse?.jobs || [];

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

      if (!isMountedRef.current) {
        return;
      }

      setRecentReports(reports);
      setMetrics({
        total: reports.length,
        active: activeJobs.length,
        thisMonth: reportsThisMonth.length,
        avgConfidence,
      });
    } catch (err) {
      console.error('Dashboard load error:', err);
      if (isMountedRef.current) {
        if (err instanceof APIError) {
          setError(`Reports API unavailable: ${err.message}`);
        } else {
          setError('Failed to load dashboard data. Please check your connection and try again.');
        }
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  // Load dashboard data
  useEffect(() => {
    isMountedRef.current = true;
    loadDashboard();
    return () => {
      isMountedRef.current = false;
    };
  }, [loadDashboard]);

  // Table columns for recent reports
  const columns = [
    {
      key: 'company',
      label: 'Company',
      accessor: (row: RecentReport) => row.company || row.report_id || '',
      render: (value: any, report: RecentReport) => (
        <div>
          <div className="font-semibold text-gray-900">{report.company || value || '-'}</div>
          {report.industry && (
            <div className="text-sm text-gray-700">{report.industry}</div>
          )}
          {getPartialStatus(report) && (
            <div className="mt-1">
              <Badge variant="warning">Partial data</Badge>
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'confidence_score',
      label: 'Confidence',
      render: (value: any, report: RecentReport) => (
        <span className="text-gray-900">
          {report.confidence_score != null
            ? `${(report.confidence_score * 100).toFixed(0)}%`
            : value ?? '—'}
        </span>
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
        if (!dateStr) return <span className="text-gray-900">-</span>;
        try {
          const date = new Date(dateStr);
          if (isNaN(date.getTime())) return <span className="text-gray-900">-</span>;
          return <span className="text-gray-900">{format(date, 'MMM d, yyyy')}</span>;
        } catch {
          return <span className="text-gray-900">-</span>;
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
    {
      key: 'actions',
      label: '',
      render: (_: any, report: RecentReport) => (
        <div className="flex justify-end gap-2">
          {getPartialStatus(report) && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(event) => {
                event.stopPropagation();
                router.push(`/reports/${report.report_id}?tab=health`);
              }}
            >
              View Issues
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={(event) => {
              event.stopPropagation();
              router.push(`/reports/${report.report_id}`);
            }}
          >
            Open
          </Button>
        </div>
      ),
    },
  ];

  // No full-page loading - use skeleton loaders instead

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.5 }}
              className="text-4xl font-bold mb-4"
            >
              Welcome to ConsultantOS
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto"
            >
              Generate professional-grade business framework analyses in 30 minutes
              with our multi-agent AI system
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="flex justify-center gap-4 flex-wrap"
            >
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => router.push('/mvp-demo')}
                  className="!bg-white !text-blue-900 !border-white hover:!bg-blue-50 hover:!text-blue-900 focus:ring-blue-300 shadow-md"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Try MVP Demo
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => router.push('/analysis')}
                  className="!bg-white !text-blue-900 !border-white hover:!bg-blue-50 hover:!text-blue-900 focus:ring-blue-300 shadow-md"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Create Analysis
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => router.push('/reports')}
                  className="border-white text-white hover:bg-blue-700"
                >
                  View Reports
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </motion.section>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert with Retry */}
        {error && (
          <Alert 
            variant="error" 
            className="mb-6"
            title={isSampleData ? "Showing sample dashboard data" : "Data Fetch Error"}
            actions={
              <div className="flex gap-2 mt-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={loadDashboard}
                  className="bg-white text-red-700 hover:bg-red-50"
                >
                  Retry Live Data
                </Button>
                {!isSampleData && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open('/help', '_blank')}
                    className="border-red-300 text-red-700 hover:bg-red-50"
                  >
                    Contact Support
                  </Button>
                )}
              </div>
            }
          >
            <div className="text-red-800">
              {error}
              {isSampleData && (
                <p className="mt-2 text-sm text-red-700">
                  Data below is from a sample workspace—try reloading to fetch live metrics.
                </p>
              )}
            </div>
          </Alert>
        )}

        {isSampleData && !error && (
          <Alert
            variant="warning"
            className="mb-6"
            title="Showing sample dashboard data"
            description="We couldn't reach your latest reports. Data below is from a sample workspace—try reloading to fetch live metrics."
            actions={
              <Button
                size="sm"
                variant="outline"
                onClick={loadDashboard}
              >
                Retry Live Data
              </Button>
            }
          />
        )}

        {/* Key Metrics Dashboard */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-8"
        >
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
        </motion.section>

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
                  rowKey={(report, index) => `${report.report_id}-${index}`}
                  onRowClick={(report) => router.push(`/reports/${report.report_id}`)}
                />
              )}
            </CardContent>
          </Card>
        </section>

        {/* Quick Actions Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="mb-8 border-t border-gray-200 pt-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
            <motion.div
              whileHover={{ y: -4, scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
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
            </motion.div>

            <motion.div
              whileHover={{ y: -4, scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
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
            </motion.div>

            <motion.div
              whileHover={{ y: -4, scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
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
            </motion.div>

            <motion.div
              whileHover={{ y: -4, scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
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
            </motion.div>
          </div>
        </motion.section>

        {/* Getting Started Guide */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="border-t border-gray-200 pt-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Getting Started</h2>
          <Card className="bg-white shadow-sm">
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-center"
                >
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
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="text-center"
                >
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
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="text-center"
                >
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
                </motion.div>
              </div>
            </CardContent>
          </Card>
        </motion.section>
      </main>
    </div>
  );
}
