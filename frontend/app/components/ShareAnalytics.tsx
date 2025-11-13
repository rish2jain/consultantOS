"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './Card';
import { MetricCard } from './MetricCard';
import { Alert } from './Alert';
import { Spinner, InlineLoading } from './Spinner';
import { Badge } from './Badge';
import {
  Eye,
  Download,
  Clock,
  TrendingUp,
  Globe,
  Calendar,
  Users,
  BarChart3,
} from 'lucide-react';

export interface ShareAnalyticsProps {
  /** Share ID to view analytics for */
  shareId: string;
}

interface AnalyticsData {
  share_id: string;
  total_views: number;
  total_downloads: number;
  last_accessed_at?: string;
  created_at: string;
  view_timeline: Array<{
    date: string;
    views: number;
  }>;
  geographic_distribution?: Array<{
    country: string;
    count: number;
  }>;
  hourly_distribution?: Array<{
    hour: number;
    count: number;
  }>;
  referrers?: Array<{
    source: string;
    count: number;
  }>;
}

export const ShareAnalytics: React.FC<ShareAnalyticsProps> = ({ shareId }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | 'all'>('7d');

  useEffect(() => {
    loadAnalytics();
  }, [shareId, timeRange]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/analytics/shares/${shareId}?range=${timeRange}`);

      if (!response.ok) {
        throw new Error('Failed to load analytics');
      }

      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDateShort = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getViewTrend = (): 'up' | 'down' | undefined => {
    if (!analytics?.view_timeline || analytics.view_timeline.length < 2) {
      return undefined;
    }

    const recent = analytics.view_timeline.slice(-3);
    const older = analytics.view_timeline.slice(-6, -3);

    const recentAvg = recent.reduce((sum, item) => sum + item.views, 0) / recent.length;
    const olderAvg = older.reduce((sum, item) => sum + item.views, 0) / older.length;

    if (recentAvg > olderAvg * 1.1) return 'up';
    if (recentAvg < olderAvg * 0.9) return 'down';
    return undefined;
  };

  const getMaxViews = () => {
    if (!analytics?.view_timeline) return 0;
    return Math.max(...analytics.view_timeline.map((item) => item.views), 1);
  };

  const getPeakHour = () => {
    if (!analytics?.hourly_distribution || analytics.hourly_distribution.length === 0) {
      return null;
    }

    const peak = analytics.hourly_distribution.reduce((max, item) =>
      item.count > max.count ? item : max
    );

    return peak.hour;
  };

  const formatHour = (hour: number) => {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
    return `${displayHour}${period}`;
  };

  if (isLoading) {
    return (
      <Card padding="lg">
        <InlineLoading message="Loading analytics..." centered />
      </Card>
    );
  }

  if (error || !analytics) {
    return (
      <Card padding="lg">
        <Alert
          variant="error"
          title="Error"
          description={error || 'Failed to load analytics data'}
        />
      </Card>
    );
  }

  const peakHour = getPeakHour();
  const viewTrend = getViewTrend();

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <Card padding="md">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Time Range</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setTimeRange('7d')}
              className={`
                px-3 py-1 text-sm rounded-md transition-colors
                ${
                  timeRange === '7d'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              7 Days
            </button>
            <button
              onClick={() => setTimeRange('30d')}
              className={`
                px-3 py-1 text-sm rounded-md transition-colors
                ${
                  timeRange === '30d'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              30 Days
            </button>
            <button
              onClick={() => setTimeRange('all')}
              className={`
                px-3 py-1 text-sm rounded-md transition-colors
                ${
                  timeRange === 'all'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              All Time
            </button>
          </div>
        </div>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Views"
          value={analytics.total_views.toString()}
          icon={<Eye className="w-5 h-5" />}
          trend={viewTrend}
        />

        <MetricCard
          title="Downloads"
          value={analytics.total_downloads.toString()}
          icon={<Download className="w-5 h-5" />}
        />

        <MetricCard
          title="Last Accessed"
          value={analytics.last_accessed_at ? 'Active' : 'Never'}
          subtitle={
            analytics.last_accessed_at
              ? formatDateShort(analytics.last_accessed_at)
              : undefined
          }
          icon={<Clock className="w-5 h-5" />}
        />

        <MetricCard
          title="Peak Hour"
          value={peakHour !== null ? formatHour(peakHour) : 'N/A'}
          icon={<TrendingUp className="w-5 h-5" />}
        />
      </div>

      {/* View Timeline Chart */}
      <Card padding="lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            View Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          {analytics.view_timeline && analytics.view_timeline.length > 0 ? (
            <div className="space-y-2">
              <div className="flex items-end gap-1 h-40">
                {analytics.view_timeline.map((item, index) => {
                  const maxViews = getMaxViews();
                  const height = maxViews > 0 ? (item.views / maxViews) * 100 : 0;

                  return (
                    <div key={index} className="flex-1 flex flex-col items-center gap-1">
                      <div className="flex-1 w-full flex items-end">
                        <div
                          className="w-full bg-primary-600 rounded-t transition-all hover:bg-primary-700"
                          style={{ height: `${height}%` }}
                          title={`${item.views} views`}
                        />
                      </div>
                      <span className="text-xs text-gray-500 transform -rotate-45 origin-top-left mt-2">
                        {formatDateShort(item.date)}
                      </span>
                    </div>
                  );
                })}
              </div>

              <div className="text-center text-sm text-gray-600 mt-6">
                Daily Views
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No view data available yet
            </div>
          )}
        </CardContent>
      </Card>

      {/* Geographic Distribution */}
      {analytics.geographic_distribution && analytics.geographic_distribution.length > 0 && (
        <Card padding="lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              Geographic Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analytics.geographic_distribution.slice(0, 10).map((location, index) => {
                const total = analytics.geographic_distribution!.reduce(
                  (sum, item) => sum + item.count,
                  0
                );
                const percentage = Math.round((location.count / total) * 100);

                return (
                  <div key={index} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-gray-900">
                        {location.country}
                      </span>
                      <span className="text-gray-600">
                        {location.count} ({percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Hourly Distribution */}
      {analytics.hourly_distribution && analytics.hourly_distribution.length > 0 && (
        <Card padding="lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Access by Hour of Day
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-12 gap-1">
              {analytics.hourly_distribution.map((item) => {
                const maxCount = Math.max(
                  ...analytics.hourly_distribution!.map((h) => h.count),
                  1
                );
                const intensity = Math.round((item.count / maxCount) * 100);

                return (
                  <div
                    key={item.hour}
                    className="flex flex-col items-center gap-1"
                    title={`${formatHour(item.hour)}: ${item.count} views`}
                  >
                    <div
                      className={`
                        w-full h-16 rounded transition-colors
                        ${
                          intensity > 66
                            ? 'bg-primary-600'
                            : intensity > 33
                            ? 'bg-primary-400'
                            : 'bg-primary-200'
                        }
                      `}
                      style={{ opacity: intensity / 100 }}
                    />
                    <span className="text-xs text-gray-500">
                      {item.hour}
                    </span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Referrers */}
      {analytics.referrers && analytics.referrers.length > 0 && (
        <Card padding="lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Traffic Sources
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {analytics.referrers.map((referrer, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-sm font-medium text-gray-900">
                    {referrer.source || 'Direct'}
                  </span>
                  <Badge variant="default">{referrer.count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Info */}
      <Card padding="md" variant="filled">
        <p className="text-xs text-gray-600 text-center">
          Share created on {formatDate(analytics.created_at)} • Last updated:{' '}
          {analytics.last_accessed_at ? formatDate(analytics.last_accessed_at) : 'Never'}
        </p>
      </Card>
    </div>
  );
};
export default ShareAnalytics;
