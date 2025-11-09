"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  AnalysisRequestForm,
  AsyncAnalysisForm,
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
  Alert,
  Badge,
  Button,
  JobStatusIndicator,
} from '@/app/components';
import { api } from '@/lib/api';
import {
  Rocket,
  Clock,
  TrendingUp,
  Zap,
  CheckCircle,
  AlertCircle,
  FileText,
  Lightbulb,
} from 'lucide-react';

interface RecentAnalysis {
  id: string;
  company: string;
  industry: string;
  frameworks: string[];
  timestamp: string;
  status: 'completed' | 'pending' | 'failed';
}

export default function AnalysisPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('quick');
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([]);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [reportId, setReportId] = useState<string | null>(null);

  // Load recent analyses from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('recent_analyses');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setRecentAnalyses(parsed.slice(0, 3)); // Show last 3
      } catch (error) {
        console.error('Failed to parse recent analyses:', error);
      }
    }
  }, []);

  // Save analysis to recent list
  const saveToRecent = (analysis: Omit<RecentAnalysis, 'timestamp'>) => {
    const newAnalysis: RecentAnalysis = {
      ...analysis,
      timestamp: new Date().toISOString(),
    };

    const updated = [newAnalysis, ...recentAnalyses].slice(0, 10);
    setRecentAnalyses(updated.slice(0, 3));
    localStorage.setItem('recent_analyses', JSON.stringify(updated));
  };

  // Handle sync analysis success
  const handleSyncSuccess = (reportData: any) => {
    const reportId = reportData.report_id || reportData.id;
    setReportId(reportId);
    setSuccessMessage(`Analysis completed successfully! Redirecting to report...`);
    setErrorMessage('');

    // Save to recent
    saveToRecent({
      id: reportId,
      company: reportData.company || 'Unknown',
      industry: reportData.industry || 'Unknown',
      frameworks: reportData.frameworks || [],
      status: 'completed',
    });

    // Redirect after brief delay
    setTimeout(() => {
      router.push(`/reports/${reportId}`);
    }, 1500);
  };

  // Handle sync analysis error
  const handleSyncError = (error: Error) => {
    setErrorMessage(error.message || 'Failed to generate analysis. Please try again.');
    setSuccessMessage('');
  };

  // Handle async job submission
  const handleAsyncJobSubmitted = (jobId: string) => {
    setCurrentJobId(jobId);
    setSuccessMessage(`Analysis job submitted! Job ID: ${jobId}`);
    setErrorMessage('');

    // Optionally redirect to jobs page
    setTimeout(() => {
      router.push(`/jobs?id=${jobId}`);
    }, 2000);
  };

  // Handle async submission error
  const handleAsyncError = (error: string) => {
    setErrorMessage(error);
    setSuccessMessage('');
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hr ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
            <Rocket className="w-8 h-8 text-primary-600" aria-hidden="true" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Request Strategic Analysis
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Generate McKinsey-grade business framework analyses powered by AI.
            Choose between instant analysis or background processing for complex reports.
          </p>
        </div>

        {/* Global Success/Error Messages */}
        {successMessage && (
          <div className="max-w-4xl mx-auto mb-6">
            <Alert
              variant="success"
              showIcon
              dismissible
              onClose={() => setSuccessMessage('')}
            >
              <strong>Success!</strong> {successMessage}
            </Alert>
          </div>
        )}

        {errorMessage && (
          <div className="max-w-4xl mx-auto mb-6">
            <Alert
              variant="error"
              showIcon
              dismissible
              onClose={() => setErrorMessage('')}
            >
              <strong>Error:</strong> {errorMessage}
            </Alert>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Analysis Forms */}
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabList className="mb-6">
                <Tab value="quick">
                  <Zap className="w-4 h-4 mr-2" aria-hidden="true" />
                  Quick Analysis
                </Tab>
                <Tab value="batch">
                  <Clock className="w-4 h-4 mr-2" aria-hidden="true" />
                  Batch Analysis
                </Tab>
              </TabList>

              <TabPanels>
                {/* Quick Analysis Tab */}
                <TabPanel value="quick">
                  <div className="mb-4">
                    <Alert variant="info" showIcon>
                      <strong>Quick Analysis:</strong> Get results immediately. Best for
                      1-2 frameworks and standard depth. Processing time: 2-5 minutes.
                    </Alert>
                  </div>
                  <AnalysisRequestForm
                    onSuccess={handleSyncSuccess}
                    onError={handleSyncError}
                    async={false}
                  />
                </TabPanel>

                {/* Batch Analysis Tab */}
                <TabPanel value="batch">
                  <div className="mb-4">
                    <Alert variant="info" showIcon>
                      <strong>Batch Analysis:</strong> Submit multiple analyses or complex
                      reports. Jobs are processed in the background. You'll be notified
                      when complete.
                    </Alert>
                  </div>

                  <AsyncAnalysisForm
                    onJobSubmitted={handleAsyncJobSubmitted}
                    onError={handleAsyncError}
                  />

                  {/* Show job status if available */}
                  {currentJobId && (
                    <div className="mt-6">
                      <JobStatusIndicator jobId={currentJobId} autoRefresh />
                    </div>
                  )}
                </TabPanel>
              </TabPanels>
            </Tabs>
          </div>

          {/* Right Column - Recent Analyses & Tips */}
          <div className="space-y-6">
            {/* Recent Analyses */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-primary-600" aria-hidden="true" />
                  Recent Analyses
                </CardTitle>
                <CardDescription>
                  Your most recent analysis requests
                </CardDescription>
              </CardHeader>
              <CardContent>
                {recentAnalyses.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-3 text-gray-400" aria-hidden="true" />
                    <p className="text-sm">No recent analyses yet</p>
                    <p className="text-xs mt-1">
                      Submit your first analysis to get started
                    </p>
                  </div>
                ) : (
                  <ul className="space-y-3" role="list">
                    {recentAnalyses.map((analysis, index) => (
                      <li
                        key={`${analysis.id}-${index}`}
                        className="border-l-4 border-primary-500 pl-4 py-2 hover:bg-gray-50 transition-colors cursor-pointer rounded-r"
                        onClick={() => {
                          if (analysis.status === 'completed') {
                            router.push(`/reports/${analysis.id}`);
                          }
                        }}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {analysis.company}
                            </p>
                            <p className="text-xs text-gray-500 truncate">
                              {analysis.industry}
                            </p>
                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                              {analysis.frameworks.slice(0, 2).map((framework) => (
                                <Badge
                                  key={framework}
                                  variant="secondary"
                                  size="sm"
                                >
                                  {framework}
                                </Badge>
                              ))}
                              {analysis.frameworks.length > 2 && (
                                <span className="text-xs text-gray-400">
                                  +{analysis.frameworks.length - 2} more
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex flex-col items-end ml-3">
                            {analysis.status === 'completed' && (
                              <CheckCircle className="w-4 h-4 text-green-500 mb-1" aria-label="Completed" />
                            )}
                            {analysis.status === 'pending' && (
                              <Clock className="w-4 h-4 text-yellow-500 mb-1" aria-label="Pending" />
                            )}
                            {analysis.status === 'failed' && (
                              <AlertCircle className="w-4 h-4 text-red-500 mb-1" aria-label="Failed" />
                            )}
                            <span className="text-xs text-gray-400 whitespace-nowrap">
                              {formatTimestamp(analysis.timestamp)}
                            </span>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}

                {recentAnalyses.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <Button
                      variant="outline"
                      size="sm"
                      fullWidth
                      onClick={() => router.push('/reports')}
                    >
                      View All Reports
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Helpful Tips */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" aria-hidden="true" />
                  Helpful Tips
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-sm text-gray-700" role="list">
                  <li className="flex items-start">
                    <span className="inline-block w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 mr-2 flex-shrink-0" aria-hidden="true"></span>
                    <span>
                      <strong>Quick Analysis:</strong> Best for 1-2 frameworks with standard
                      depth. Get results in 2-5 minutes.
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="inline-block w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 mr-2 flex-shrink-0" aria-hidden="true"></span>
                    <span>
                      <strong>Deep Analysis:</strong> Use batch mode for comprehensive
                      reports with 3+ frameworks. Processing takes 15-30 minutes.
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="inline-block w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 mr-2 flex-shrink-0" aria-hidden="true"></span>
                    <span>
                      <strong>Additional Context:</strong> Provide specific questions or
                      focus areas for more targeted insights.
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="inline-block w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 mr-2 flex-shrink-0" aria-hidden="true"></span>
                    <span>
                      <strong>Region Targeting:</strong> Specify geographic focus for
                      localized market analysis.
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="inline-block w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 mr-2 flex-shrink-0" aria-hidden="true"></span>
                    <span>
                      <strong>Framework Mix:</strong> Combine complementary frameworks
                      (e.g., Porter + SWOT) for comprehensive strategic view.
                    </span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Framework Quick Reference */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Framework Guide</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-xs text-gray-600" role="list">
                  <li>
                    <strong className="text-gray-900">Porter's 5 Forces:</strong> Industry
                    competitive analysis
                  </li>
                  <li>
                    <strong className="text-gray-900">SWOT:</strong> Internal strengths &
                    weaknesses, external opportunities & threats
                  </li>
                  <li>
                    <strong className="text-gray-900">PESTEL:</strong> Political,
                    Economic, Social, Technological, Environmental, Legal factors
                  </li>
                  <li>
                    <strong className="text-gray-900">Blue Ocean:</strong> Uncontested
                    market space creation
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
