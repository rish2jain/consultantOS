'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  DataTable,
  DataTableSkeleton,
  TablePagination,
  TableSort,
  useSort,
  TableFilters,
  useFilters,
  TableActions,
  commonActions,
  exportData,
  Card,
  Button,
  Badge,
  Input,
  Alert,
  ErrorAlert,
  Spinner,
  Modal,
  useModal
} from '@/app/components';
import { api, APIError } from '@/lib/api';
import { Trash2, Download, Eye, Share2, Plus, FileText, Search } from 'lucide-react';
import type { Column } from '@/app/components';

interface Report {
  id: string;
  company: string;
  industry: string;
  frameworks: string[];
  created_at: string;
  status: 'completed' | 'processing' | 'failed';
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
  porter: 'blue',
  swot: 'green',
  pestel: 'purple',
  blue_ocean: 'indigo',
  ansoff: 'pink',
  bcg: 'yellow',
  vrio: 'orange',
};

const STATUS_COLORS: Record<string, 'success' | 'warning' | 'error'> = {
  completed: 'success',
  processing: 'warning',
  failed: 'error',
};

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
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedRows, setSelectedRows] = useState<Set<string | number>>(new Set());
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Navigation helpers
  const goToPage = (page: number) => {
    if (page >= 0 && page < totalPages) {
      setCurrentPage(page);
    }
  };

  const { sortConfig, handleSort } = useSort({
    defaultSort: { key: 'created_at', direction: 'desc' },
  });

  const {
    isOpen: isDeleteModalOpen,
    open: openDeleteModal,
    close: closeDeleteModal
  } = useModal();

  const {
    isOpen: isBulkDeleteOpen,
    open: openBulkDelete,
    close: closeBulkDelete
  } = useModal();

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
      const response = await api.analysis.listReports({
        page: currentPage,
        limit: pageSize,
        sort_by: sortConfig.key,
        order: sortConfig.direction,
        search: debouncedSearch || undefined,
      }) as ReportsListResponse;

      const allReports = response.reports || [];
      
      // If backend supports search, use server-side filtering
      // Otherwise fall back to client-side filtering
      let filteredReports = allReports;
      if (debouncedSearch && !response.total) {
        // Backend doesn't support search, filter client-side
        const search = debouncedSearch.toLowerCase();
        filteredReports = allReports.filter(report =>
          report.company.toLowerCase().includes(search) ||
          report.industry.toLowerCase().includes(search)
        );
      }

      setReports(filteredReports);
      
      // Use server-provided total if available, otherwise use filtered count
      // Ensure total is a number, defaulting to 0 if missing
      const total = typeof response.total === 'number' 
        ? response.total 
        : (debouncedSearch && !response.total 
            ? filteredReports.length 
            : (typeof response.count === 'number' ? response.count : allReports.length));
      const safeTotal = Math.max(0, total || 0);
      setTotalReports(safeTotal);
      
      // Calculate total pages safely, ensuring it's never NaN
      // Guard against pageSize being 0 or undefined
      const safePageSize = Math.max(1, pageSize || 25);
      const calculatedTotalPages = safePageSize > 0 
        ? Math.ceil(safeTotal / safePageSize)
        : 0;
      const safeTotalPages = isNaN(calculatedTotalPages) || calculatedTotalPages < 1 ? 1 : Math.max(1, calculatedTotalPages);
      setTotalPages(safeTotalPages);
      
      // Clear error if data loaded successfully
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof APIError
        ? err.message
        : 'Failed to load reports';
      setError(errorMessage);
      console.error('Failed to fetch reports:', err);
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
      setSelectedRows(prev => {
        const next = new Set(prev);
        next.delete(reportId);
        return next;
      });
    } catch (err) {
      const errorMessage = err instanceof APIError
        ? err.message
        : 'Failed to delete report';
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
      await Promise.all(ids.map(id => api.analysis.deleteReport(id)));
      await fetchReports();
      setSelectedRows(new Set());
      closeBulkDelete();
    } catch (err) {
      const errorMessage = err instanceof APIError
        ? err.message
        : 'Failed to delete reports';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Export data
  const handleExport = (format: 'csv' | 'json') => {
    const exportReports = reports.map(r => ({
      Company: r.company,
      Industry: r.industry,
      Frameworks: r.frameworks.join(', '),
      Status: r.status,
      'Created At': new Date(r.created_at).toLocaleDateString(),
      'Confidence Score': r.confidence_score || 'N/A',
    }));

    exportData(exportReports, `reports-${Date.now()}`, format);
  };

  // Table columns
  const columns: Column<Report>[] = useMemo(() => [
    {
      key: 'company',
      label: 'Company',
      sortable: true,
      accessor: (row) => row.company,
      render: (value, row) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900">{value}</span>
          <span className="text-sm text-gray-500 md:hidden">{row.industry}</span>
        </div>
      ),
    },
    {
      key: 'industry',
      label: 'Industry',
      sortable: true,
      hideOnMobile: true,
      accessor: (row) => row.industry,
      render: (value) => (
        <span className="text-gray-600">{value}</span>
      ),
    },
    {
      key: 'frameworks',
      label: 'Frameworks',
      accessor: (row) => row.frameworks,
      render: (frameworks: string[]) => (
        <div className="flex flex-wrap gap-1">
          {frameworks.slice(0, 3).map((fw) => (
            <Badge
              key={fw}
              variant={FRAMEWORK_COLORS[fw] || 'gray'}
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
      key: 'created_at',
      label: 'Created',
      sortable: true,
      hideOnMobile: true,
      accessor: (row) => row.created_at,
      render: (value) => (
        <span className="text-gray-600">
          {new Date(value).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      accessor: (row) => row.status,
      render: (value: string) => (
        <Badge variant={STATUS_COLORS[value] || 'gray'} size="sm">
          {value.charAt(0).toUpperCase() + value.slice(1)}
        </Badge>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      align: 'right',
      render: (_, row) => (
        <TableActions
          row={row}
          index={0}
          actions={[
            {
              key: 'view',
              label: 'View Report',
              icon: <Eye className="w-4 h-4" />,
              onClick: (report) => router.push(`/reports/${report.id}`),
            },
            {
              key: 'share',
              label: 'Share',
              icon: <Share2 className="w-4 h-4" />,
              onClick: (report) => {
                // TODO: Implement share functionality
                console.log('Share report:', report.id);
              },
            },
            {
              key: 'download',
              label: 'Download PDF',
              icon: <Download className="w-4 h-4" />,
              onClick: async (report) => {
                window.open(`${process.env.NEXT_PUBLIC_API_URL}/reports/${report.id}/download`, '_blank');
              },
            },
            {
              key: 'delete',
              label: 'Delete',
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
  ], [router, openDeleteModal]);

  // Empty state
  const emptyState = (
    <div className="text-center py-12">
      <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {searchTerm ? 'No reports found' : 'No reports yet'}
      </h3>
      <p className="text-gray-500 mb-6">
        {searchTerm
          ? 'Try adjusting your search criteria'
          : 'Create your first business analysis to get started'
        }
      </p>
      {!searchTerm && (
        <Button
          onClick={() => router.push('/analysis')}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Create Analysis
        </Button>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Reports
          </h1>
          <p className="text-gray-600">
            View and manage your business analysis reports
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <ErrorAlert className="mb-6">
            {error}
          </ErrorAlert>
        )}

        {/* Toolbar */}
        <Card className="mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            {/* Search */}
            <div className="flex-1 max-w-md">
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
            </div>

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
                onClick={() => handleExport('csv')}
                leftIcon={<Download className="w-4 h-4" />}
              >
                Export CSV
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport('json')}
                leftIcon={<Download className="w-4 h-4" />}
              >
                Export JSON
              </Button>

              <Button
                onClick={() => router.push('/analysis')}
                leftIcon={<Plus className="w-4 h-4" />}
              >
                New Analysis
              </Button>
            </div>
          </div>
        </Card>

        {/* Data Table */}
        <Card>
          {loading ? (
            <DataTableSkeleton columns={6} rows={pageSize} />
          ) : reports.length === 0 ? (
            emptyState
          ) : (
            <>
              <DataTable
                columns={columns}
                data={reports}
                rowKey={(row) => row.id}
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
                loading={deletingId !== null}
              >
                Delete
              </Button>
            </>
          }
        >
          <p className="text-gray-600">
            Are you sure you want to delete this report? This action cannot be undone.
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
                loading={loading}
              >
                Delete {selectedRows.size} Reports
              </Button>
            </>
          }
        >
          <p className="text-gray-600">
            Are you sure you want to delete {selectedRows.size} selected report(s)?
            This action cannot be undone.
          </p>
        </Modal>
      </div>
    </div>
  );
}
