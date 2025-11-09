"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './Card';
import { Button } from './Button';
import { Badge } from './Badge';
import { Alert } from './Alert';
import { Spinner, InlineLoading } from './Spinner';
import { TablePagination, usePagination } from './TablePagination';
import { Dropdown, DropdownItem } from './Dropdown';
import {
  Copy,
  Edit,
  Trash2,
  ExternalLink,
  Calendar,
  Eye,
  Download,
  Filter,
  Check,
  MoreVertical,
} from 'lucide-react';
import { Modal } from './Modal';

export interface ShareListProps {
  /** User ID to filter shares */
  userId: string;
  /** Share click handler */
  onShareClick?: (shareId: string) => void;
  /** Revoke handler */
  onRevoke?: (shareId: string) => void;
}

interface ShareItem {
  share_id: string;
  report_id: string;
  report_name: string;
  share_link: string;
  created_at: string;
  expires_at?: string;
  access_count: number;
  permissions: 'view' | 'download';
  is_active: boolean;
  password_protected: boolean;
}

type FilterStatus = 'all' | 'active' | 'expired';
type SortField = 'created_at' | 'access_count' | 'expires_at';
type SortOrder = 'asc' | 'desc';

const FILTER_OPTIONS: DropdownItem[] = [
  { label: 'All Shares', value: 'all' },
  { label: 'Active Only', value: 'active' },
  { label: 'Expired Only', value: 'expired' },
];

const SORT_OPTIONS: DropdownItem[] = [
  { label: 'Newest First', value: 'created_at-desc' },
  { label: 'Oldest First', value: 'created_at-asc' },
  { label: 'Most Accessed', value: 'access_count-desc' },
  { label: 'Least Accessed', value: 'access_count-asc' },
  { label: 'Expiring Soon', value: 'expires_at-asc' },
];

export const ShareList: React.FC<ShareListProps> = ({
  userId,
  onShareClick,
  onRevoke,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [shares, setShares] = useState<ShareItem[]>([]);
  const [filteredShares, setFilteredShares] = useState<ShareItem[]>([]);

  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [sortOption, setSortOption] = useState('created_at-desc');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [revokeConfirmId, setRevokeConfirmId] = useState<string | null>(null);
  const [isRevoking, setIsRevoking] = useState(false);

  const {
    currentPage,
    pageSize,
    totalPages,
    startIndex,
    endIndex,
    handlePageChange,
    handlePageSizeChange,
  } = usePagination(filteredShares.length, 10);

  useEffect(() => {
    loadShares();
  }, [userId]);

  useEffect(() => {
    applyFiltersAndSort();
  }, [shares, filterStatus, sortOption]);

  const loadShares = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/shares/my-shares', {
        headers: {
          'X-User-ID': userId,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load shares');
      }

      const data = await response.json();
      setShares(data.shares || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const applyFiltersAndSort = () => {
    let filtered = [...shares];

    // Apply status filter
    if (filterStatus === 'active') {
      filtered = filtered.filter((share) => share.is_active && !isExpired(share.expires_at));
    } else if (filterStatus === 'expired') {
      filtered = filtered.filter((share) => !share.is_active || isExpired(share.expires_at));
    }

    // Apply sorting
    const [field, order] = sortOption.split('-') as [SortField, SortOrder];

    filtered.sort((a, b) => {
      let aValue: number | string = 0;
      let bValue: number | string = 0;

      if (field === 'created_at') {
        aValue = new Date(a.created_at).getTime();
        bValue = new Date(b.created_at).getTime();
      } else if (field === 'access_count') {
        aValue = a.access_count;
        bValue = b.access_count;
      } else if (field === 'expires_at') {
        aValue = a.expires_at ? new Date(a.expires_at).getTime() : Infinity;
        bValue = b.expires_at ? new Date(b.expires_at).getTime() : Infinity;
      }

      if (order === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredShares(filtered);
    handlePageChange(1); // Reset to first page when filters change (1-based indexing)
  };

  const isExpired = (expiresAt?: string): boolean => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  const handleCopyLink = async (shareLink: string, shareId: string) => {
    try {
      await navigator.clipboard.writeText(shareLink);
      setCopiedId(shareId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      setError('Failed to copy link');
    }
  };

  const handleRevoke = async (shareId: string) => {
    setIsRevoking(true);

    try {
      const response = await fetch(`/api/shares/${shareId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to revoke share');
      }

      // Remove from list or reload
      setShares((prev) => prev.map((s) =>
        s.share_id === shareId ? { ...s, is_active: false } : s
      ));
      setRevokeConfirmId(null);
      onRevoke?.(shareId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to revoke share');
    } finally {
      setIsRevoking(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusBadge = (share: ShareItem) => {
    if (!share.is_active) {
      return <Badge variant="danger">Revoked</Badge>;
    }
    if (isExpired(share.expires_at)) {
      return <Badge variant="warning">Expired</Badge>;
    }
    return <Badge variant="success" dot>Active</Badge>;
  };

  const paginatedShares = filteredShares.slice(startIndex, endIndex);

  if (isLoading) {
    return (
      <Card padding="lg">
        <InlineLoading message="Loading shares..." centered />
      </Card>
    );
  }

  return (
    <>
      <Card padding="lg">
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <CardTitle>My Shared Reports</CardTitle>

            <div className="flex items-center gap-3">
              <Dropdown
                trigger={
                  <span className="flex items-center gap-2">
                    <Filter className="w-4 h-4" />
                    {FILTER_OPTIONS.find(opt => opt.value === filterStatus)?.label}
                  </span>
                }
                items={FILTER_OPTIONS}
                value={filterStatus}
                onChange={(value) => setFilterStatus(value as FilterStatus)}
              />

              <Dropdown
                items={SORT_OPTIONS}
                value={sortOption}
                onChange={setSortOption}
              />
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {error && (
            <Alert
              variant="error"
              description={error}
              dismissible
              onClose={() => setError(null)}
              className="mb-4"
            />
          )}

          {filteredShares.length === 0 ? (
            <div className="text-center py-12">
              <ExternalLink className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No shares found
              </h3>
              <p className="text-gray-600">
                {filterStatus !== 'all'
                  ? 'Try changing the filter to see more results'
                  : 'Create your first share to get started'}
              </p>
            </div>
          ) : (
            <>
              {/* Desktop Table View */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left text-xs font-semibold text-gray-600 uppercase tracking-wider py-3 px-4">
                        Report
                      </th>
                      <th className="text-left text-xs font-semibold text-gray-600 uppercase tracking-wider py-3 px-4">
                        Created
                      </th>
                      <th className="text-left text-xs font-semibold text-gray-600 uppercase tracking-wider py-3 px-4">
                        Expires
                      </th>
                      <th className="text-left text-xs font-semibold text-gray-600 uppercase tracking-wider py-3 px-4">
                        Access
                      </th>
                      <th className="text-left text-xs font-semibold text-gray-600 uppercase tracking-wider py-3 px-4">
                        Status
                      </th>
                      <th className="text-right text-xs font-semibold text-gray-600 uppercase tracking-wider py-3 px-4">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {paginatedShares.map((share) => (
                      <tr
                        key={share.share_id}
                        className="hover:bg-gray-50 transition-colors"
                      >
                        <td className="py-3 px-4">
                          <div>
                            <p className="font-medium text-gray-900">
                              {share.report_name}
                            </p>
                            <div className="flex items-center gap-2 mt-1">
                              {share.password_protected && (
                                <Badge variant="info" size="sm">Password</Badge>
                              )}
                              {share.permissions === 'download' ? (
                                <Badge variant="default" size="sm">
                                  <Download className="w-3 h-3 mr-1" />
                                  Download
                                </Badge>
                              ) : (
                                <Badge variant="default" size="sm">
                                  <Eye className="w-3 h-3 mr-1" />
                                  View
                                </Badge>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {formatDate(share.created_at)}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {share.expires_at ? formatDate(share.expires_at) : 'Never'}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {share.access_count} views
                        </td>
                        <td className="py-3 px-4">
                          {getStatusBadge(share)}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleCopyLink(share.share_link, share.share_id)}
                              leftIcon={
                                copiedId === share.share_id ? (
                                  <Check className="w-4 h-4" />
                                ) : (
                                  <Copy className="w-4 h-4" />
                                )
                              }
                              aria-label="Copy link"
                            >
                              {copiedId === share.share_id ? 'Copied' : 'Copy'}
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => onShareClick?.(share.share_id)}
                              leftIcon={<Edit className="w-4 h-4" />}
                              aria-label="Edit share"
                            >
                              Edit
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setRevokeConfirmId(share.share_id)}
                              disabled={!share.is_active}
                              leftIcon={<Trash2 className="w-4 h-4" />}
                              aria-label="Revoke share"
                            >
                              Revoke
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile Card View */}
              <div className="md:hidden space-y-4">
                {paginatedShares.map((share) => (
                  <Card
                    key={share.share_id}
                    padding="md"
                    variant="outlined"
                    hoverable
                  >
                    <div className="space-y-3">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">
                            {share.report_name}
                          </h3>
                          <div className="flex flex-wrap items-center gap-2 mt-2">
                            {getStatusBadge(share)}
                            {share.password_protected && (
                              <Badge variant="info" size="sm">Password</Badge>
                            )}
                            {share.permissions === 'download' ? (
                              <Badge variant="default" size="sm">
                                <Download className="w-3 h-3 mr-1" />
                                Download
                              </Badge>
                            ) : (
                              <Badge variant="default" size="sm">
                                <Eye className="w-3 h-3 mr-1" />
                                View
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <p className="text-gray-500">Created</p>
                          <p className="text-gray-900 font-medium">
                            {formatDate(share.created_at)}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Expires</p>
                          <p className="text-gray-900 font-medium">
                            {share.expires_at ? formatDate(share.expires_at) : 'Never'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Access</p>
                          <p className="text-gray-900 font-medium">
                            {share.access_count} views
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 pt-2 border-t border-gray-200">
                        <Button
                          size="sm"
                          variant="outline"
                          fullWidth
                          onClick={() => handleCopyLink(share.share_link, share.share_id)}
                          leftIcon={
                            copiedId === share.share_id ? (
                              <Check className="w-4 h-4" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )
                          }
                        >
                          {copiedId === share.share_id ? 'Copied' : 'Copy Link'}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => onShareClick?.(share.share_id)}
                          leftIcon={<Edit className="w-4 h-4" />}
                        >
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => setRevokeConfirmId(share.share_id)}
                          disabled={!share.is_active}
                          leftIcon={<Trash2 className="w-4 h-4" />}
                        >
                          Revoke
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Pagination */}
              {filteredShares.length > 10 && (
                <div className="mt-6">
                  <TablePagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    totalItems={filteredShares.length}
                    pageSize={pageSize}
                    onPageChange={handlePageChange}
                    onPageSizeChange={handlePageSizeChange}
                    pageSizeOptions={[10, 25, 50]}
                  />
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Revoke Confirmation Modal */}
      <Modal
        isOpen={revokeConfirmId !== null}
        onClose={() => setRevokeConfirmId(null)}
        title="Revoke Share"
        size="sm"
        footer={
          <>
            <Button variant="ghost" onClick={() => setRevokeConfirmId(null)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => revokeConfirmId && handleRevoke(revokeConfirmId)}
              isLoading={isRevoking}
            >
              Revoke
            </Button>
          </>
        }
      >
        <Alert
          variant="warning"
          description="This will permanently revoke the share link. Anyone with the link will no longer be able to access the report."
          showIcon
        />
      </Modal>
    </>
  );
};
