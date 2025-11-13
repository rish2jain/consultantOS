"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  X, 
  ChevronDown, 
  ChevronUp,
  ExternalLink,
  CheckCircle2
} from 'lucide-react';
import { Badge } from './Badge';
import { Button } from './Button';

export interface AlertCardProps {
  /** Alert title */
  title: string;
  /** Alert summary/description */
  summary: string;
  /** Alert severity */
  severity?: 'info' | 'warning' | 'critical';
  /** Confidence score (0-1) */
  confidence?: number;
  /** Timestamp */
  timestamp: string;
  /** Whether alert is unread */
  unread?: boolean;
  /** Change details */
  changes?: Array<{
    change_type: string;
    title: string;
    description: string;
    confidence: number;
  }>;
  /** Source URLs */
  sourceUrls?: string[];
  /** Mark as read handler */
  onMarkRead?: () => void;
  /** Dismiss handler */
  onDismiss?: () => void;
  /** Investigate handler */
  onInvestigate?: () => void;
  /** Expandable content */
  expandable?: boolean;
}

const severityConfig = {
  info: {
    icon: Info,
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-900',
    iconColor: 'text-blue-600',
    badgeVariant: 'info' as const,
  },
  warning: {
    icon: AlertTriangle,
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    textColor: 'text-yellow-900',
    iconColor: 'text-yellow-600',
    badgeVariant: 'warning' as const,
  },
  critical: {
    icon: AlertCircle,
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-900',
    iconColor: 'text-red-600',
    badgeVariant: 'danger' as const,
  },
};

export const AlertCard: React.FC<AlertCardProps> = ({
  title,
  summary,
  severity = 'info',
  confidence,
  timestamp,
  unread = false,
  changes = [],
  sourceUrls = [],
  onMarkRead,
  onDismiss,
  onInvestigate,
  expandable = true,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const config = severityConfig[severity];
  const Icon = config.icon;

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={`
        border rounded-lg transition-all duration-200
        ${config.bgColor} ${config.borderColor}
        ${unread ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}
        ${expandable ? 'cursor-pointer' : ''}
        hover:shadow-md
      `}
      onClick={() => expandable && setIsExpanded(!isExpanded)}
    >
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className={`${config.iconColor} flex-shrink-0 mt-0.5`}>
              <Icon className="w-5 h-5" />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2 mb-1">
                <h4 className={`font-semibold text-sm ${config.textColor} truncate`}>
                  {title}
                </h4>
                {unread && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0 mt-1.5"
                  />
                )}
              </div>
              
              <p className={`text-sm ${config.textColor} opacity-90 mb-2 line-clamp-2`}>
                {summary}
              </p>

              <div className="flex items-center gap-2 flex-wrap">
                <span className={`text-xs ${config.textColor} opacity-75`}>
                  {formatDate(timestamp)}
                </span>
                {confidence !== undefined && (
                  <Badge variant={config.badgeVariant} size="sm">
                    {(confidence * 100).toFixed(0)}% confidence
                  </Badge>
                )}
                {changes.length > 0 && (
                  <Badge variant="default" size="sm">
                    {changes.length} change{changes.length !== 1 ? 's' : ''}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {expandable && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className={`${config.iconColor} flex-shrink-0`}
            >
              {isExpanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </motion.button>
          )}
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden mt-4 pt-4 border-t border-current border-opacity-20"
            >
              {changes.length > 0 && (
                <div className="mb-4">
                  <h5 className={`text-xs font-semibold ${config.textColor} mb-2`}>
                    Changes Detected:
                  </h5>
                  <div className="space-y-2">
                    {changes.map((change, idx) => (
                      <div
                        key={idx}
                        className={`p-2 rounded ${config.bgColor} border ${config.borderColor}`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className={`text-xs font-medium ${config.textColor}`}>
                            {change.title}
                          </span>
                          <Badge variant={config.badgeVariant} size="sm">
                            {(change.confidence * 100).toFixed(0)}%
                          </Badge>
                        </div>
                        <p className={`text-xs ${config.textColor} opacity-75`}>
                          {change.description}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {sourceUrls.length > 0 && (
                <div className="mb-4">
                  <h5 className={`text-xs font-semibold ${config.textColor} mb-2`}>
                    Sources:
                  </h5>
                  <div className="space-y-1">
                    {sourceUrls.slice(0, 3).map((url, idx) => (
                      <a
                        key={idx}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`text-xs ${config.textColor} opacity-75 hover:opacity-100 flex items-center gap-1 underline`}
                        onClick={(e) => e.stopPropagation()}
                      >
                        {url}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2 flex-wrap">
                {onMarkRead && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      onMarkRead();
                    }}
                    className="text-xs"
                  >
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Mark Read
                  </Button>
                )}
                {onInvestigate && (
                  <Button
                    size="sm"
                    variant="primary"
                    onClick={(e) => {
                      e.stopPropagation();
                      onInvestigate();
                    }}
                    className="text-xs"
                  >
                    Investigate
                  </Button>
                )}
                {onDismiss && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDismiss();
                    }}
                    className="text-xs"
                  >
                    <X className="w-3 h-3 mr-1" />
                    Dismiss
                  </Button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

