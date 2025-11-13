"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  MetricCard,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Button,
  Badge,
  ShareDialog,
  CommentThread,
  CommentForm,
  VersionHistory,
  VersionComparison,
  Alert,
  Spinner,
  LoadingOverlay,
  Tooltip,
  Breadcrumb,
} from "@/app/components";
import { transformReportData } from "@/app/utils/reportTransformers";
import { api } from "@/lib/api";
import { isSWOTPlaceholder, isPorterPlaceholder, getPlaceholderMessage } from "@/lib/analysis-utils";
import {
  Share2,
  Download,
  Trash2,
  Calendar,
  Building2,
  FileText,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  ArrowLeft,
  Info,
} from "lucide-react";

interface ReportData {
  id: string;
  company: string;
  industry: string;
  created_at: string;
  frameworks: string[];
  depth: "quick" | "standard" | "deep";
  confidence_score: number;
  status: "completed" | "partial_success" | "failed";
  executive_summary?: string;
  key_findings?: string[];
  recommendations?: string[];
  analysis?: {
    porter?: {
      competitive_rivalry: string;
      supplier_power: string;
      buyer_power: string;
      threat_of_substitution: string;
      threat_of_new_entry: string;
      overall_assessment: string;
    };
    swot?: {
      strengths: string[];
      weaknesses: string[];
      opportunities: string[];
      threats: string[];
    };
    pestel?: {
      political: string;
      economic: string;
      social: string;
      technological: string;
      environmental: string;
      legal: string;
    };
    blue_ocean?: {
      eliminate: string[];
      reduce: string[];
      raise: string[];
      create: string[];
    };
    market_insights?: {
      trends: string[];
      key_findings: string[];
    };
    financial_insights?: {
      metrics: Record<string, any>;
      key_findings: string[];
    };
  };
  pdf_url?: string;
}

interface Comment {
  id: string;
  text: string;
  user: {
    id: string;
    name: string;
  };
  created_at: string;
  updated_at?: string;
  parent_id?: string;
  replies?: Comment[];
}

interface Version {
  id: string;
  version_number: number;
  created_at: string;
  created_by: string;
  change_summary: string;
  is_current: boolean;
}

const extractExecutiveSummary = (data: any): string | undefined => {
  if (!data) return undefined;
  const summary = data.executive_summary;
  if (!summary) return undefined;
  if (typeof summary === "string") {
    return summary.trim() ? summary : undefined;
  }

  const parts = [
    summary.summary,
    summary.overview,
    summary.strategic_recommendation,
  ]
    .filter((part) => typeof part === "string" && part.trim())
    .map((part) => part.trim());

  if (Array.isArray(summary.supporting_evidence)) {
    const evidence = summary.supporting_evidence
      .filter((item: unknown) => typeof item === "string" && item.trim())
      .map((item: string) => `• ${item.trim()}`);
    if (evidence.length) {
      parts.push(evidence.join("\n"));
    }
  }

  return parts.length ? parts.join("\n\n") : undefined;
};

const extractKeyFindings = (data: any): string[] => {
  if (Array.isArray(data?.key_findings) && data.key_findings.length) {
    return data.key_findings;
  }
  if (
    Array.isArray(data?.executive_summary?.key_findings) &&
    data.executive_summary.key_findings.length
  ) {
    return data.executive_summary.key_findings;
  }
  return [];
};

const extractRecommendations = (data: any): string[] => {
  if (Array.isArray(data?.recommendations) && data.recommendations.length) {
    return data.recommendations;
  }
  if (
    Array.isArray(data?.executive_summary?.next_steps) &&
    data.executive_summary.next_steps.length
  ) {
    return data.executive_summary.next_steps;
  }
  return [];
};

export default function ReportDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  // Unwrap the params Promise using React.use()
  const { id } = use(params);
  
  const router = useRouter();
  const [report, setReport] = useState<ReportData | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [showVersionComparison, setShowVersionComparison] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [activeFramework, setActiveFramework] = useState<string | 'all'>('all');
  const [isDeleting, setIsDeleting] = useState(false);
  
  // Breadcrumb items
  const breadcrumbItems = [
    { label: 'Reports', href: '/reports' },
    { label: report?.company || 'Report Details' },
  ];

  useEffect(() => {
    loadReport();
    loadComments();
    loadVersions();
  }, [id]);

  const loadReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const data: any = await api.analysis.getReport(id);
      const baseReport = transformReportData(data, id);

      const transformedData: ReportData = {
        ...baseReport,
        depth: (data.depth as ReportData['depth']) || baseReport.depth || 'standard',
        executive_summary: extractExecutiveSummary(data),
        key_findings: extractKeyFindings(data),
        recommendations: extractRecommendations(data),
        analysis: baseReport.analysis,
      };

      setReport(transformedData);
      // Reset framework filter when report changes
      setActiveFramework('all');
    } catch (err: any) {
      setError(
        err?.message || "Failed to load report. Please try again later."
      );
    } finally {
      setLoading(false);
    }
  };

  const loadComments = async () => {
    try {
      const data = await api.comments.list(id);
      setComments(data.comments || []);
    } catch (err) {
      console.error("Failed to load comments:", err);
    }
  };

  const loadVersions = async () => {
    try {
      const data = await api.versions.list(id);
      setVersions(data.versions || []);
    } catch (err) {
      console.error("Failed to load versions:", err);
    }
  };

  const handleShareSuccess = (shareLink: string) => {
    // Optional: Show success toast or notification
    console.log("Share link created:", shareLink);
  };

  const handleDownloadPDF = async () => {
    if (!report?.pdf_url) {
      setError("PDF is not available for this report");
      return;
    }

    try {
      // If pdf_url is a relative path (download endpoint), construct full URL
      const downloadUrl = report.pdf_url.startsWith('/') 
        ? `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}${report.pdf_url}`
        : report.pdf_url;
      
      // Open in new tab for download
      window.open(downloadUrl, "_blank");
    } catch (err) {
      setError("Failed to download PDF");
    }
  };

  const handleDeleteReport = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this report? This action cannot be undone."
    );

    if (!confirmed) return;

    try {
      setIsDeleting(true);
      await api.analysis.deleteReport(id);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to delete report");
      setIsDeleting(false);
    }
  };

  const handleAddComment = async (text: string) => {
    try {
      await api.comments.create(id, text);
      await loadComments();
    } catch (err: any) {
      throw new Error(err.message || "Failed to add comment");
    }
  };

  const handleReplyComment = async (commentId: string, text: string) => {
    try {
      await api.comments.reply(commentId, text);
      await loadComments();
    } catch (err: any) {
      throw new Error(err.message || "Failed to reply to comment");
    }
  };

  const handleEditComment = async (commentId: string, text: string) => {
    try {
      await api.comments.update(commentId, text);
      await loadComments();
    } catch (err: any) {
      throw new Error(err.message || "Failed to edit comment");
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    try {
      await api.comments.delete(commentId);
      await loadComments();
    } catch (err: any) {
      throw new Error(err.message || "Failed to delete comment");
    }
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) {
      return "N/A";
    }
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return "Invalid date";
      }
      return new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
    } catch (error) {
      return "Invalid date";
    }
  };

  const getFrameworkBadgeColor = (framework: string): string => {
    const colors: Record<string, string> = {
      porter: "bg-blue-100 text-blue-800",
      swot: "bg-green-100 text-green-800",
      pestel: "bg-purple-100 text-purple-800",
      blue_ocean: "bg-indigo-100 text-indigo-800",
    };
    return colors[framework.toLowerCase()] || "bg-gray-100 text-gray-800";
  };

  // Normalize framework name to match analysis keys
  const normalizeFrameworkName = (framework: string): string => {
    const normalized = framework.toLowerCase();
    // Handle variations like "porters_five_forces" -> "porter"
    if (normalized.includes('porter')) return 'porter';
    if (normalized.includes('swot')) return 'swot';
    if (normalized.includes('pestel')) return 'pestel';
    if (normalized.includes('blue') || normalized.includes('ocean')) return 'blue_ocean';
    return normalized;
  };

  const getConfidenceLevel = (score: number): {
    label: string;
    color: string;
  } => {
    if (score >= 0.8)
      return { label: "High", color: "text-green-600 bg-green-50" };
    if (score >= 0.6)
      return { label: "Medium", color: "text-yellow-600 bg-yellow-50" };
    return { label: "Low", color: "text-red-600 bg-red-50" };
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" label="Loading report..." />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <Alert
            variant="error"
            title="Error Loading Report"
            description={error || "Report not found"}
          />
          <div className="mt-4 flex justify-center">
            <Button
              variant="primary"
              leftIcon={<ArrowLeft className="w-4 h-4" />}
              onClick={() => router.push("/")}
            >
              Back to Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const confidence = getConfidenceLevel(report.confidence_score);
  const frameworksAvailable = Boolean(
    report.analysis &&
    (report.analysis.porter ||
      report.analysis.swot ||
      report.analysis.pestel ||
      report.analysis.blue_ocean)
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="min-h-screen bg-gray-50"
    >
      {isDeleting && <LoadingOverlay label="Deleting report..." />}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb Navigation */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <Breadcrumb items={breadcrumbItems} />
        </motion.div>
        
        {/* Back Button */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-6"
        >
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<ArrowLeft className="w-4 h-4" />}
            onClick={() => router.push("/")}
          >
            Back to Reports
          </Button>
        </motion.div>

        {/* Report Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
              <div className="flex-1 min-w-0">
                <h1 className="text-2xl font-bold text-gray-900 mb-1">
                  {report.company}
                </h1>

                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-4">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4" />
                    <span>{report.industry}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>{formatDate(report.created_at)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    <span className="capitalize">{report.depth || 'Standard'} Analysis</span>
                  </div>
                </div>

                {/* Frameworks */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {(report.frameworks || []).map((framework) => (
                    <Badge
                      key={framework}
                      className={getFrameworkBadgeColor(framework)}
                    >
                      {framework.toUpperCase()}
                    </Badge>
                  ))}
                </div>

                {/* Confidence Score */}
                <Tooltip
                  content={
                    <div className="space-y-2">
                      <p className="font-semibold">Confidence Score Explanation</p>
                      <p className="text-sm">
                        This score reflects the reliability and completeness of the analysis based on:
                      </p>
                      <ul className="text-sm list-disc list-inside space-y-1">
                        <li>Data availability and quality</li>
                        <li>Agent execution success rate</li>
                        <li>Framework analysis completeness</li>
                        <li>Source credibility and recency</li>
                      </ul>
                      <div className="mt-2 pt-2 border-t border-gray-700">
                        <p className="text-xs">
                          <strong>High (80%+)</strong>: Comprehensive analysis with reliable data sources
                        </p>
                        <p className="text-xs">
                          <strong>Medium (60-79%)</strong>: Good coverage with some limitations
                        </p>
                        <p className="text-xs">
                          <strong>Low (&lt;60%)</strong>: Limited data or incomplete analysis
                        </p>
                      </div>
                    </div>
                  }
                  placement="top"
                  maxWidth="320px"
                >
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50 cursor-help">
                    <span className="text-sm font-medium text-gray-700">
                      Confidence:
                    </span>
                    <span
                      className={`text-sm font-semibold px-2 py-0.5 rounded ${confidence.color}`}
                    >
                      {confidence.label} ({Math.round(report.confidence_score * 100)}%)
                    </span>
                    <Info className="w-4 h-4 text-gray-400" />
                  </div>
                </Tooltip>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<Share2 className="w-4 h-4" />}
                  onClick={() => setShowShareDialog(true)}
                >
                  Share
                </Button>
                {report.pdf_url && (
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<Download className="w-4 h-4" />}
                    onClick={handleDownloadPDF}
                  >
                    Download PDF
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<Trash2 className="w-4 h-4" />}
                  onClick={handleDeleteReport}
                  className="text-red-600 hover:bg-red-50 border-red-300"
                >
                  Delete
                </Button>
              </div>
            </div>

            {/* Status Alert */}
            {report.status === "partial_success" && (
              <Alert
                variant="warning"
                title="Partial Analysis"
                description="Some analysis components could not be completed. Results may be incomplete."
                className="mt-4"
              />
            )}
          </CardContent>
        </Card>
        </motion.div>

        {/* Tabbed Content */}
        <Tabs selectedIndex={activeTab} onChange={setActiveTab}>
          <TabList>
            <Tab>Overview</Tab>
            <Tab>Analysis</Tab>
            <Tab>Comments ({comments.length})</Tab>
            <Tab>Versions ({versions.length})</Tab>
          </TabList>

          <TabPanels>
            {/* Overview Tab */}
            <TabPanel>
              <div className="space-y-6">
                {/* Executive Summary */}
                {report.executive_summary && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Executive Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                        {report.executive_summary}
                      </p>
                    </CardContent>
                  </Card>
                )}

                {/* Key Metrics */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                >
                  <MetricCard
                    title="Frameworks Applied"
                    value={(report.frameworks || []).length}
                    icon={<FileText className="w-6 h-6" />}
                    trend="neutral"
                  />
                  <MetricCard
                    title="Analysis Depth"
                    value={report.depth ? report.depth.toUpperCase() : 'Standard'}
                    icon={<TrendingUp className="w-6 h-6" />}
                    trend="neutral"
                  />
                  <MetricCard
                    title="Confidence Score"
                    value={`${Math.round(report.confidence_score * 100)}%`}
                    icon={<CheckCircle className="w-6 h-6" />}
                    trend={
                      report.confidence_score >= 0.8
                        ? "up"
                        : report.confidence_score >= 0.6
                        ? "neutral"
                        : "down"
                    }
                  />
                </motion.div>

                {/* Key Findings */}
                {report.key_findings && report.key_findings.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Key Findings</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-3">
                        {report.key_findings.map((finding, idx) => (
                          <li key={idx} className="flex gap-3">
                            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{finding}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Recommendations */}
                {report.recommendations && report.recommendations.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Recommendations</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-3">
                        {report.recommendations.map((rec, idx) => (
                          <li key={idx} className="flex gap-3">
                            <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabPanel>

            {/* Analysis Tab */}
            <TabPanel>
              <div className="space-y-6">
                {!frameworksAvailable ? (
                  <Card>
                    <CardHeader>
                      <CardTitle>Framework details unavailable</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-gray-700">
                        We couldn’t find structured framework output for this report. Run a
                        new analysis with the latest agents to regenerate Porter's, SWOT,
                        PESTEL, or Blue Ocean insights.
                      </p>
                      <Button
                        variant="primary"
                        onClick={() => router.push('/analysis')}
                        leftIcon={<TrendingUp className="w-4 h-4" />}
                      >
                        Run New Analysis
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  <>
                    {/* Framework Filter/Selector */}
                    {report.frameworks && report.frameworks.length > 1 && (
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-sm font-medium text-gray-700 mr-2">
                              View Framework:
                            </span>
                            <Button
                              variant={activeFramework === 'all' ? 'primary' : 'outline'}
                              size="sm"
                              onClick={() => setActiveFramework('all')}
                            >
                              All Frameworks
                            </Button>
                            {report.frameworks.map((framework) => {
                              const frameworkKey = normalizeFrameworkName(framework);
                              const hasData = 
                                (frameworkKey === 'porter' && report.analysis?.porter) ||
                                (frameworkKey === 'swot' && report.analysis?.swot) ||
                                (frameworkKey === 'pestel' && report.analysis?.pestel) ||
                                (frameworkKey === 'blue_ocean' && report.analysis?.blue_ocean);
                              
                              if (!hasData) return null;
                              
                              // Display name for the button
                              const displayName = frameworkKey === 'porter' ? "PORTER'S 5 FORCES" :
                                                frameworkKey === 'swot' ? 'SWOT' :
                                                frameworkKey === 'pestel' ? 'PESTEL' :
                                                frameworkKey === 'blue_ocean' ? 'BLUE OCEAN' :
                                                framework.toUpperCase();
                              
                              return (
                                <Button
                                  key={framework}
                                  variant={activeFramework === frameworkKey ? 'primary' : 'outline'}
                                  size="sm"
                                  onClick={() => setActiveFramework(frameworkKey)}
                                >
                                  {displayName}
                                </Button>
                              );
                            })}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Porter's Five Forces */}
                    {report.analysis?.porter && (activeFramework === 'all' || activeFramework === 'porter') && (
                      <Card>
                        <CardHeader>
                          <CardTitle>Porter's Five Forces Analysis</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          {isPorterPlaceholder(report.analysis.porter) && (
                            <Alert variant="warning" className="mb-4" showIcon>
                              <strong>Analysis Incomplete:</strong> {getPlaceholderMessage("Porter's Five Forces")}
                            </Alert>
                          )}
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">
                              Competitive Rivalry
                            </h4>
                            <p className="text-gray-700">
                              {report.analysis?.porter?.competitive_rivalry}
                            </p>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">
                              Supplier Power
                            </h4>
                            <p className="text-gray-700">
                              {report.analysis?.porter?.supplier_power}
                            </p>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">
                              Buyer Power
                            </h4>
                            <p className="text-gray-700">
                              {report.analysis?.porter?.buyer_power}
                            </p>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">
                              Threat of Substitution
                            </h4>
                            <p className="text-gray-700">
                              {report.analysis?.porter?.threat_of_substitution}
                            </p>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">
                              Threat of New Entry
                            </h4>
                            <p className="text-gray-700">
                              {report.analysis?.porter?.threat_of_new_entry}
                            </p>
                          </div>
                          <div className="pt-4 border-t border-gray-200">
                            <h4 className="font-semibold text-gray-900 mb-2">
                              Overall Assessment
                            </h4>
                            <p className="text-gray-700">
                              {report.analysis?.porter?.overall_assessment}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                {/* SWOT Analysis */}
                {report.analysis?.swot && (activeFramework === 'all' || activeFramework === 'swot') && (
                  <Card>
                    <CardHeader>
                      <CardTitle>SWOT Analysis</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {isSWOTPlaceholder(report.analysis.swot) && (
                        <Alert variant="warning" className="mb-4" showIcon>
                          <strong>Analysis Incomplete:</strong> {getPlaceholderMessage('SWOT')}
                        </Alert>
                      )}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
                            <CheckCircle className="w-5 h-5" />
                            Strengths
                          </h4>
                          <ul className="space-y-2">
                            {report.analysis?.swot?.strengths?.map((item, idx) => (
                              <li key={idx} className="text-gray-700 pl-4 border-l-2 border-green-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold text-red-900 mb-3 flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5" />
                            Weaknesses
                          </h4>
                          <ul className="space-y-2">
                            {report.analysis?.swot?.weaknesses?.map((item, idx) => (
                              <li key={idx} className="text-gray-700 pl-4 border-l-2 border-red-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5" />
                            Opportunities
                          </h4>
                          <ul className="space-y-2">
                            {report.analysis?.swot?.opportunities?.map((item, idx) => (
                              <li key={idx} className="text-gray-700 pl-4 border-l-2 border-blue-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5" />
                            Threats
                          </h4>
                          <ul className="space-y-2">
                            {report.analysis?.swot?.threats?.map((item, idx) => (
                              <li key={idx} className="text-gray-700 pl-4 border-l-2 border-yellow-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* PESTEL Analysis */}
                {report.analysis?.pestel && (activeFramework === 'all' || activeFramework === 'pestel') && (
                  <Card>
                    <CardHeader>
                      <CardTitle>PESTEL Analysis</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {Object.entries(report.analysis?.pestel || {}).map(([key, value]) => (
                        <div key={key}>
                          <h4 className="font-semibold text-gray-900 mb-2 capitalize">
                            {key}
                          </h4>
                          <p className="text-gray-700">{value}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Blue Ocean Strategy */}
                {report.analysis?.blue_ocean && (activeFramework === 'all' || activeFramework === 'blue_ocean') && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Blue Ocean Strategy - ERRC Grid</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-semibold text-red-900 mb-3">
                            Eliminate
                          </h4>
                          <ul className="space-y-2">
                            {report.analysis?.blue_ocean?.eliminate?.map((item, idx) => (
                              <li key={idx} className="text-gray-700 pl-4 border-l-2 border-red-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold text-orange-900 mb-3">
                            Reduce
                          </h4>
                          <ul className="space-y-2">
                            {report.analysis?.blue_ocean?.reduce?.map((item, idx) => (
                              <li key={idx} className="text-gray-700 pl-4 border-l-2 border-orange-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold text-blue-900 mb-3">
                            Raise
                          </h4>
                          <ul className="space-y-2">
                            {report.analysis?.blue_ocean?.raise?.map((item, idx) => (
                              <li key={idx} className="text-gray-700 pl-4 border-l-2 border-blue-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold text-green-900 mb-3">
                            Create
                          </h4>
                          <ul className="space-y-2">
                            {report.analysis?.blue_ocean?.create?.map((item, idx) => (
                              <li key={idx} className="text-gray-700 pl-4 border-l-2 border-green-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
                  </>
                )}
              </div>
            </TabPanel>

            {/* Comments Tab */}
            <TabPanel>
              <div className="space-y-6">
                <Card>
                  <CardContent className="p-6">
                    <CommentForm
                      reportId={id}
                      onSubmit={handleAddComment}
                      placeholder="Share your thoughts on this analysis..."
                    />
                  </CardContent>
                </Card>

                <CommentThread
                  reportId={id}
                  comments={comments}
                  onReply={handleReplyComment}
                  onEdit={handleEditComment}
                  onDelete={handleDeleteComment}
                />
              </div>
            </TabPanel>

            {/* Versions Tab */}
            <TabPanel>
              <VersionHistory
                reportId={id}
                currentVersion={versions.find((v) => v.is_current)?.version_number}
                onRestore={async () => {
                  await loadReport();
                  await loadVersions();
                }}
              />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>

      {/* Share Dialog */}
      <ShareDialog
        reportId={id}
        isOpen={showShareDialog}
        onClose={() => setShowShareDialog(false)}
        onSuccess={handleShareSuccess}
      />
    </motion.div>
  );
}
