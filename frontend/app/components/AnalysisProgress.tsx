"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Loader2, Clock } from "lucide-react";

interface ProgressUpdate {
  status: "running" | "completed" | "failed";
  phase: string;
  phase_name: string;
  phase_num: number;
  total_phases: number;
  progress: number;
  current_agents: string[];
  completed_agents: string[];
  message: string;
  estimated_seconds_remaining?: number;
  timestamp?: string;
  error?: string;
}

interface AnalysisProgressProps {
  reportId: string;
  apiUrl?: string;
  onComplete?: () => void;
  onError?: (error: string) => void;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  reportId,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  onComplete,
  onError,
}) => {
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!reportId) return;

    // Connect to SSE endpoint
    const eventSource = new EventSource(
      `${apiUrl}/analyze/${reportId}/progress`
    );
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const data: ProgressUpdate = JSON.parse(event.data);
        setProgress(data);
        setError(null);

        if (data.status === "completed") {
          eventSource.close();
          onComplete?.();
        } else if (data.status === "failed") {
          eventSource.close();
          const errorMsg = data.error || "Analysis failed";
          setError(errorMsg);
          onError?.(errorMsg);
        }
      } catch (err) {
        console.error("Failed to parse progress update:", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE connection error:", err);
      // Don't close on error - might be temporary network issue
    };

    return () => {
      eventSource.close();
    };
  }, [reportId, apiUrl, onComplete, onError]);

  if (error) {
    return (
      <div className="w-full p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-sm text-red-600 font-medium">Error: {error}</p>
      </div>
    );
  }

  if (!progress) {
    return (
      <div className="w-full p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <div className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
          <span className="text-sm text-gray-600">Connecting to progress stream...</span>
        </div>
      </div>
    );
  }

  const formatTime = (seconds?: number): string => {
    if (!seconds) return "";
    if (seconds < 60) return `~${seconds}s remaining`;
    const minutes = Math.ceil(seconds / 60);
    return `~${minutes} min remaining`;
  };

  const getPhaseColor = (phaseNum: number): string => {
    const colors = {
      1: "bg-blue-500",
      2: "bg-purple-500",
      3: "bg-green-500",
    };
    return colors[phaseNum as keyof typeof colors] || "bg-gray-500";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full space-y-4"
    >
      {/* Phase Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-full ${getPhaseColor(progress.phase_num)} text-white flex items-center justify-center text-sm font-bold`}>
            {progress.phase_num}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900">
              {progress.phase_name || "Processing..."}
            </h3>
            <p className="text-xs text-gray-500">
              Phase {progress.phase_num} of {progress.total_phases}
            </p>
          </div>
        </div>
        {progress.estimated_seconds_remaining && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            <span>{formatTime(progress.estimated_seconds_remaining)}</span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-gray-700">
            {progress.message || "Processing..."}
          </span>
          <span className="text-xs font-medium text-gray-700">
            {progress.progress}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
          <motion.div
            className="bg-blue-600 h-2.5 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress.progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Active Agents */}
      {progress.current_agents.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium text-gray-700">Active:</p>
          <div className="flex flex-wrap gap-2">
            {progress.current_agents.map((agent) => (
              <div
                key={agent}
                className="flex items-center gap-1.5 px-2 py-1 bg-blue-50 border border-blue-200 rounded-md"
              >
                <Loader2 className="w-3 h-3 animate-spin text-blue-600" />
                <span className="text-xs text-blue-700">{agent}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Agents */}
      {progress.completed_agents.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium text-gray-700">Completed:</p>
          <div className="flex flex-wrap gap-2">
            {progress.completed_agents.map((agent) => (
              <div
                key={agent}
                className="flex items-center gap-1.5 px-2 py-1 bg-green-50 border border-green-200 rounded-md"
              >
                <CheckCircle2 className="w-3 h-3 text-green-600" />
                <span className="text-xs text-green-700">{agent}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Phase Progress Indicators */}
      <div className="flex items-center gap-2 pt-2 border-t border-gray-200">
        {[1, 2, 3].map((phaseNum) => (
          <div
            key={phaseNum}
            className={`flex-1 h-1.5 rounded-full ${
              phaseNum < progress.phase_num
                ? "bg-green-500"
                : phaseNum === progress.phase_num
                ? getPhaseColor(phaseNum)
                : "bg-gray-200"
            }`}
          />
        ))}
      </div>
    </motion.div>
  );
};


