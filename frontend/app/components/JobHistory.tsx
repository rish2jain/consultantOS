"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card';
import { Badge } from './Badge';
import { Button } from './Button';
import { Spinner } from './Spinner';
import { Alert } from './Alert';
import { CheckCircle, XCircle, Download, Trash2, ChevronLeft, ChevronRight, FileText } from 'lucide-react';
import { JobStatus } from './JobStatusIndicator';

export interface JobHistoryProps {
  /** API base URL */
  apiUrl?: string;
  /** Jobs per page */
  pageSize?: number;
  /** Show delete button */
  allowDelete?: boolean;
  /** Callback when job is deleted */
  onJobDeleted?: (jobId: string) => void;
  /** Callback when download is requested */
  onDownload?: (jobId: string, result: any) => void;
  /** Custom className */
  className?: string;
}

export const JobHistory: React.FC<JobHistoryProps> = ({
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  pageSize = 10,
  allowDelete = true,
  onJobDeleted,
  onDownload,
  className = '',
}) => {
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingJobId, setDeletingJobId] = useState<string | null>(null);

  const totalPages = Math.ceil(totalJobs / pageSize);

  const fetchJobHistory = useCallback(async () => {
    setIsLoading(true);
    try {
      // Note: This endpoint would need to be implemented in the backend
      const offset = (currentPage - 1) * pageSize;
      const response = await fetch(
        `${apiUrl}/jobs?status=completed,failed&limit=${pageSize}&offset=${offset}`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch job history: ${response.statusText}`);
      }

      const data = await response.json();

      // Assuming API returns { jobs: JobStatus[], total: number }
      if (Array.isArray(data)) {
        setJobs(data);
        setTotalJobs(data.length);
      } else {
        setJobs(data.jobs || []);
        setTotalJobs(data.total || 0);
      }

      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, currentPage, pageSize]);

  const deleteJob = async (jobId: string) => {
    setDeletingJobId(jobId);
    try {
      const response = await fetch(`${apiUrl}/jobs/${jobId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete job: ${response.statusText}`);
      }

      setJobs(prev => prev.filter(job => job.job_id !== jobId));
      setTotalJobs(prev => prev - 1);
      onJobDeleted?.(jobId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
    } finally {
      setDeletingJobId(null);
    }
  };

  const handleDownload = (job: JobStatus) => {
    onDownload?.(job.job_id, job.result);
  };

  useEffect(() => {
    fetchJobHistory();
  }, [fetchJobHistory]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const formatDuration = (createdAt: string, updatedAt: string) => {
    const start = new Date(createdAt).getTime();
    const end = new Date(updatedAt).getTime();
    const durationSeconds = Math.floor((end - start) / 1000);

    if (durationSeconds < 60) {
      return `${durationSeconds}s`;
    }
    const minutes = Math.floor(durationSeconds / 60);
    const seconds = durationSeconds % 60;
    return `${minutes}m ${seconds}s`;
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Job History</CardTitle>
        <CardDescription>
          {totalJobs > 0
            ? `${totalJobs} completed job${totalJobs !== 1 ? 's' : ''}`
            : 'No completed jobs'}
        </CardDescription>
      </CardHeader>

      <CardContent>
        {error && (
          <Alert
            variant="error"
            title="Error loading history"
            description={error}
            dismissible
            onClose={() => setError(null)}
            className="mb-4"
          />
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Spinner size="lg" />
            <span className="ml-3 text-sm text-gray-600">Loading history...</span>
          </div>
        ) : jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mb-3" aria-hidden="true" />
            <p className="text-sm font-medium text-gray-900">No completed jobs</p>
            <p className="text-sm text-gray-500 mt-1">
              Your completed and failed jobs will appear here
            </p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Job ID
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Completed At
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {jobs.map((job) => (
                    <tr
                      key={job.job_id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="py-3 px-4">
                        <span className="text-sm font-mono text-gray-900">
                          {job.job_id.slice(0, 8)}...
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-900">
                          {job.company || '-'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {job.status === 'completed' ? (
                          <Badge variant="success" size="sm">
                            <CheckCircle className="w-3 h-3" aria-hidden="true" />
                            Completed
                          </Badge>
                        ) : (
                          <Badge variant="danger" size="sm">
                            <XCircle className="w-3 h-3" aria-hidden="true" />
                            Failed
                          </Badge>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-600">
                          {formatDuration(job.created_at, job.updated_at)}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-600">
                          {formatDate(job.updated_at)}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-end gap-2">
                          {job.status === 'completed' && job.result && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDownload(job)}
                              leftIcon={<Download className="w-4 h-4" />}
                              aria-label="Download result"
                            >
                              Download
                            </Button>
                          )}
                          {allowDelete && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteJob(job.job_id)}
                              isLoading={deletingJobId === job.job_id}
                              leftIcon={<Trash2 className="w-4 h-4" />}
                              aria-label="Delete job"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            />
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  Page {currentPage} of {totalPages} ({totalJobs} total)
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    leftIcon={<ChevronLeft className="w-4 h-4" />}
                    aria-label="Previous page"
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    rightIcon={<ChevronRight className="w-4 h-4" />}
                    aria-label="Next page"
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};
