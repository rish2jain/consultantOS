'use client';

import { useState, useEffect, useCallback, useRef, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';

// Force dynamic rendering to avoid static generation issues with useSearchParams
export const dynamic = 'force-dynamic';
import Link from 'next/link';
import {
  JobQueue,
  JobHistory,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
  Alert,
  ErrorAlert,
  SuccessAlert,
  Badge,
  Modal,
  Spinner,
} from '@/app/components';
import { api } from '@/lib/api';

interface Job {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  result?: any;
  error?: string;
  created_at: string;
  updated_at: string;
  company?: string;
  industry?: string;
  frameworks?: string[];
}

interface JobDetailsModalProps {
  job: Job | null;
  isOpen: boolean;
  onClose: () => void;
  onCancel?: (jobId: string) => void;
}

function JobDetailsModal({ job, isOpen, onClose, onCancel }: JobDetailsModalProps) {
  if (!job) return null;

  const formatDuration = (created: string, updated: string) => {
    const start = new Date(created);
    const end = new Date(updated);
    const diffMs = end.getTime() - start.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffSecs = Math.floor((diffMs % 60000) / 1000);
    return diffMins > 0 ? `${diffMins}m ${diffSecs}s` : `${diffSecs}s`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Job Details">
      <div className="space-y-4">
        {/* Job Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <Badge className={getStatusColor(job.status)}>
            {job.status.toUpperCase()}
          </Badge>
        </div>

        {/* Job ID */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Job ID
          </label>
          <code className="block bg-gray-50 px-3 py-2 rounded text-sm font-mono">
            {job.id}
          </code>
        </div>

        {/* Progress */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Progress
          </label>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <motion.div
              className="bg-blue-600 h-2.5 rounded-full"
              initial={false}
              animate={{ width: `${job.progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-1">{job.progress}%</p>
        </div>

        {/* Analysis Details */}
        {job.company && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company
            </label>
            <p className="text-sm text-gray-900">{job.company}</p>
          </div>
        )}

        {job.industry && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry
            </label>
            <p className="text-sm text-gray-900">{job.industry}</p>
          </div>
        )}

        {job.frameworks && job.frameworks.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Frameworks
            </label>
            <div className="flex flex-wrap gap-2">
              {job.frameworks.map((framework) => (
                <Badge key={framework} className="bg-purple-100 text-purple-800">
                  {framework}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Timing */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Elapsed Time
          </label>
          <p className="text-sm text-gray-900">
            {formatDuration(job.created_at, job.updated_at)}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Created At
          </label>
          <p className="text-sm text-gray-900">
            {new Date(job.created_at).toLocaleString()}
          </p>
        </div>

        {/* Error Message */}
        {job.error && (
          <div>
            <label className="block text-sm font-medium text-red-700 mb-1">
              Error
            </label>
            <div className="bg-red-50 border border-red-200 rounded px-3 py-2">
              <p className="text-sm text-red-800 font-mono">{job.error}</p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t">
          {job.status === 'completed' && job.result?.report_id && (
            <Link
              href={`/reports/${job.result.report_id}`}
              className="flex-1"
            >
              <Button className="w-full">
                View Report
              </Button>
            </Link>
          )}

          {(job.status === 'pending' || job.status === 'running') && onCancel && (
            <Button
              onClick={() => onCancel(job.id)}
              variant="secondary"
              className="flex-1"
            >
              Cancel Job
            </Button>
          )}

          <Button onClick={onClose} variant="secondary" className="flex-1">
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}

function JobsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const jobId = searchParams.get('id');

  const [activeJobs, setActiveJobs] = useState<Job[]>([]);
  const [jobHistory, setJobHistory] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const successMessageTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Fetch active jobs
  const fetchActiveJobs = useCallback(async () => {
    try {
      const response = await api.jobs.listJobs({
        status: 'pending,running',
        limit: 50,
      });
      // Handle different response formats and transform to Job interface
      let jobs: Job[] = [];
      if (Array.isArray(response)) {
        jobs = response;
      } else if (response?.jobs) {
        jobs = response.jobs;
      }
      
      // Transform jobs to match Job interface (id -> job_id mapping)
      const transformedJobs: Job[] = jobs.map((job: any) => ({
        id: job.job_id || job.id,
        status: job.status,
        progress: job.progress || 0,
        result: job.result,
        error: job.error,
        created_at: job.created_at,
        updated_at: job.updated_at || job.created_at,
        company: job.company,
        industry: job.industry,
        frameworks: job.frameworks || [],
      }));
      
      setActiveJobs(transformedJobs);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch active jobs:', err);
      // Handle network errors and connection refused
      if (err.message?.includes('Failed to fetch') || 
          err.message?.includes('NetworkError') ||
          err.message?.includes('ERR_CONNECTION_REFUSED') ||
          err.name === 'TypeError') {
        setError('Unable to connect to backend server. Please ensure the backend is running at ' + (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'));
        setActiveJobs([]);
      } else if (err.status !== 404) {
        setError(err.message || 'Failed to load active jobs');
      } else {
        setActiveJobs([]);
        setError(null);
      }
    }
  }, []);

  // Fetch job history
  const fetchJobHistory = useCallback(async () => {
    try {
      const response = await api.jobs.listJobs({
        status: 'completed,failed,cancelled',
        limit: 100,
      });
      // Handle different response formats and transform to Job interface
      let jobs: Job[] = [];
      if (Array.isArray(response)) {
        jobs = response;
      } else if (response?.jobs) {
        jobs = response.jobs;
      }
      
      // Transform jobs to match Job interface (id -> job_id mapping)
      const transformedJobs: Job[] = jobs.map((job: any) => ({
        id: job.job_id || job.id,
        status: job.status,
        progress: job.progress || (job.status === 'completed' ? 100 : 0),
        result: job.result,
        error: job.error,
        created_at: job.created_at,
        updated_at: job.updated_at || job.created_at,
        company: job.company,
        industry: job.industry,
        frameworks: job.frameworks || [],
      }));
      
      setJobHistory(transformedJobs);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch job history:', err);
      // Handle network errors and connection refused
      if (err.message?.includes('Failed to fetch') || 
          err.message?.includes('NetworkError') ||
          err.message?.includes('ERR_CONNECTION_REFUSED') ||
          err.name === 'TypeError') {
        setError('Unable to connect to backend server. Please ensure the backend is running at ' + (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'));
        setJobHistory([]);
      } else if (err.status !== 404) {
        setError(err.message || 'Failed to load job history');
      } else {
        setJobHistory([]);
        setError(null);
      }
    }
  }, []);

  // Initial load with timeout
  useEffect(() => {
    const loadJobs = async () => {
      setIsLoading(true);
      
      // Set a timeout to prevent infinite loading
      const timeoutId = setTimeout(() => {
        setIsLoading(false);
        if (activeJobs.length === 0 && jobHistory.length === 0 && !error) {
          setError('Request timed out. Please check if the backend server is running.');
        }
      }, 10000); // 10 second timeout
      
      try {
        await Promise.all([fetchActiveJobs(), fetchJobHistory()]);
        clearTimeout(timeoutId);
        setIsLoading(false);
      } catch (err) {
        clearTimeout(timeoutId);
        setIsLoading(false);
        // Error is already handled in fetchActiveJobs/fetchJobHistory
      }
    };

    loadJobs();
  }, [fetchActiveJobs, fetchJobHistory]);

  // Auto-refresh active jobs every 5 seconds
  useEffect(() => {
    const interval = setInterval(fetchActiveJobs, 5000);
    return () => clearInterval(interval);
  }, [fetchActiveJobs]);

  // Cleanup success message timeout on unmount
  useEffect(() => {
    return () => {
      if (successMessageTimeoutRef.current !== null) {
        clearTimeout(successMessageTimeoutRef.current);
        successMessageTimeoutRef.current = null;
      }
    };
  }, []);

  // Handle job ID from URL
  useEffect(() => {
    if (jobId) {
      const loadJobDetails = async () => {
        try {
          const jobData = await api.jobs.getStatus(jobId);
          // Transform to Job interface
          const job: Job = {
            id: jobData.job_id || jobData.id || jobId,
            status: jobData.status,
            progress: jobData.progress || 0,
            result: jobData.result,
            error: jobData.error,
            created_at: jobData.created_at,
            updated_at: jobData.updated_at || jobData.created_at,
            company: jobData.company,
            industry: jobData.industry,
            frameworks: jobData.frameworks || [],
          };
          setSelectedJob(job);
          setIsModalOpen(true);
        } catch (err: any) {
          console.error('Failed to load job details:', err);
          setError(`Failed to load job ${jobId}: ${err.message}`);
        }
      };

      loadJobDetails();
    }
  }, [jobId]);

  // Handle job selection
  const handleJobClick = async (job: Job) => {
    try {
      // Fetch full details - use job_id if available, otherwise use id
      const jobId = (job as any).job_id || job.id;
      const fullJobData = await api.jobs.getStatus(jobId);
      
      // Transform to Job interface
      const fullJob: Job = {
        id: fullJobData.job_id || fullJobData.id || jobId,
        status: fullJobData.status,
        progress: fullJobData.progress || 0,
        result: fullJobData.result,
        error: fullJobData.error,
        created_at: fullJobData.created_at,
        updated_at: fullJobData.updated_at || fullJobData.created_at,
        company: fullJobData.company,
        industry: fullJobData.industry,
        frameworks: fullJobData.frameworks || [],
      };
      
      setSelectedJob(fullJob);
      setIsModalOpen(true);
    } catch (err: any) {
      console.error('Failed to load job details:', err);
      setError(`Failed to load job details: ${err.message}`);
    }
  };

  // Handle job cancellation
  const handleCancelJob = async (jobId: string) => {
    try {
      await api.jobs.cancelJob(jobId);
      setSuccessMessage('Job cancelled successfully');
      setIsModalOpen(false);
      setSelectedJob(null);

      // Refresh jobs
      await Promise.all([fetchActiveJobs(), fetchJobHistory()]);

      // Clear any existing timeout before creating a new one
      if (successMessageTimeoutRef.current !== null) {
        clearTimeout(successMessageTimeoutRef.current);
      }

      // Clear success message after 3 seconds
      successMessageTimeoutRef.current = setTimeout(() => {
        setSuccessMessage(null);
        successMessageTimeoutRef.current = null;
      }, 3000);
    } catch (err: any) {
      console.error('Failed to cancel job:', err);
      setError(`Failed to cancel job: ${err.message}`);
    }
  };

  // Handle modal close
  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedJob(null);

    // Clear job ID from URL
    if (jobId) {
      router.push('/jobs');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="container mx-auto px-4 py-8 max-w-7xl"
    >
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">Job Queue</h1>
            <p className="text-base text-gray-600">
              Monitor and manage your analysis jobs
            </p>
          </div>
          <Link href="/analysis">
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button>
                Create New Analysis
              </Button>
            </motion.div>
          </Link>
        </div>
      </motion.div>

      {/* Alerts */}
      {error && (
        <Alert
          variant="error"
          title="Failed to Load Jobs"
          description={
            <div>
              <p className="mb-2">{error}</p>
              {error.includes('Unable to connect') || error.includes('Network error') ? (
                <p className="text-sm text-red-700 mt-2">
                  Please ensure the backend server is running at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}
                </p>
              ) : null}
            </div>
          }
          actions={
            <div className="flex gap-2 mt-3">
              <Button
                size="sm"
                variant="secondary"
                onClick={async () => {
                  setError(null);
                  try {
                    await Promise.all([fetchActiveJobs(), fetchJobHistory()]);
                  } catch (err) {
                    setError(err instanceof Error ? err.message : String(err));
                  }
                }}
                className="bg-white text-red-700 hover:bg-red-50"
              >
                Retry
              </Button>
            </div>
          }
          dismissible
          onClose={() => setError(null)}
          className="mb-6"
        />
      )}

      {successMessage && (
        <SuccessAlert className="mb-6" onDismiss={() => setSuccessMessage(null)}>
          {successMessage}
        </SuccessAlert>
      )}

      {/* Loading State */}
      {isLoading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <Spinner />
              <p className="text-gray-700 font-medium mt-4">Loading jobs...</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Active Jobs Section */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Running and Pending Jobs</CardTitle>
                  <CardDescription>
                    Jobs are automatically refreshed every 5 seconds
                  </CardDescription>
                </div>
                {activeJobs.length > 0 && (
                  <Badge className="bg-blue-100 text-blue-800">
                    {activeJobs.length} active
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <JobQueue
                jobs={activeJobs.map(job => ({
                  job_id: job.id,
                  status: job.status as "pending" | "running" | "completed" | "failed",
                  progress: job.progress,
                  created_at: job.created_at,
                  updated_at: job.updated_at,
                  company: job.company,
                  industry: job.industry,
                  frameworks: job.frameworks,
                  result: job.result,
                  error: job.error,
                }))}
                onJobClick={(jobStatus) => {
                  // Find the corresponding Job from activeJobs
                  const job = activeJobs.find(j => j.id === jobStatus.job_id);
                  if (job) {
                    handleJobClick(job);
                  }
                }}
                onCancelJob={handleCancelJob}
                autoRefresh={true}
                refreshInterval={5000}
              />

              {activeJobs.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-700 font-medium">No active jobs</p>
                  <Link href="/analysis">
                    <Button className="mt-4">
                      Create New Analysis
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Job History Section */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Completed Jobs</CardTitle>
                  <CardDescription>
                    View past completed, failed, and cancelled jobs
                  </CardDescription>
                </div>
                {jobHistory.length > 0 && (
                  <Badge className="bg-gray-100 text-gray-800">
                    {jobHistory.length} total
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <JobHistory
                jobs={jobHistory.map(job => ({
                  job_id: job.id,
                  status: job.status as "pending" | "running" | "completed" | "failed",
                  progress: job.progress,
                  created_at: job.created_at,
                  updated_at: job.updated_at,
                  company: job.company,
                  industry: job.industry,
                  frameworks: job.frameworks,
                  result: job.result,
                  error: job.error,
                }))}
                pageSize={20}
                allowDelete={true}
                onJobDeleted={(jobId) => {
                  // Refresh job history after deletion
                  fetchJobHistory();
                }}
                onDownload={(jobId, result) => {
                  // Handle download - navigate to report if available
                  if (result?.report_id) {
                    router.push(`/reports/${result.report_id}`);
                  }
                }}
              />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Job Details Modal */}
      <JobDetailsModal
        job={selectedJob}
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onCancel={handleCancelJob}
      />
    </motion.div>
  );
}

export default function JobsPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <Spinner />
              <p className="text-gray-700 font-medium mt-4">Loading jobs...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    }>
      <JobsPageContent />
    </Suspense>
  );
}
