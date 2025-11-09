"use client";

import React from 'react';
import { MoreVertical, Download, Trash2, Edit, Eye, Copy, Share2 } from 'lucide-react';
import { Dropdown, DropdownItem } from './Dropdown';
import { Button } from './Button';
import { Modal, useModal } from './Modal';

export interface Action<T> {
  /** Action unique key */
  key: string;
  /** Action label */
  label: string;
  /** Action icon */
  icon?: React.ReactNode;
  /** Action handler */
  onClick: (row: T, index: number) => void | Promise<void>;
  /** Whether action is disabled */
  disabled?: (row: T, index: number) => boolean;
  /** Whether action is dangerous (shows confirmation) */
  dangerous?: boolean;
  /** Confirmation message for dangerous actions */
  confirmMessage?: string;
  /** Custom confirmation title */
  confirmTitle?: string;
  /** Show divider after this action */
  divider?: boolean;
}

export interface TableActionsProps<T> {
  /** Row data */
  row: T;
  /** Row index */
  index: number;
  /** Available actions */
  actions: Action<T>[];
  /** Dropdown placement */
  placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end';
  /** Compact mode */
  compact?: boolean;
}

export function TableActions<T>({
  row,
  index,
  actions,
  placement = 'bottom-end',
  compact = false,
}: TableActionsProps<T>) {
  const { isOpen: isConfirmOpen, open: openConfirm, close: closeConfirm } = useModal();
  const [pendingAction, setPendingAction] = React.useState<Action<T> | null>(null);
  const [isExecuting, setIsExecuting] = React.useState(false);

  const handleActionClick = async (action: Action<T>) => {
    if (action.dangerous) {
      setPendingAction(action);
      openConfirm();
    } else {
      await executeAction(action);
    }
  };

  const executeAction = async (action: Action<T>) => {
    setIsExecuting(true);
    try {
      await action.onClick(row, index);
    } finally {
      setIsExecuting(false);
      if (isConfirmOpen) {
        closeConfirm();
        setPendingAction(null);
      }
    }
  };

  const handleConfirm = async () => {
    if (pendingAction) {
      await executeAction(pendingAction);
    }
  };

  const dropdownItems: DropdownItem[] = actions.map((action) => ({
    label: action.label,
    value: action.key,
    icon: action.icon,
    disabled: action.disabled?.(row, index),
    onClick: () => handleActionClick(action),
  }));

  return (
    <>
      <Dropdown
        trigger={
          <div
            className={`
              p-1 rounded hover:bg-gray-100 active:bg-gray-200 transition-colors cursor-pointer inline-flex items-center justify-center
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1
              ${compact ? '' : 'p-2'}
            `}
            onClick={(e) => e.stopPropagation()}
            role="button"
            tabIndex={0}
            aria-label="Row actions"
            aria-haspopup="true"
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                e.stopPropagation();
              }
            }}
          >
            <MoreVertical className={`${compact ? 'w-4 h-4' : 'w-5 h-5'} text-gray-600 hover:text-gray-900`} />
          </div>
        }
        items={dropdownItems}
        placement={placement}
        width="auto"
      />

      <Modal
        isOpen={isConfirmOpen}
        onClose={closeConfirm}
        title={pendingAction?.confirmTitle || 'Confirm Action'}
        size="sm"
        footer={
          <>
            <Button variant="outline" onClick={closeConfirm} disabled={isExecuting}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleConfirm}
              isLoading={isExecuting}
            >
              Confirm
            </Button>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          {pendingAction?.confirmMessage || 'Are you sure you want to perform this action?'}
        </p>
      </Modal>
    </>
  );
}

// Bulk actions component
export interface BulkAction<T> {
  /** Action unique key */
  key: string;
  /** Action label */
  label: string;
  /** Action icon */
  icon?: React.ReactNode;
  /** Action handler for multiple rows */
  onClick: (rows: T[], indices: number[]) => void | Promise<void>;
  /** Whether action is dangerous (shows confirmation) */
  dangerous?: boolean;
  /** Confirmation message */
  confirmMessage?: string;
  /** Custom confirmation title */
  confirmTitle?: string;
}

export interface BulkActionsProps<T> {
  /** All data */
  data: T[];
  /** Selected row keys */
  selectedRows: Set<string | number>;
  /** Row key accessor */
  rowKey: (row: T, index: number) => string | number;
  /** Available bulk actions */
  actions: BulkAction<T>[];
  /** Selection cleared handler */
  onClearSelection?: () => void;
}

export function BulkActions<T>({
  data,
  selectedRows,
  rowKey,
  actions,
  onClearSelection,
}: BulkActionsProps<T>) {
  const { isOpen: isConfirmOpen, open: openConfirm, close: closeConfirm } = useModal();
  const [pendingAction, setPendingAction] = React.useState<BulkAction<T> | null>(null);
  const [isExecuting, setIsExecuting] = React.useState(false);

  const selectedData = React.useMemo(() => {
    const rows: T[] = [];
    const indices: number[] = [];

    data.forEach((row, index) => {
      const key = rowKey(row, index);
      if (selectedRows.has(key)) {
        rows.push(row);
        indices.push(index);
      }
    });

    return { rows, indices };
  }, [data, selectedRows, rowKey]);

  const handleActionClick = async (action: BulkAction<T>) => {
    if (action.dangerous) {
      setPendingAction(action);
      openConfirm();
    } else {
      await executeAction(action);
    }
  };

  const executeAction = async (action: BulkAction<T>) => {
    setIsExecuting(true);
    try {
      await action.onClick(selectedData.rows, selectedData.indices);
      onClearSelection?.();
    } finally {
      setIsExecuting(false);
      if (isConfirmOpen) {
        closeConfirm();
        setPendingAction(null);
      }
    }
  };

  const handleConfirm = async () => {
    if (pendingAction) {
      await executeAction(pendingAction);
    }
  };

  if (selectedRows.size === 0) {
    return null;
  }

  return (
    <>
      <div className="flex items-center gap-3 px-4 py-3 bg-primary-50 border-b border-primary-200">
        <span className="text-sm font-medium text-primary-900">
          {selectedRows.size} selected
        </span>
        <div className="flex items-center gap-2">
          {actions.map((action) => (
            <Button
              key={action.key}
              variant={action.dangerous ? 'danger' : 'primary'}
              size="sm"
              onClick={() => handleActionClick(action)}
              leftIcon={action.icon}
              disabled={isExecuting}
            >
              {action.label}
            </Button>
          ))}
          {onClearSelection && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearSelection}
              disabled={isExecuting}
            >
              Clear selection
            </Button>
          )}
        </div>
      </div>

      <Modal
        isOpen={isConfirmOpen}
        onClose={closeConfirm}
        title={pendingAction?.confirmTitle || 'Confirm Bulk Action'}
        size="sm"
        footer={
          <>
            <Button variant="outline" onClick={closeConfirm} disabled={isExecuting}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleConfirm}
              isLoading={isExecuting}
            >
              Confirm
            </Button>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          {pendingAction?.confirmMessage ||
            `Are you sure you want to perform this action on ${selectedRows.size} selected items?`}
        </p>
      </Modal>
    </>
  );
}

// Common action presets
export const commonActions = {
  view: <T,>(onClick: (row: T, index: number) => void): Action<T> => ({
    key: 'view',
    label: 'View',
    icon: <Eye className="w-4 h-4" />,
    onClick,
  }),

  edit: <T,>(onClick: (row: T, index: number) => void): Action<T> => ({
    key: 'edit',
    label: 'Edit',
    icon: <Edit className="w-4 h-4" />,
    onClick,
  }),

  duplicate: <T,>(onClick: (row: T, index: number) => void): Action<T> => ({
    key: 'duplicate',
    label: 'Duplicate',
    icon: <Copy className="w-4 h-4" />,
    onClick,
  }),

  share: <T,>(onClick: (row: T, index: number) => void): Action<T> => ({
    key: 'share',
    label: 'Share',
    icon: <Share2 className="w-4 h-4" />,
    onClick,
  }),

  delete: <T,>(onClick: (row: T, index: number) => void): Action<T> => ({
    key: 'delete',
    label: 'Delete',
    icon: <Trash2 className="w-4 h-4" />,
    onClick,
    dangerous: true,
    confirmMessage: 'Are you sure you want to delete this item? This action cannot be undone.',
    confirmTitle: 'Delete Item',
    divider: true,
  }),

  download: <T,>(onClick: (row: T, index: number) => void): Action<T> => ({
    key: 'download',
    label: 'Download',
    icon: <Download className="w-4 h-4" />,
    onClick,
  }),
};

// Export functionality
export interface ExportOptions {
  /** Export format */
  format: 'csv' | 'json';
  /** File name (without extension) */
  filename?: string;
  /** Columns to include (if not specified, all columns) */
  columns?: string[];
}

export const exportData = <T,>(
  data: T[],
  options: ExportOptions = { format: 'csv' }
) => {
  const { format, filename = 'export', columns } = options;

  if (format === 'csv') {
    exportToCSV(data, filename, columns);
  } else if (format === 'json') {
    exportToJSON(data, filename);
  }
};

const exportToCSV = <T,>(data: T[], filename: string, columns?: string[]) => {
  if (data.length === 0) return;

  const keys = columns || Object.keys(data[0] as object);
  const csvContent = [
    keys.join(','),
    ...data.map((row) =>
      keys
        .map((key) => {
          const value = (row as any)[key];
          // Escape quotes and wrap in quotes if contains comma
          const stringValue = String(value ?? '');
          if (stringValue.includes(',') || stringValue.includes('"')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
          }
          return stringValue;
        })
        .join(',')
    ),
  ].join('\n');

  downloadFile(csvContent, `${filename}.csv`, 'text/csv');
};

const exportToJSON = <T,>(data: T[], filename: string) => {
  const jsonContent = JSON.stringify(data, null, 2);
  downloadFile(jsonContent, `${filename}.json`, 'application/json');
};

const downloadFile = (content: string, filename: string, type: string) => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
