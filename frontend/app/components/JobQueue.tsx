"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "./Card";
import { JobStatusIndicator, JobStatus } from "./JobStatusIndicator";
import { Button } from "./Button";
import { Spinner } from "./Spinner";
import { Alert } from "./Alert";
import { X, RefreshCw, Inbox } from "lucide-react";

export interface JobQueueProps {
  /** API base URL */
  apiUrl?: string;
  /** Polling interval for active jobs in milliseconds (default: 5000ms = 5s) */
  pollingInterval?: number;
  /** Max number of jobs to display */
  maxJobs?: number;
  /** Show completed jobs */
  showCompleted?: boolean;
  /** Callback when job is cancelled */
  onJobCancelled?: (jobId: string) => void;
  /** Callback when job completes */
  onJobComplete?: (jobId: string, result: any) => void;
  /** Custom className */
  className?: string;
}

export const JobQueue: React.FC<JobQueueProps> = ({
  apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  pollingInterval = 5000,
  maxJobs = 10,
  showCompleted = false,
  onJobCancelled,
  onJobComplete,
  className = "",
}) => {
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancellingJobId, setCancellingJobId] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    try {
      // Note: This endpoint would need to be implemented in the backend
      // For now, we'll assume it returns an array of job statuses
      const statusParam = showCompleted
        ? "status=pending,running,completed,failed"
        : "status=pending,running";
      const apiUrlWithParams = `${apiUrl}/jobs?limit=${maxJobs}&${statusParam}`;

      const response = await fetch(apiUrlWithParams);

      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.statusText}`);
      }

      const data: JobStatus[] = await response.json();
      setJobs(data);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, maxJobs, showCompleted]);

  const cancelJob = async (jobId: string) => {
    setCancellingJobId(jobId);
    try {
      const response = await fetch(`${apiUrl}/jobs/${jobId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`Failed to cancel job: ${response.statusText}`);
      }

      // Remove job from list
      setJobs((prev) => prev.filter((job) => job.job_id !== jobId));
      onJobCancelled?.(jobId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
    } finally {
      setCancellingJobId(null);
    }
  };

  const handleJobComplete = (jobId: string, result: any) => {
    if (!showCompleted) {
      setJobs((prev) => prev.filter((job) => job.job_id !== jobId));
    }
    onJobComplete?.(jobId, result);
  };

  const handleJobFailed = (jobId: string) => {
    if (!showCompleted) {
      setJobs((prev) => prev.filter((job) => job.job_id !== jobId));
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  // Polling for updates
  useEffect(() => {
    const activeJobs = jobs.filter(
      (job) => job.status === "pending" || job.status === "running"
    );

    if (activeJobs.length > 0) {
      const intervalId = setInterval(fetchJobs, pollingInterval);
      return () => clearInterval(intervalId);
    }
  }, [jobs, fetchJobs, pollingInterval]);

  const activeJobs = jobs.filter(
    (job) => job.status === "pending" || job.status === "running"
  );
  const hasActiveJobs = activeJobs.length > 0;

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Job Queue</CardTitle>
            <CardDescription>
              {hasActiveJobs
                ? `${activeJobs.length} active job${
                    activeJobs.length !== 1 ? "s" : ""
                  }`
                : "No active jobs"}
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchJobs}
            leftIcon={<RefreshCw className="w-4 h-4" />}
            aria-label="Refresh jobs"
          >
            Refresh
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        {error && (
          <Alert
            variant="error"
            title="Error loading jobs"
            description={error}
            dismissible
            onClose={() => setError(null)}
            className="mb-4"
          />
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Spinner size="lg" />
            <span className="ml-3 text-sm text-gray-600">Loading jobs...</span>
          </div>
        ) : jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Inbox
              className="w-12 h-12 text-gray-400 mb-3"
              aria-hidden="true"
            />
            <p className="text-sm font-medium text-gray-900">
              No jobs in queue
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Submit an async analysis to see jobs here
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {jobs.map((job) => (
              <div
                key={job.job_id}
                className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-medium text-gray-900 truncate">
                      Job {job.job_id.slice(0, 8)}
                    </span>
                  </div>

                  <JobStatusIndicator
                    jobId={job.job_id}
                    apiUrl={apiUrl}
                    showProgress={job.status === "running"}
                    showElapsedTime
                    onComplete={(result) =>
                      handleJobComplete(job.job_id, result)
                    }
                    onError={() => handleJobFailed(job.job_id)}
                  />
                </div>

                {(job.status === "pending" || job.status === "running") && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => cancelJob(job.job_id)}
                    isLoading={cancellingJobId === job.job_id}
                    leftIcon={<X className="w-4 h-4" />}
                    aria-label="Cancel job"
                    className="flex-shrink-0"
                  >
                    Cancel
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
