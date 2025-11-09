'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  JobQueue,
  JobHistory,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
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
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${job.progress}%` }}
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

export default function JobsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const jobId = searchParams.get('id');

  const [activeTab, setActiveTab] = useState<'active' | 'history'>('active');
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
      // Handle different response formats
      if (Array.isArray(response)) {
        setActiveJobs(response);
      } else if (response?.jobs) {
        setActiveJobs(response.jobs);
      } else {
        setActiveJobs([]);
      }
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch active jobs:', err);
      // Don't show error if it's just an empty result
      if (err.status !== 404) {
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
      // Handle different response formats
      if (Array.isArray(response)) {
        setJobHistory(response);
      } else if (response?.jobs) {
        setJobHistory(response.jobs);
      } else {
        setJobHistory([]);
      }
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch job history:', err);
      // Don't show error if it's just an empty result
      if (err.status !== 404) {
        setError(err.message || 'Failed to load job history');
      } else {
        setJobHistory([]);
        setError(null);
      }
    }
  }, []);

  // Initial load
  useEffect(() => {
    const loadJobs = async () => {
      setIsLoading(true);
      await Promise.all([fetchActiveJobs(), fetchJobHistory()]);
      setIsLoading(false);
    };

    loadJobs();
  }, [fetchActiveJobs, fetchJobHistory]);

  // Auto-refresh active jobs every 5 seconds
  useEffect(() => {
    if (activeTab === 'active') {
      const interval = setInterval(fetchActiveJobs, 5000);
      return () => clearInterval(interval);
    }
  }, [activeTab, fetchActiveJobs]);

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
          const job = await api.jobs.getStatus(jobId);
          setSelectedJob(job);
          setIsModalOpen(true);

          // Auto-select correct tab based on job status
          if (job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') {
            setActiveTab('history');
          } else {
            setActiveTab('active');
          }
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
      // Fetch full details
      const fullJob = await api.jobs.getStatus(job.id);
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
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Job Queue</h1>
            <p className="text-gray-600 mt-2">
              Monitor and manage your analysis jobs
            </p>
          </div>
          <Link href="/analysis">
            <Button>
              Create New Analysis
            </Button>
          </Link>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <ErrorAlert className="mb-6" onDismiss={() => setError(null)}>
          {error}
        </ErrorAlert>
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
              <p className="text-gray-600 mt-4">Loading jobs...</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* Tabbed Interface */
        <Tabs
          defaultTab={activeTab === 'active' ? 0 : 1}
          onChange={(index) => setActiveTab(index === 0 ? 'active' : 'history')}
        >
          <TabList>
            <Tab>
              Active Jobs
              {activeJobs.length > 0 && (
                <Badge className="ml-2 bg-blue-100 text-blue-800">
                  {activeJobs.length}
                </Badge>
              )}
            </Tab>
            <Tab>
              Job History
              {jobHistory.length > 0 && (
                <Badge className="ml-2 bg-gray-100 text-gray-800">
                  {jobHistory.length}
                </Badge>
              )}
            </Tab>
          </TabList>

          <TabPanels>
            {/* Active Jobs Tab */}
            <TabPanel>
              <Card>
                <CardHeader>
                  <CardTitle>Running and Pending Jobs</CardTitle>
                  <CardDescription>
                    Jobs are automatically refreshed every 5 seconds
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <JobQueue
                    jobs={activeJobs}
                    onJobClick={handleJobClick}
                    onCancelJob={handleCancelJob}
                    autoRefresh={true}
                    refreshInterval={5000}
                  />

                  {activeJobs.length === 0 && (
                    <div className="text-center py-12">
                      <p className="text-gray-500">No active jobs</p>
                      <Link href="/analysis">
                        <Button className="mt-4">
                          Create New Analysis
                        </Button>
                      </Link>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabPanel>

            {/* Job History Tab */}
            <TabPanel>
              <Card>
                <CardHeader>
                  <CardTitle>Completed Jobs</CardTitle>
                  <CardDescription>
                    View past completed, failed, and cancelled jobs
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <JobHistory
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
            </TabPanel>
          </TabPanels>
        </Tabs>
      )}

      {/* Job Details Modal */}
      <JobDetailsModal
        job={selectedJob}
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onCancel={handleCancelJob}
      />
    </div>
  );
}
