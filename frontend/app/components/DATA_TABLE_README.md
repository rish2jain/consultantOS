# Enhanced Data Table Components

Comprehensive, accessible, and feature-rich data table system for ConsultantOS frontend.

## Components Overview

### 1. DataTable.tsx - Core Table Component

**File Path**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/DataTable.tsx`

Generic table component with TypeScript support for any data type.

**Features**:
- Generic TypeScript with `<T>` for type safety
- Column definitions with custom renderers
- Row selection (single/multi/none)
- Empty state handling with custom components
- Loading skeleton state
- Responsive design (stack on mobile via hideOnMobile)
- Sticky header support
- Striped/bordered/compact modes
- Hover effects
- Custom row styling
- Scrollable with max height

**Key Props**:
```typescript
interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: (row: T, index: number) => string | number;
  isLoading?: boolean;
  emptyMessage?: string;
  selectionMode?: 'none' | 'single' | 'multi';
  selectedRows?: Set<string | number>;
  onSelectionChange?: (selectedKeys: Set<string | number>) => void;
  onRowClick?: (row: T, index: number) => void;
  // ... styling props
}
```

**Column Configuration**:
```typescript
interface Column<T> {
  key: string;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, row: T, index: number) => React.ReactNode;
  accessor?: (row: T) => any;
  width?: string;
  align?: 'left' | 'center' | 'right';
  hideOnMobile?: boolean;
}
```

### 2. TablePagination.tsx - Pagination Controls

**File Path**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/TablePagination.tsx`

Full-featured pagination with page size selection.

**Features**:
- Page size selector (10, 25, 50, 100)
- Page navigation (first, prev, next, last)
- Current page indicator with smart ellipsis
- Total items/pages display
- Responsive (simplified on mobile)
- Keyboard navigation
- ARIA attributes

**usePagination Hook**:
```typescript
const {
  currentPage,
  pageSize,
  totalPages,
  startIndex,
  endIndex,
  handlePageChange,
  handlePageSizeChange,
} = usePagination(totalItems, initialPageSize);
```

### 3. TableSort.tsx - Column Sorting

**File Path**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/TableSort.tsx`

Column sorting with visual indicators and multi-column support.

**Features**:
- Sort indicators (up/down/unsorted arrows)
- Click to cycle: asc → desc → null
- Multi-column sort support (with shift+click)
- Custom sort functions per column
- String, number, and date sorting
- Keyboard accessible (Enter/Space)

**useSort Hook**:
```typescript
const { sortConfig, handleSort, sortData } = useSort<T>({
  initialSort?: SortConfig,
  customSorters?: Record<string, (a: T, b: T) => number>,
});
```

**useMultiSort Hook** (for advanced use):
```typescript
const { sortConfigs, handleSort, sortData } = useMultiSort<T>();
```

### 4. TableFilters.tsx - Column Filters

**File Path**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/TableFilters.tsx`

Flexible filtering system with multiple filter types.

**Features**:
- Text search per column
- Select dropdowns for categorical data
- Date filters (single date or range)
- Clear all filters button
- Active filter count
- Custom filter functions

**Filter Types**:
- `text`: Text input with search
- `select`: Dropdown with predefined options
- `date`: Single date picker
- `dateRange`: Date range (from/to)

**useFilters Hook**:
```typescript
const {
  filterValues,
  handleFilterChange,
  handleClearAll,
  filterData,
  activeFilterCount,
} = useFilters<T>({
  initialFilters?: Record<string, any>,
  customFilters?: Record<string, (row: T, value: any) => boolean>,
});
```

### 5. TableActions.tsx - Row Actions & Bulk Operations

**File Path**: `/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/TableActions.tsx`

Row-level actions and bulk operations with confirmation modals.

**Features**:
- Dropdown menu per row (MoreVertical icon)
- Bulk actions for selected rows
- Confirmation modals for dangerous actions
- Common action presets (view, edit, delete, etc.)
- Export functionality (CSV/JSON)
- Async action support

**Common Actions**:
```typescript
import { commonActions } from './TableActions';

const actions = [
  commonActions.view(handleView),
  commonActions.edit(handleEdit),
  commonActions.duplicate(handleDuplicate),
  commonActions.share(handleShare),
  commonActions.download(handleDownload),
  commonActions.delete(handleDelete), // with confirmation
];
```

**Export Data**:
```typescript
import { exportData } from './TableActions';

exportData(data, {
  format: 'csv' | 'json',
  filename: 'my-export',
  columns: ['id', 'name', 'email'], // optional
});
```

## Complete Usage Example

```tsx
import React from 'react';
import {
  DataTable,
  Column,
  TablePagination,
  usePagination,
  useSort,
  useFilters,
  TableActions,
  BulkActions,
  commonActions,
  exportData,
} from './components';

interface MyData {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export const MyTablePage: React.FC = () => {
  const [data, setData] = React.useState<MyData[]>([/* ... */]);
  const [selectedRows, setSelectedRows] = React.useState<Set<string>>(new Set());

  // Hooks
  const pagination = usePagination(data.length, 10);
  const sorting = useSort<MyData>();
  const filtering = useFilters<MyData>();

  // Apply filters, sorting, and pagination
  const processedData = React.useMemo(() => {
    let result = data;
    result = filtering.filterData(result);
    result = sorting.sortData(result);
    return result.slice(pagination.startIndex, pagination.endIndex);
  }, [data, filtering, sorting, pagination.startIndex, pagination.endIndex]);

  // Columns
  const columns: Column<MyData>[] = [
    {
      key: 'name',
      label: 'Name',
      sortable: true,
      filterable: true,
      filterType: 'text',
    },
    {
      key: 'email',
      label: 'Email',
      sortable: true,
      filterable: true,
      filterType: 'text',
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      filterType: 'select',
      filterOptions: [
        { label: 'Active', value: 'active' },
        { label: 'Inactive', value: 'inactive' },
      ],
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
            commonActions.delete(() => handleDelete(row.id)),
          ]}
        />
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <BulkActions
        data={data}
        selectedRows={selectedRows}
        rowKey={(row) => row.id}
        actions={[
          {
            key: 'export',
            label: 'Export',
            onClick: (rows) => exportData(rows, { format: 'csv' }),
          },
        ]}
        onClearSelection={() => setSelectedRows(new Set())}
      />

      <DataTable
        columns={columns}
        data={processedData}
        rowKey={(row) => row.id}
        selectionMode="multi"
        selectedRows={selectedRows}
        onSelectionChange={setSelectedRows}
        hoverable
        striped
      />

      <TablePagination
        currentPage={pagination.currentPage}
        totalPages={pagination.totalPages}
        totalItems={data.length}
        pageSize={pagination.pageSize}
        onPageChange={pagination.handlePageChange}
        onPageSizeChange={pagination.handlePageSizeChange}
      />
    </div>
  );
};
```

## Accessibility Features

All components follow WCAG 2.1 AA standards:

- Keyboard navigation (Tab, Enter, Space, Arrow keys)
- ARIA attributes (roles, labels, descriptions)
- Focus management and indicators
- Screen reader support
- Color contrast compliance
- Focus trap in modals
- Semantic HTML elements

## Responsive Behavior

- **Mobile**: Tables scroll horizontally, pagination simplified
- **Tablet**: Full features with adjusted layouts
- **Desktop**: Complete feature set

Use `hideOnMobile` on columns to hide less important data on small screens.

## Performance Considerations

- **Memoization**: Use `useMemo` for processed data
- **Controlled State**: Parent manages data, sorting, filtering
- **Pagination**: Only render visible rows
- **Virtual Scrolling**: Consider for >1000 rows (not included, but can be added)

## Integration with ConsultantOS

Use these components for:
- Report listings (JobHistory, ReportsList)
- Template library tables
- User management tables
- Analytics dashboards
- Job queue displays

## Additional Files

- **DataTableExample.tsx**: Complete working example with all features
- **index.ts**: Updated with all exports

## Dependencies

All components use Phase 1 base components:
- Button
- Input
- Dropdown
- Modal
- Spinner
- Badge (for status indicators)

## TypeScript Support

Full TypeScript support with:
- Generic types for data
- Strict type checking
- IntelliSense support
- Type-safe custom renderers and sorters

## Future Enhancements

Consider adding:
- Column reordering (drag & drop)
- Column visibility toggle
- Virtual scrolling for large datasets
- Saved filter presets
- Advanced search across all columns
- Column resizing
- Export to Excel/PDF
