"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play,
  Pause,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle2,
  Clock,
  Activity,
} from "lucide-react";
import { Badge } from "./Badge";
import { Button } from "./Button";

export interface MonitorRowProps {
  monitor: {
    id: string;
    company: string;
    industry: string;
    status: "active" | "paused" | "deleted" | "error";
    config: {
      frequency: string;
      frameworks: string[];
    };
    last_check?: string;
    next_check?: string;
    total_alerts: number;
    error_count: number;
    last_error?: string;
  };
  onPause?: () => void;
  onResume?: () => void;
  onCheckNow?: () => void;
  expandable?: boolean;
}

const statusConfig = {
  active: {
    icon: CheckCircle2,
    color: "text-green-600",
    bgColor: "bg-green-100",
    badgeVariant: "success" as const,
  },
  paused: {
    icon: Pause,
    color: "text-yellow-600",
    bgColor: "bg-yellow-100",
    badgeVariant: "warning" as const,
  },
  error: {
    icon: AlertCircle,
    color: "text-red-600",
    bgColor: "bg-red-100",
    badgeVariant: "danger" as const,
  },
  deleted: {
    icon: AlertCircle,
    color: "text-gray-600",
    bgColor: "bg-gray-100",
    badgeVariant: "default" as const,
  },
};

export const MonitorRow: React.FC<MonitorRowProps> = ({
  monitor,
  onPause,
  onResume,
  onCheckNow,
  expandable = true,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const config = statusConfig[monitor.status];
  const StatusIcon = config.icon;

  const formatDate = (dateStr?: string): string => {
    // Check for undefined/null first
    if (!dateStr) return "Never";

    // Parse the date and check for invalid dates
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return "Never";

    // Check for future dates
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    if (diffMs <= 0) return "Just now";

    // Format valid past dates
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-b border-gray-200 last:border-b-0 hover:bg-gray-50 transition-colors"
    >
      <div
        className={`px-6 py-4 ${expandable ? "cursor-pointer" : ""}`}
        onClick={() => expandable && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className={`${config.color} flex-shrink-0 mt-0.5`}>
              <StatusIcon className="w-5 h-5" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1">
                <h3 className="text-lg font-medium text-gray-900 truncate">
                  {monitor.company}
                </h3>
                <Badge variant={config.badgeVariant} size="sm">
                  {monitor.status}
                </Badge>
              </div>

              <p className="text-sm text-gray-500 mb-2">{monitor.industry}</p>

              <div className="flex items-center gap-4 text-sm text-gray-600 flex-wrap">
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {monitor.config.frequency} checks
                </span>
                <span className="flex items-center gap-1">
                  <Activity className="w-4 h-4" />
                  {monitor.total_alerts} alerts
                </span>
                {monitor.last_check && (
                  <span className="flex items-center gap-1">
                    Last check: {formatDate(monitor.last_check)}
                  </span>
                )}
              </div>

              {monitor.error_count > 0 && monitor.last_error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-2 p-2 bg-red-50 rounded text-sm text-red-700 border border-red-200"
                >
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{monitor.last_error}</span>
                  </div>
                </motion.div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            {onCheckNow && (
              <Button
                size="sm"
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation();
                  onCheckNow();
                }}
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Check Now
              </Button>
            )}

            {monitor.status === "active" && onPause && (
              <Button
                size="sm"
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation();
                  onPause();
                }}
              >
                <Pause className="w-4 h-4 mr-1" />
                Pause
              </Button>
            )}

            {monitor.status === "paused" && onResume && (
              <Button
                size="sm"
                variant="primary"
                onClick={(e) => {
                  e.stopPropagation();
                  onResume();
                }}
              >
                <Play className="w-4 h-4 mr-1" />
                Resume
              </Button>
            )}

            {expandable && (
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={(e) => {
                  e.stopPropagation();
                  setIsExpanded(!isExpanded);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                {isExpanded ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </motion.button>
            )}
          </div>
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden mt-4 pt-4 border-t border-gray-200"
            >
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500 mb-1">Frameworks:</p>
                  <div className="flex flex-wrap gap-1">
                    {monitor.config.frameworks.map((framework, idx) => (
                      <Badge key={idx} variant="default" size="sm">
                        {framework}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-gray-500 mb-1">Next Check:</p>
                  <p className="text-gray-900">
                    {monitor.next_check
                      ? formatDate(monitor.next_check)
                      : "Not scheduled"}
                  </p>
                </div>
                {monitor.error_count > 0 && (
                  <div>
                    <p className="text-gray-500 mb-1">Error Count:</p>
                    <p className="text-red-600 font-medium">
                      {monitor.error_count} error
                      {monitor.error_count !== 1 ? "s" : ""}
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};
