"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  DataTable,
  DataTableSkeleton,
  TablePagination,
  useSort,
  TableActions,
  exportData,
  Card,
  Button,
  Badge,
  Input,
  Alert,
  Modal,
  useModal,
  MetricCard,
  ProgressBar,
} from "@/app/components";
import { api, APIError } from "@/lib/api";
import {
  Trash2,
  Download,
  Eye,
  Share2,
  Plus,
  FileText,
  Search,
  BarChart2,
  CheckCircle2,
  Timer,
  Shield,
  Filter as FilterIcon,
  AlertTriangle,
} from "lucide-react";
import type { Column } from "@/app/components";

interface Report {
  id: string;
  report_id?: string; // Backend returns report_id, we map it to id
  company: string;
  industry: string;
  frameworks: string[];
  created_at: string;
  status: "completed" | "processing" | "failed" | "partial_success";
  confidence_score?: number;
  user_id?: string;
}

interface ReportsListResponse {
  reports: Report[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

const FRAMEWORK_COLORS: Record<string, string> = {
  porter: "blue",
  swot: "green",
  pestel: "purple",
  blue_ocean: "indigo",
  ansoff: "pink",
  bcg: "yellow",
  vrio: "orange",
};

const STATUS_COLORS: Record<string, "success" | "warning" | "danger"> = {
  completed: "success",
  processing: "warning",
  failed: "danger",
};

const STATUS_FILTERS: Array<"all" | "completed" | "processing" | "failed"> = [
  "all",
  "completed",
  "processing",
  "failed",
];

const ONE_DAY = 1000 * 60 * 60 * 24;
const ONE_WEEK = ONE_DAY * 7;

const numberFormatter = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
});

const percentageFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0,
});

const relativeTimeFormatter = new Intl.RelativeTimeFormat("en", {
  numeric: "auto",
});

const formatRelativeTime = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  let delta = (date.getTime() - Date.now()) / 1000;
  const divisions: Array<{ amount: number; unit: Intl.RelativeTimeFormatUnit }> = [
    { amount: 60, unit: "second" },
    { amount: 60, unit: "minute" },
    { amount: 24, unit: "hour" },
    { amount: 7, unit: "day" },
    { amount: 4.34524, unit: "week" },
    { amount: 12, unit: "month" },
    { amount: Number.POSITIVE_INFINITY, unit: "year" },
  ];

  for (const division of divisions) {
    if (Math.abs(delta) < division.amount) {
      return relativeTimeFormatter.format(
        Math.round(delta),
        division.unit
      );
    }
    delta /= division.amount;
  }
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
};

const formatFrameworkLabel = (value: string) =>
  value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

export default function ReportsPage() {
  const router = useRouter();

  // State
  const [reports, setReports] = useState<Report[]>([]);
  const [totalReports, setTotalReports] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedRows, setSelectedRows] = useState<Set<string | number>>(
    new Set()
  );
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<
    "all" | "completed" | "processing" | "failed"
  >("all");
  const [frameworkFilter, setFrameworkFilter] = useState<string | null>(null);

  // Navigation helpers
  const goToPage = (page: number) => {
    if (page >= 0 && page < totalPages) {
      setCurrentPage(page);
    }
  };

  const { sortConfig, handleSort } = useSort({
    defaultSort: { key: "created_at", direction: "desc" },
  });

  const {
    isOpen: isDeleteModalOpen,
    open: openDeleteModal,
    close: closeDeleteModal,
  } = useModal();

  const {
    isOpen: isBulkDeleteOpen,
    open: openBulkDelete,
    close: closeBulkDelete,
  } = useModal();

  const availableFrameworkFilters = useMemo(() => {
    const set = new Set<string>();
    reports.forEach((report) => {
      report.frameworks.forEach((framework) => set.add(framework));
    });
    return Array.from(set).sort();
  }, [reports]);

  useEffect(() => {
    if (
      frameworkFilter &&
      !availableFrameworkFilters.includes(frameworkFilter)
    ) {
      setFrameworkFilter(null);
    }
  }, [frameworkFilter, availableFrameworkFilters]);

  const displayedReports = useMemo(() => {
    return reports.filter((report) => {
      const matchesStatus =
        statusFilter === "all" || report.status === statusFilter;
      const matchesFramework =
        !frameworkFilter || report.frameworks.includes(frameworkFilter);
      return matchesStatus && matchesFramework;
    });
  }, [reports, statusFilter, frameworkFilter]);

  const hasAppliedFilters =
    statusFilter !== "all" || Boolean(frameworkFilter);

  const insights = useMemo(() => {
    if (reports.length === 0) {
      return {
        statusCounts: {
          completed: 0,
          processing: 0,
          failed: 0,
        } as Record<Report["status"], number>,
        frameworkBreakdown: [] as Array<[string, number]>,
        recentReports: [] as Report[],
        attentionReports: [] as Report[],
        completionRate: 0,
        avgConfidence: null as number | null,
        last7Days: 0,
        prev7Days: 0,
        latestReport: null as Report | null,
      };
    }

    const statusCounts = reports.reduce(
      (acc, report) => {
        acc[report.status] = (acc[report.status] || 0) + 1;
        return acc;
      },
      {
        completed: 0,
        processing: 0,
        failed: 0,
      } as Record<Report["status"], number>
    );

    const frameworkMap = new Map<string, number>();
    reports.forEach((report) => {
      report.frameworks.forEach((framework) => {
        frameworkMap.set(
          framework,
          (frameworkMap.get(framework) || 0) + 1
        );
      });
    });

    const frameworkBreakdown = Array.from(frameworkMap.entries()).sort(
      (a, b) => b[1] - a[1]
    );

    const scores = reports
      .map((report) => report.confidence_score)
      .filter((score): score is number => typeof score === "number");

    const avgConfidence = scores.length
      ? Math.round(
          (scores.reduce((sum, score) => sum + score, 0) / scores.length) *
            100
        )
      : null;

    const now = Date.now();
    const lastWeekStart = now - ONE_WEEK;
    const previousWeekStart = now - ONE_WEEK * 2;

    const last7Days = reports.filter(
      (report) => new Date(report.created_at).getTime() >= lastWeekStart
    ).length;

    const prev7Days = reports.filter((report) => {
      const createdAt = new Date(report.created_at).getTime();
      return createdAt >= previousWeekStart && createdAt < lastWeekStart;
    }).length;

    const recentReports = [...reports].sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );

    const attentionReports = recentReports
      .filter(
        (report) => report.status === 'failed' || report.status === 'processing'
      )
      .slice(0, 4);

    const completionDenominator =
      statusCounts.completed + statusCounts.failed || 0;
    const completionRate = completionDenominator
      ? Math.round((statusCounts.completed / completionDenominator) * 100)
      : 0;

      return {
        statusCounts,
        frameworkBreakdown,
        recentReports: recentReports.slice(0, 5),
        attentionReports,
        completionRate,
        avgConfidence,
        last7Days,
        prev7Days,
        latestReport: recentReports[0] || null,
      };
  }, [reports]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch reports
  const fetchReports = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = (await api.analysis.listReports({
        page: currentPage,
        limit: pageSize,
        sort_by: sortConfig.key,
        order: sortConfig.direction,
        search: debouncedSearch || undefined,
      })) as ReportsListResponse;

      // Response is already validated and transformed by Zod in api.ts
      // The ReportSchema automatically maps report_id to id
      const allReports = response.reports || [];

      // If backend supports search, use server-side filtering
      // Otherwise fall back to client-side filtering
      let filteredReports = allReports;
      if (debouncedSearch && !response.total) {
        // Backend doesn't support search, filter client-side
        const search = debouncedSearch.toLowerCase();
        filteredReports = allReports.filter(
          (report) =>
            report.company.toLowerCase().includes(search) ||
            report.industry.toLowerCase().includes(search)
        );
      }

      setReports(filteredReports);

      // Use server-provided total if available, otherwise use filtered count
      // Ensure total is a number, defaulting to 0 if missing
      const total =
        typeof response.total === "number"
          ? response.total
          : debouncedSearch && !response.total
          ? filteredReports.length
          : typeof response.count === "number"
          ? response.count
          : allReports.length;
      const safeTotal = Math.max(0, total || 0);
      setTotalReports(safeTotal);

      // Calculate total pages safely, ensuring it's never NaN
      // Guard against pageSize being 0 or undefined
      const safePageSize = Math.max(1, pageSize || 25);
      const calculatedTotalPages =
        safePageSize > 0 ? Math.ceil(safeTotal / safePageSize) : 0;
      const safeTotalPages =
        isNaN(calculatedTotalPages) || calculatedTotalPages < 1
          ? 1
          : Math.max(1, calculatedTotalPages);
      setTotalPages(safeTotalPages);

      // Clear error if data loaded successfully
      setError(null);
    } catch (err) {
      const errorMessage =
        err instanceof APIError ? err.message : "Failed to load reports";
      setError(errorMessage);
      console.error("Failed to fetch reports:", err);
      // Set empty state on error
      setReports([]);
      setTotalReports(0);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, sortConfig, debouncedSearch]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  // Reset to page 0 when search changes
  useEffect(() => {
    if (debouncedSearch) {
      setCurrentPage(0);
    }
  }, [debouncedSearch]);

  // Delete single report
  const handleDelete = async (reportId: string) => {
    setDeletingId(reportId);
    try {
      await api.analysis.deleteReport(reportId);
      await fetchReports();
      closeDeleteModal();
      setSelectedRows((prev) => {
        const next = new Set(prev);
        next.delete(reportId);
        return next;
      });
    } catch (err) {
      const errorMessage =
        err instanceof APIError ? err.message : "Failed to delete report";
      setError(errorMessage);
    } finally {
      setDeletingId(null);
    }
  };

  // Bulk delete
  const handleBulkDelete = async () => {
    const ids = Array.from(selectedRows) as string[];
    setLoading(true);

    try {
      await Promise.all(ids.map((id) => api.analysis.deleteReport(id)));
      await fetchReports();
      setSelectedRows(new Set());
      closeBulkDelete();
    } catch (err) {
      const errorMessage =
        err instanceof APIError ? err.message : "Failed to delete reports";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Export data
  const handleExport = (format: "csv" | "json") => {
    const exportReports = displayedReports.map((r) => ({
      Company: r.company,
      Industry: r.industry,
      Frameworks: r.frameworks.join(", "),
      Status: r.status,
      "Created At": new Date(r.created_at).toLocaleDateString(),
      "Confidence Score": r.confidence_score || "N/A",
    }));

    exportData(exportReports, `reports-${Date.now()}`, format);
  };

  // Table columns
  const columns: Column<Report>[] = useMemo(
    () => [
      {
        key: "company",
        label: "Company",
        sortable: true,
        accessor: (row) => row.company,
        render: (value, row) => (
          <div className="flex flex-col">
            <span className="font-medium text-gray-900">{value}</span>
            <span className="text-sm text-gray-500 md:hidden">
              {row.industry}
            </span>
          </div>
        ),
      },
      {
        key: "industry",
        label: "Industry",
        sortable: true,
        hideOnMobile: true,
        accessor: (row) => row.industry,
        render: (value) => <span className="text-gray-600">{value}</span>,
      },
      {
        key: "frameworks",
        label: "Frameworks",
        accessor: (row) => row.frameworks,
        render: (frameworks: string[]) => (
          <div className="flex flex-wrap gap-1">
            {frameworks.slice(0, 3).map((fw) => (
              <Badge
                key={fw}
                variant={FRAMEWORK_COLORS[fw] || "gray"}
                size="sm"
              >
                {fw.toUpperCase()}
              </Badge>
            ))}
            {frameworks.length > 3 && (
              <Badge variant="gray" size="sm">
                +{frameworks.length - 3}
              </Badge>
            )}
          </div>
        ),
      },
      {
        key: "created_at",
        label: "Created",
        sortable: true,
        hideOnMobile: true,
        accessor: (row) => row.created_at,
        render: (value) => (
          <span className="text-gray-600">
            {new Date(value).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            })}
          </span>
        ),
      },
      {
        key: "status",
        label: "Status",
        sortable: true,
        accessor: (row) => row.status,
        render: (value: string) => (
          <Badge variant={STATUS_COLORS[value] || "default"} size="sm">
            {value.charAt(0).toUpperCase() + value.slice(1)}
          </Badge>
        ),
      },
      {
        key: "actions",
        label: "Actions",
        align: "right",
        render: (_, row) => (
          <TableActions
            row={row}
            index={0}
            actions={[
              {
                key: "view",
                label: "View Report",
                icon: <Eye className="w-4 h-4" />,
                onClick: (report) => router.push(`/reports/${report.id}`),
              },
              {
                key: "share",
                label: "Share",
                icon: <Share2 className="w-4 h-4" />,
                onClick: (report) => {
                  // TODO: Implement share functionality
                  console.log("Share report:", report.id);
                },
              },
              {
                key: "download",
                label: "Download PDF",
                icon: <Download className="w-4 h-4" />,
                onClick: async (report) => {
                  window.open(
                    `${process.env.NEXT_PUBLIC_API_URL}/reports/${report.id}/download`,
                    "_blank"
                  );
                },
              },
              {
                key: "delete",
                label: "Delete",
                icon: <Trash2 className="w-4 h-4" />,
                onClick: (report) => {
                  setDeletingId(report.id);
                  openDeleteModal();
                },
                dangerous: true,
              },
            ]}
          />
        ),
      },
    ],
    [router, openDeleteModal]
  );

  // Empty state
  const emptyState = (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center py-12"
    >
      <motion.div
        animate={{ rotate: [0, 10, -10, 0] }}
        transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
      >
        <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
      </motion.div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {searchTerm || hasAppliedFilters
          ? "No reports match your filters"
          : "No reports yet"}
      </h3>
      <p className="text-gray-500 mb-6">
        {searchTerm || hasAppliedFilters
          ? "Try adjusting your search or clearing the filters"
          : "Create your first business analysis to get started"}
      </p>
      {!searchTerm && (
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Button
            onClick={() => router.push("/analysis")}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Create Analysis
          </Button>
        </motion.div>
      )}
    </motion.div>
  );

  const statusCounts = insights.statusCounts;
  const appliedFiltersCount =
    (statusFilter !== "all" ? 1 : 0) + (frameworkFilter ? 1 : 0);
  const clearLocalFilters = () => {
    setStatusFilter("all");
    setFrameworkFilter(null);
  };
  const completionTrendDirection = insights.prev7Days === 0
    ? insights.last7Days > 0
      ? "up"
      : "neutral"
    : insights.last7Days >= insights.prev7Days
    ? "up"
    : "down";
  const completionTrendValue = insights.prev7Days === 0
    ? insights.last7Days > 0
      ? `+${insights.last7Days}`
      : undefined
    : `${Math.abs(
        Math.round(
          ((insights.last7Days - insights.prev7Days) /
            Math.max(1, insights.prev7Days)) *
            100
        )
      )}%`;

  const completionRateDisplay = `${percentageFormatter.format(
    insights.completionRate
  )}%`;
  const avgConfidenceDisplay =
    insights.avgConfidence !== null
      ? `${percentageFormatter.format(insights.avgConfidence)}%`
      : "—";
  const processingSubtitle = statusCounts.processing
    ? `${statusCounts.processing} running now`
    : "No analyses running";
  const latestReport = insights.latestReport;
  const statusDenominator = Math.max(
    statusCounts.completed + statusCounts.processing + statusCounts.failed,
    1
  );
  const frameworksToShow = insights?.frameworkBreakdown?.slice(0, 5) || [];
  const frameworkMax = frameworksToShow[0]?.[1] || 1;
  const confidenceSampleCount = reports.filter(
    (report) => typeof report.confidence_score === "number"
  ).length;
  const attentionReports = insights?.attentionReports || [];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="min-h-screen bg-gray-50 py-8"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Reports</h1>
          <p className="text-base text-gray-600">
            View and manage your business analysis reports
          </p>
        </motion.div>

        {/* KPI Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="mb-8"
        >
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              title="Total Reports"
              value={numberFormatter.format(totalReports)}
              icon={<BarChart2 className="w-5 h-5" />}
              color="blue"
              trend={completionTrendDirection}
              trendValue={completionTrendValue}
              subtitle={`${insights.last7Days} in the last 7 days`}
            />
            <MetricCard
              title="Completion Rate"
              value={completionRateDisplay}
              icon={<CheckCircle2 className="w-5 h-5" />}
              color="green"
              subtitle={`${statusCounts.completed} completed / ${
                statusCounts.completed + statusCounts.failed
              } closed`}
            />
            <MetricCard
              title="In Progress"
              value={statusCounts.processing}
              icon={<Timer className="w-5 h-5" />}
              color="orange"
              subtitle={processingSubtitle}
            />
            <MetricCard
              title="Avg Confidence"
              value={avgConfidenceDisplay}
              icon={<Shield className="w-5 h-5" />}
              color="purple"
              subtitle={
                insights.avgConfidence !== null
                  ? `Across ${confidenceSampleCount} scored reports`
                  : "Confidence appears after reports finish"
              }
            />
          </div>
        </motion.div>

        {/* Error Alert with Retry */}
        {error && (
          <Alert
            variant="error"
            title="Failed to Load Reports"
            description={
              <div>
                <p className="mb-2">{error}</p>
                {error.includes("Unable to connect") ||
                error.includes("Network error") ? (
                  <p className="text-sm text-red-700 mt-2">
                    Please ensure the backend server is running at{" "}
                    {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"}
                  </p>
                ) : null}
              </div>
            }
            actions={
              <div className="flex gap-2 mt-3">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={fetchReports}
                  className="bg-white text-red-700 hover:bg-red-50"
                >
                  Retry
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => router.push("/analysis")}
                  className="border-red-300 text-red-700 hover:bg-red-50"
                >
                  Create New Report
                </Button>
              </div>
            }
            dismissible
            onClose={() => setError(null)}
            className="mb-6"
          />
        )}

        {/* Toolbar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="mb-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              {/* Search */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="flex-1 max-w-md"
              >
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search by company or industry..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </motion.div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                {selectedRows.size > 0 && (
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={openBulkDelete}
                    leftIcon={<Trash2 className="w-4 h-4" />}
                  >
                    Delete ({selectedRows.size})
                  </Button>
                )}

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport("csv")}
                  leftIcon={<Download className="w-4 h-4" />}
                >
                  Export CSV
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport("json")}
                  leftIcon={<Download className="w-4 h-4" />}
                >
                  Export JSON
                </Button>

                <Button
                  onClick={() => router.push("/analysis")}
                  leftIcon={<Plus className="w-4 h-4" />}
                >
                  New Analysis
                </Button>
              </div>
            </div>

            {/* Inline Filters */}
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <FilterIcon className="w-4 h-4" />
                  <span>Quick Filters</span>
                  {appliedFiltersCount > 0 && (
                    <Badge variant="info" size="sm">
                      {appliedFiltersCount} active
                    </Badge>
                  )}
                </div>
                {hasAppliedFilters && (
                  <button
                    type="button"
                    onClick={clearLocalFilters}
                    className="text-xs font-medium text-gray-500 hover:text-gray-900"
                  >
                    Reset
                  </button>
                )}
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
                    Status
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {STATUS_FILTERS.map((status) => {
                      const isActive = statusFilter === status;
                      const label =
                        status === "all"
                          ? "All statuses"
                          : `${status.charAt(0).toUpperCase()}${status.slice(1)}`;
                      return (
                        <button
                          key={status}
                          type="button"
                          onClick={() => setStatusFilter(status)}
                          className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                            isActive
                              ? "bg-gray-900 text-white border-gray-900 shadow-sm"
                              : "text-gray-600 border-gray-200 hover:border-gray-400 hover:text-gray-900"
                          }`}
                        >
                          {label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {availableFrameworkFilters.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
                      Framework
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {availableFrameworkFilters.map((framework) => {
                        const isActive = frameworkFilter === framework;
                        return (
                          <button
                            key={framework}
                            type="button"
                            onClick={() =>
                              setFrameworkFilter(
                                isActive ? null : framework
                              )
                            }
                            className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                              isActive
                                ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                                : "text-gray-600 border-gray-200 hover:border-blue-300 hover:text-gray-900"
                            }`}
                          >
                            {formatFrameworkLabel(framework)}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Data + Insights */}
        <div className="grid gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <Card>
              {loading ? (
                <DataTableSkeleton columns={6} rows={pageSize} />
              ) : displayedReports.length === 0 ? (
                emptyState
              ) : (
                <>
                  <DataTable
                    columns={columns}
                    data={displayedReports}
                    rowKey={(row, index) => {
                      const key = row.id || row.report_id;
                      if (!key) {
                        console.warn('Report missing both id and report_id:', row);
                        return `missing-report-${index}-${Date.now()}`;
                      }
                      // Ensure unique key by combining ID with index and timestamp if needed
                      return `${key}-${index}-${row.created_at || row.timestamp || ''}`;
                    }}
                    selectionMode="multi"
                    selectedRows={selectedRows}
                    onSelectionChange={setSelectedRows}
                    onRowClick={(row) => {
                      if (row?.id) {
                        router.push(`/reports/${row.id}`);
                      }
                    }}
                    hoverable
                    striped
                    stickyHeader
                    maxHeight="calc(100vh - 400px)"
                  />

                  {/* Pagination */}
                  <div className="border-t border-gray-200 px-6 py-4">
                    <TablePagination
                      currentPage={currentPage}
                      totalPages={totalPages}
                      pageSize={pageSize}
                      totalItems={totalReports}
                      onPageChange={goToPage}
                      onPageSizeChange={(size) => {
                        setPageSize(size);
                        goToPage(0);
                      }}
                      pageSizeOptions={[10, 25, 50, 100]}
                    />
                  </div>
                </>
              )}
            </Card>
          </div>

          <div className="xl:col-span-1">
            <Card className="h-full">
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase">
                        Pipeline status
                      </p>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Health Monitor
                      </h3>
                    </div>
                    <Badge variant="info" size="sm">
                      {displayedReports.length} shown
                    </Badge>
                  </div>
                  <div className="space-y-3">
                    {(["completed", "processing", "failed"] as Report["status"][]).map(
                      (status) => (
                        <div key={status} className="space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">
                              {status.charAt(0).toUpperCase() + status.slice(1)}
                            </span>
                            <span className="font-semibold text-gray-900">
                              {statusCounts[status] || 0}
                            </span>
                          </div>
                          <ProgressBar
                            progress={Math.round(
                              ((statusCounts[status] || 0) / statusDenominator) *
                                100
                            )}
                            showPercentage={false}
                            color={
                              status === "completed"
                                ? "green"
                                : status === "processing"
                                ? "yellow"
                                : "red"
                            }
                          />
                        </div>
                      )
                    )}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
                    Framework coverage
                  </p>
                  {frameworksToShow.length === 0 ? (
                    <p className="text-sm text-gray-500">
                      Coverage metrics will appear after you run a few reports.
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {frameworksToShow.map(([framework, count]) => (
                        <div key={framework}>
                          <div className="flex items-center justify-between text-sm mb-1">
                            <span className="text-gray-700">
                              {formatFrameworkLabel(framework)}
                            </span>
                            <span className="font-medium text-gray-900">
                              {count}
                            </span>
                          </div>
                          <div className="h-2 w-full bg-gray-100 rounded-full">
                            <div
                              className="h-2 rounded-full bg-gray-900"
                              style={{
                                width: `${Math.max(
                                  8,
                                  Math.round((count / frameworkMax) * 100)
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-xs font-semibold text-gray-500 uppercase flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-500" />
                      Needs attention
                    </p>
                    <Badge
                      variant={attentionReports.length ? 'danger' : 'success'}
                      size="sm"
                    >
                      {attentionReports.length ? `${attentionReports.length} open` : 'All clear'}
                    </Badge>
                  </div>
                  {attentionReports.length === 0 ? (
                    <p className="text-sm text-gray-500">
                      All recent analyses are healthy. We’ll surface failed or stuck runs here.
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {attentionReports.map((report) => (
                        <div
                          key={report.id || report.report_id}
                          className="flex items-start justify-between rounded-lg border border-red-100 bg-red-50/40 px-3 py-2"
                        >
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                              {report.company}
                            </p>
                            <p className="text-xs text-gray-500 truncate">
                              {(report.industry && report.industry.trim()) || 'Unknown industry'} · {formatRelativeTime(report.created_at)}
                            </p>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {report.frameworks.slice(0, 2).map((framework) => (
                                <Badge key={framework} variant="warning" size="sm">
                                  {framework.toUpperCase()}
                                </Badge>
                              ))}
                              {report.frameworks.length > 2 && (
                                <Badge variant="default" size="sm">
                                  +{report.frameworks.length - 2}
                                </Badge>
                              )}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-2 ml-3">
                            <Badge variant={STATUS_COLORS[report.status] || 'warning'} size="sm">
                              {report.status}
                            </Badge>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => report.id && router.push(`/reports/${report.id}`)}
                            >
                              Review
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {latestReport && (
                    <p className="text-xs text-gray-400 mt-3">
                      Last completion {formatRelativeTime(latestReport.created_at)}
                    </p>
                  )}
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Delete Confirmation Modal */}
        <Modal
          isOpen={isDeleteModalOpen}
          onClose={closeDeleteModal}
          title="Delete Report"
          footer={
            <>
              <Button
                variant="outline"
                onClick={closeDeleteModal}
                disabled={deletingId !== null}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => deletingId && handleDelete(deletingId)}
                disabled={deletingId === null}
                isLoading={deletingId !== null}
              >
                Delete
              </Button>
            </>
          }
        >
          <p className="text-gray-600">
            Are you sure you want to delete this report? This action cannot be
            undone.
          </p>
        </Modal>

        {/* Bulk Delete Confirmation Modal */}
        <Modal
          isOpen={isBulkDeleteOpen}
          onClose={closeBulkDelete}
          title="Delete Multiple Reports"
          footer={
            <>
              <Button
                variant="outline"
                onClick={closeBulkDelete}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleBulkDelete}
                isLoading={loading}
              >
                Delete {selectedRows.size} Reports
              </Button>
            </>
          }
        >
          <p className="text-gray-600">
            Are you sure you want to delete {selectedRows.size} selected
            report(s)? This action cannot be undone.
          </p>
        </Modal>
      </div>
    </motion.div>
  );
}
