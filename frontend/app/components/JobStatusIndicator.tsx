"use client";

import React, { useEffect, useState, useCallback, useRef } from "react";
import { Badge } from "./Badge";
import { Spinner } from "./Spinner";
import { Clock, CheckCircle, XCircle, Loader2 } from "lucide-react";

export interface JobStatus {
  job_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress?: number;
  created_at: string;
  updated_at: string;
  company?: string;
  result?: any;
  error?: string;
}

export interface JobStatusIndicatorProps {
  /** Job ID to monitor */
  jobId: string;
  /** API base URL */
  apiUrl?: string;
  /** Polling interval in milliseconds (default: 3000ms = 3s) */
  pollingInterval?: number;
  /** Show progress bar */
  showProgress?: boolean;
  /** Show elapsed time */
  showElapsedTime?: boolean;
  /** Callback when job status changes */
  onStatusChange?: (status: JobStatus) => void;
  /** Callback when job completes */
  onComplete?: (result: any) => void;
  /** Callback when job fails */
  onError?: (error: string) => void;
  /** Custom className */
  className?: string;
}

const statusConfig = {
  pending: {
    variant: "default" as const,
    icon: Clock,
    label: "Pending",
    color: "text-gray-600",
  },
  running: {
    variant: "info" as const,
    icon: Loader2,
    label: "Running",
    color: "text-blue-600",
  },
  completed: {
    variant: "success" as const,
    icon: CheckCircle,
    label: "Completed",
    color: "text-green-600",
  },
  failed: {
    variant: "danger" as const,
    icon: XCircle,
    label: "Failed",
    color: "text-red-600",
  },
};

export const JobStatusIndicator: React.FC<JobStatusIndicatorProps> = ({
  jobId,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  pollingInterval = 3000,
  showProgress = true,
  showElapsedTime = true,
  onStatusChange,
  onComplete,
  onError,
  className = "",
}) => {
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [isPolling, setIsPolling] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState<number>(0);

  // Use refs to store callbacks to avoid dependency issues
  const onStatusChangeRef = useRef(onStatusChange);
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);

  // Update refs when callbacks change
  useEffect(() => {
    onStatusChangeRef.current = onStatusChange;
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  }, [onStatusChange, onComplete, onError]);

  const fetchJobStatus = useCallback(async () => {
    try {
      const response = await fetch(`${apiUrl}/jobs/${jobId}/status`);

      if (!response.ok) {
        throw new Error(`Failed to fetch job status: ${response.statusText}`);
      }

      const data: JobStatus = await response.json();
      setStatus(data);
      setError(null);

      if (data.status === "completed") {
        setIsPolling(false);
      } else if (data.status === "failed") {
        setIsPolling(false);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      setIsPolling(false);
    }
  }, [jobId, apiUrl]);

  // Separate effect to handle callbacks when status changes
  useEffect(() => {
    if (!status) return;

    onStatusChangeRef.current?.(status);

    if (status.status === "completed") {
      onCompleteRef.current?.(status.result);
    } else if (status.status === "failed") {
      onErrorRef.current?.(status.error || "Job failed");
    }
  }, [status]);

  // Initial fetch and polling
  useEffect(() => {
    fetchJobStatus();

    if (isPolling) {
      const intervalId = setInterval(fetchJobStatus, pollingInterval);
      return () => clearInterval(intervalId);
    }
    return undefined;
  }, [fetchJobStatus, isPolling, pollingInterval]);

  // Elapsed time counter
  useEffect(() => {
    if (
      !status ||
      status.status === "completed" ||
      status.status === "failed"
    ) {
      return;
    }

    const startTime = new Date(status.created_at).getTime();
    const updateElapsed = () => {
      const now = Date.now();
      setElapsedTime(Math.floor((now - startTime) / 1000));
    };

    updateElapsed();
    const timerId = setInterval(updateElapsed, 1000);
    return () => clearInterval(timerId);
  }, [status]);

  if (error) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Badge variant="danger" dot>
          Error loading status
        </Badge>
        <span className="text-sm text-red-600">{error}</span>
      </div>
    );
  }

  if (!status) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Spinner size="sm" />
        <span className="text-sm text-gray-600">Loading status...</span>
      </div>
    );
  }

  const config = statusConfig[status.status];
  const IconComponent = config.icon;
  const progress = status.progress || 0;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-3">
        <Badge variant={config.variant} dot>
          <IconComponent
            className={`w-3 h-3 ${config.color} ${
              status.status === "running" ? "animate-spin" : ""
            }`}
            aria-hidden="true"
          />
          {config.label}
        </Badge>

        {status.company && (
          <span className="text-sm text-gray-600">{status.company}</span>
        )}

        {showElapsedTime &&
          (status.status === "running" || status.status === "pending") && (
            <span className="text-xs text-gray-500">
              {formatElapsedTime(elapsedTime)}
            </span>
          )}
      </div>

      {showProgress && status.status === "running" && (
        <div className="w-full">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium text-gray-700">Progress</span>
            <span className="text-xs font-medium text-gray-700">
              {progress}%
            </span>
          </div>
          <div
            className="w-full bg-gray-200 rounded-full h-2 overflow-hidden"
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Job progress"
          >
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {status.status === "failed" && status.error && (
        <p className="text-xs text-red-600 mt-1">{status.error}</p>
      )}
    </div>
  );
};

// Helper function to format elapsed time
function formatElapsedTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
}
