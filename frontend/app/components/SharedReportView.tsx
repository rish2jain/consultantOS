"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './Card';
import { MetricCard } from './MetricCard';
import { Button } from './Button';
import { Input } from './Input';
import { Alert } from './Alert';
import { Spinner, InlineLoading } from './Spinner';
import { Download, Lock, AlertCircle, FileText, Calendar, TrendingUp, DollarSign, Users } from 'lucide-react';

export interface SharedReportViewProps {
  /** Share ID from URL */
  shareId: string;
  /** Optional password submit handler */
  onPasswordSubmit?: (password: string) => void;
}

interface ShareData {
  share_id: string;
  report_id: string;
  expires_at?: string;
  permissions: 'view' | 'download';
  password_required: boolean;
  access_count: number;
}

interface ReportData {
  company: string;
  industry: string;
  created_at: string;
  confidence_score?: number;
  analysis?: {
    market_analysis?: {
      trends?: string[];
      competitors?: string[];
    };
    financial_analysis?: {
      revenue?: number;
      market_cap?: number;
    };
    synthesis?: {
      executive_summary?: string;
      key_recommendations?: string[];
    };
  };
}

export const SharedReportView: React.FC<SharedReportViewProps> = ({
  shareId,
  onPasswordSubmit,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [passwordRequired, setPasswordRequired] = useState(false);
  const [password, setPassword] = useState('');
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  const [shareData, setShareData] = useState<ShareData | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    loadShareData();
  }, [shareId]);

  const loadShareData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/shares/${shareId}`);

      if (response.status === 401) {
        setPasswordRequired(true);
        setIsLoading(false);
        return;
      }

      if (response.status === 404) {
        setError('This share link does not exist or has expired');
        setIsLoading(false);
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to load shared report');
      }

      const data = await response.json();
      setShareData(data.share);
      setReportData(data.report);

      // Track view analytics
      trackView();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuthenticating(true);
    setError(null);

    try {
      const response = await fetch(`/api/shares/${shareId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });

      if (response.status === 401) {
        setError('Incorrect password');
        setIsAuthenticating(false);
        return;
      }

      if (!response.ok) {
        throw new Error('Authentication failed');
      }

      const data = await response.json();
      setShareData(data.share);
      setReportData(data.report);
      setPasswordRequired(false);
      onPasswordSubmit?.(password);

      // Track view analytics
      trackView();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const trackView = async () => {
    try {
      await fetch(`/api/analytics/shares/${shareId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event: 'view' }),
      });
    } catch (err) {
      // Analytics tracking is non-critical, fail silently
      console.error('Failed to track view:', err);
    }
  };

  const handleDownload = async () => {
    if (!shareData || shareData.permissions !== 'download') return;

    setIsDownloading(true);
    try {
      const response = await fetch(`/api/shares/${shareId}/download`, {
        method: 'GET',
        headers: password ? { 'X-Share-Password': password } : {},
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportData?.company || 'report'}-analysis.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      // Track download analytics (non-critical, fire-and-forget)
      fetch(`/api/analytics/shares/${shareId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event: 'download' }),
      }).catch((err) => {
        // Analytics failures should not interrupt the download flow
        console.error('Failed to track download analytics:', err);
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed');
    } finally {
      setIsDownloading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md text-center" padding="lg">
          <Spinner size="xl" className="mx-auto mb-4" />
          <p className="text-gray-600">Loading shared report...</p>
        </Card>
      </div>
    );
  }

  // Password required state
  if (passwordRequired) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md" padding="lg">
          <div className="mb-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-primary-100">
                <Lock className="w-5 h-5 text-primary-600" />
              </div>
              <div className="flex-1 min-w-0">
                <CardTitle className="mb-1">Password Required</CardTitle>
                <p className="text-sm text-gray-600">
                  This report is password protected. Enter the password to view.
                </p>
              </div>
            </div>
          </div>

          {error && (
            <Alert
              variant="error"
              description={error}
              dismissible
              onClose={() => setError(null)}
              className="mb-4"
            />
          )}

          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <Input
              type="password"
              label="Password"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              fullWidth
              required
              autoFocus
              leftIcon={<Lock className="w-4 h-4" />}
            />

            <Button
              type="submit"
              variant="primary"
              fullWidth
              isLoading={isAuthenticating}
              disabled={!password.trim()}
            >
              Access Report
            </Button>
          </form>
        </Card>
      </div>
    );
  }

  // Error state
  if (error && !reportData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md text-center" padding="lg">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Unable to Load Report
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button
            variant="primary"
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
        </Card>
      </div>
    );
  }

  // Report content
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <Card padding="lg">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-6 h-6 text-primary-600" />
                <CardTitle>{reportData?.company} Analysis</CardTitle>
              </div>
              <p className="text-gray-600">{reportData?.industry}</p>
              {reportData?.created_at && (
                <p className="text-sm text-gray-500 mt-1 flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  Generated: {formatDate(reportData.created_at)}
                </p>
              )}
            </div>

            <div className="flex items-center gap-3">
              {shareData?.expires_at && (
                <Alert
                  variant="warning"
                  description={`Expires: ${formatDate(shareData.expires_at)}`}
                  showIcon={false}
                  className="text-sm py-2"
                />
              )}

              {shareData?.permissions === 'download' && (
                <Button
                  variant="primary"
                  onClick={handleDownload}
                  isLoading={isDownloading}
                  leftIcon={<Download className="w-4 h-4" />}
                >
                  Download PDF
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* Key Metrics */}
        {reportData?.analysis && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {reportData.confidence_score !== undefined && (
              <MetricCard
                title="Confidence Score"
                value={`${Math.round(reportData.confidence_score * 100)}%`}
                icon={<TrendingUp className="w-5 h-5" />}
                trend={reportData.confidence_score >= 0.7 ? 'up' : undefined}
              />
            )}

            {reportData.analysis.financial_analysis?.revenue && (
              <MetricCard
                title="Revenue"
                value={`$${(reportData.analysis.financial_analysis.revenue / 1000000).toFixed(1)}M`}
                icon={<DollarSign className="w-5 h-5" />}
              />
            )}

            {reportData.analysis.market_analysis?.competitors && (
              <MetricCard
                title="Competitors Analyzed"
                value={reportData.analysis.market_analysis.competitors.length.toString()}
                icon={<Users className="w-5 h-5" />}
              />
            )}
          </div>
        )}

        {/* Executive Summary */}
        {reportData?.analysis?.synthesis?.executive_summary && (
          <Card padding="lg">
            <CardHeader>
              <CardTitle>Executive Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 whitespace-pre-wrap">
                {reportData.analysis.synthesis.executive_summary}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Key Recommendations */}
        {reportData?.analysis?.synthesis?.key_recommendations && (
          <Card padding="lg">
            <CardHeader>
              <CardTitle>Key Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {reportData.analysis.synthesis.key_recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 text-primary-600 text-sm font-semibold flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Market Trends */}
        {reportData?.analysis?.market_analysis?.trends && (
          <Card padding="lg">
            <CardHeader>
              <CardTitle>Market Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {reportData.analysis.market_analysis.trends.map((trend, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                  >
                    {trend}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer Info */}
        <Card padding="md" variant="filled">
          <p className="text-xs text-gray-600 text-center">
            This report was shared via ConsultantOS. View count: {shareData?.access_count || 0}
          </p>
        </Card>
      </div>
    </div>
  );
};
export default SharedReportView;
