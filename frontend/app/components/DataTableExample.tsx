"use client";

import React from 'react';
import {
  DataTable,
  Column,
  TablePagination,
  usePagination,
  useSort,
  TableFilters,
  useFilters,
  TableActions,
  BulkActions,
  commonActions,
  exportData,
} from './index';
import { Badge } from './Badge';

// Example data type
interface Report {
  id: string;
  company: string;
  industry: string;
  frameworks: string[];
  status: 'completed' | 'processing' | 'failed';
  createdAt: string;
  confidence: number;
}

// Example usage demonstrating all table features
const DataTableExample: React.FC = () => {
  // Sample data
  const [reports] = React.useState<Report[]>([
    {
      id: '1',
      company: 'Tesla',
      industry: 'Electric Vehicles',
      frameworks: ['Porter', 'SWOT'],
      status: 'completed',
      createdAt: '2024-01-15',
      confidence: 0.92,
    },
    {
      id: '2',
      company: 'Apple',
      industry: 'Technology',
      frameworks: ['Blue Ocean', 'PESTEL'],
      status: 'processing',
      createdAt: '2024-01-16',
      confidence: 0.85,
    },
    // ... more sample data
  ]);

  // Selection state
  const [selectedRows, setSelectedRows] = React.useState<Set<string | number>>(
    new Set()
  );

  // Pagination hook
  const {
    currentPage,
    pageSize,
    totalPages,
    startIndex,
    endIndex,
    handlePageChange,
    handlePageSizeChange,
  } = usePagination(reports.length, 10);

  // Sorting hook
  const { sortData } = useSort<Report>({
    customSorters: {
      confidence: (a, b) => a.confidence - b.confidence,
      createdAt: (a, b) =>
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime(),
    },
  });

  // Filtering hook
  const {
    filterValues,
    handleFilterChange,
    handleClearAll,
    filterData,
  } = useFilters<Report>({
    customFilters: {
      status: (row, value) => row.status === value,
    },
  });

  // Apply filters, sorting, and pagination
  const processedData = React.useMemo(() => {
    let result = reports;
    result = filterData(result);
    result = sortData(result);
    return result.slice(startIndex, endIndex);
  }, [reports, filterData, sortData, startIndex, endIndex]);

  // Column definitions
  const columns: Column<Report>[] = [
    {
      key: 'company',
      label: 'Company',
      sortable: true,
      filterable: true,
      filterType: 'text',
      render: (value) => <span className="font-medium">{value}</span>,
    },
    {
      key: 'industry',
      label: 'Industry',
      sortable: true,
      filterable: true,
      filterType: 'select',
      filterOptions: [
        { label: 'Technology', value: 'Technology' },
        { label: 'Electric Vehicles', value: 'Electric Vehicles' },
      ],
    },
    {
      key: 'frameworks',
      label: 'Frameworks',
      render: (value: string[]) => (
        <div className="flex gap-1">
          {value.map((fw) => (
            <Badge key={fw} variant="default" size="sm">
              {fw}
            </Badge>
          ))}
        </div>
      ),
      hideOnMobile: true,
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      filterType: 'select',
      filterOptions: [
        { label: 'Completed', value: 'completed' },
        { label: 'Processing', value: 'processing' },
        { label: 'Failed', value: 'failed' },
      ],
      render: (value: Report['status']) => {
        const variants = {
          completed: 'success',
          processing: 'warning',
          failed: 'danger',
        };
        return (
          <Badge variant={variants[value] as any}>
            {value.charAt(0).toUpperCase() + value.slice(1)}
          </Badge>
        );
      },
    },
    {
      key: 'confidence',
      label: 'Confidence',
      sortable: true,
      align: 'right',
      render: (value: number) => `${(value * 100).toFixed(0)}%`,
    },
    {
      key: 'createdAt',
      label: 'Created',
      sortable: true,
      filterable: true,
      filterType: 'date',
      render: (value) => new Date(value).toLocaleDateString(),
      hideOnMobile: true,
    },
    {
      key: 'actions',
      label: 'Actions',
      align: 'right',
      render: (_, row, index) => (
        <TableActions
          row={row}
          index={index}
          actions={[
            commonActions.view(() => console.log('View', row)),
            commonActions.edit(() => console.log('Edit', row)),
            commonActions.download(() => console.log('Download', row)),
            commonActions.delete(() => console.log('Delete', row)),
          ]}
        />
      ),
    },
  ];

  // Filter configurations
  const filterConfigs = React.useMemo(
    () =>
      columns
        .filter((col) => col.filterable)
        .map((col) => ({
          key: col.key,
          type: col.filterType || 'text',
          value: filterValues[col.key] || '',
          options: col.filterOptions,
        })),
    [columns, filterValues]
  );

  // Bulk actions
  const bulkActions = [
    {
      key: 'export',
      label: 'Export Selected',
      icon: <span>📤</span>,
      onClick: (rows: Report[]) => {
        exportData(rows, { format: 'csv', filename: 'reports' });
      },
    },
    {
      key: 'delete',
      label: 'Delete Selected',
      icon: <span>🗑️</span>,
      onClick: (rows: Report[]) => {
        console.log('Delete', rows);
      },
      dangerous: true,
      confirmMessage: 'Are you sure you want to delete the selected reports?',
    },
  ];

  return (
    <div className="space-y-4">
      {/* Filters */}
      <TableFilters
        filters={filterConfigs}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
      />

      {/* Bulk Actions (shown when rows selected) */}
      <BulkActions
        data={reports}
        selectedRows={selectedRows}
        rowKey={(row) => row.id}
        actions={bulkActions}
        onClearSelection={() => setSelectedRows(new Set())}
      />

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={processedData}
        rowKey={(row) => row.id}
        selectionMode="multi"
        selectedRows={selectedRows}
        onSelectionChange={setSelectedRows}
        onRowClick={(row) => console.log('Row clicked', row)}
        hoverable
        striped
        stickyHeader
        maxHeight="600px"
      />

      {/* Pagination */}
      <TablePagination
        currentPage={currentPage}
        totalPages={totalPages}
        totalItems={filterData(reports).length}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        showPageSizeSelector
        showTotal
        showFirstLast
      />
    </div>
  );
};

/**
 * USAGE EXAMPLES
 *
 * 1. Basic Table (no features):
 * ```tsx
 * <DataTable
 *   columns={columns}
 *   data={data}
 *   rowKey={(row) => row.id}
 * />
 * ```
 *
 * 2. Table with Sorting:
 * ```tsx
 * const { sortConfig, handleSort, sortData } = useSort<MyData>();
 *
 * <DataTable
 *   columns={columns.map(col => ({
 *     ...col,
 *     label: col.sortable ? (
 *       <TableSort
 *         columnKey={col.key}
 *         label={col.label}
 *         sortConfig={sortConfig}
 *         onSort={handleSort}
 *       />
 *     ) : col.label
 *   }))}
 *   data={sortData(data)}
 *   rowKey={(row) => row.id}
 * />
 * ```
 *
 * 3. Table with Pagination:
 * ```tsx
 * const { currentPage, pageSize, startIndex, endIndex, ... } = usePagination(data.length);
 *
 * <DataTable
 *   data={data.slice(startIndex, endIndex)}
 *   ...
 * />
 * <TablePagination ... />
 * ```
 *
 * 4. Table with Filters:
 * ```tsx
 * const { filterData, handleFilterChange, ... } = useFilters<MyData>();
 *
 * <TableFilters ... />
 * <DataTable data={filterData(data)} ... />
 * ```
 *
 * 5. Export Data:
 * ```tsx
 * <Button onClick={() => exportData(data, { format: 'csv', filename: 'export' })}>
 *   Export to CSV
 * </Button>
 * ```
 *
 * 6. Row Actions:
 * ```tsx
 * {
 *   key: 'actions',
 *   render: (_, row, index) => (
 *     <TableActions
 *       row={row}
 *       index={index}
 *       actions={[
 *         commonActions.view(handleView),
 *         commonActions.edit(handleEdit),
 *         commonActions.delete(handleDelete),
 *       ]}
 *     />
 *   )
 * }
 * ```
 */

export default DataTableExample;
