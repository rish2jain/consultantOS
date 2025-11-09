"use client";

import React, { useState, useEffect } from 'react';
import { Card } from './Card';
import { Badge } from './Badge';
import { Button } from './Button';
import { Modal } from './Modal';
import { Spinner } from './Spinner';
import { Alert } from './Alert';
import { VersionComparison } from './VersionComparison';

export interface Version {
  id: string;
  version_number: number;
  created_at: string;
  created_by: string;
  change_summary: string;
  is_current: boolean;
}

export interface VersionHistoryProps {
  reportId: string;
  currentVersion?: number;
  onVersionClick?: (version: Version) => void;
  onRestore?: (versionId: string) => void;
}

const VersionHistory: React.FC<VersionHistoryProps> = ({
  reportId,
  currentVersion,
  onVersionClick,
  onRestore
}) => {
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [restoreModalOpen, setRestoreModalOpen] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<Version | null>(null);
  const [restoring, setRestoring] = useState(false);
  const [compareModalOpen, setCompareModalOpen] = useState(false);
  const [compareVersions, setCompareVersions] = useState<{ versionA: number; versionB: number } | null>(null);

  useEffect(() => {
    fetchVersions();
  }, [reportId]);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/versions/${reportId}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch versions: ${response.statusText}`);
      }

      const data = await response.json();
      setVersions(data.versions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load version history');
    } finally {
      setLoading(false);
    }
  };

  const handleRestoreClick = (version: Version) => {
    setSelectedVersion(version);
    setRestoreModalOpen(true);
  };

  const handleRestoreConfirm = async () => {
    if (!selectedVersion) return;

    try {
      setRestoring(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/versions/${reportId}/${selectedVersion.id}/restore`,
        { method: 'POST' }
      );

      if (!response.ok) {
        throw new Error(`Failed to restore version: ${response.statusText}`);
      }

      if (onRestore) {
        onRestore(selectedVersion.id);
      }

      await fetchVersions();
      setRestoreModalOpen(false);
      setSelectedVersion(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to restore version');
    } finally {
      setRestoring(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12" role="status" aria-live="polite">
        <Spinner size="lg" />
        <span className="sr-only">Loading version history</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="error" onClose={() => setError(null)}>
        {error}
      </Alert>
    );
  }

  if (versions.length === 0) {
    return (
      <Card className="text-center py-8">
        <p className="text-gray-500">No version history available</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-900">Version History</h2>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" aria-hidden="true" />

        <div className="space-y-6" role="list" aria-label="Version history timeline">
          {versions.map((version, index) => (
            <div key={version.id} className="relative pl-12" role="listitem">
              {/* Timeline dot */}
              <div
                className={`absolute left-0 top-2 w-8 h-8 rounded-full flex items-center justify-center ${
                  version.is_current || version.version_number === currentVersion
                    ? 'bg-blue-600'
                    : 'bg-gray-300'
                }`}
                aria-hidden="true"
              >
                <span className="text-white text-xs font-bold">v{version.version_number}</span>
              </div>

              <Card
                className={`${
                  version.is_current || version.version_number === currentVersion
                    ? 'ring-2 ring-blue-600'
                    : ''
                }`}
                onClick={() => onVersionClick && onVersionClick(version)}
              >
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Version {version.version_number}
                      </h3>
                      {(version.is_current || version.version_number === currentVersion) && (
                        <Badge variant="primary">Current</Badge>
                      )}
                    </div>

                    <p className="text-sm text-gray-600 mb-2">{version.change_summary}</p>

                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                      <span>
                        <span className="font-medium">Created by:</span> {version.created_by}
                      </span>
                      <span>
                        <span className="font-medium">Date:</span> {formatDate(version.created_at)}
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {index < versions.length - 1 && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          setCompareVersions({
                            versionA: version.version_number,
                            versionB: versions[index + 1].version_number,
                          });
                          setCompareModalOpen(true);
                        }}
                        aria-label={`Compare version ${version.version_number} with version ${versions[index + 1].version_number}`}
                      >
                        Compare
                      </Button>
                    )}

                    {!version.is_current && version.version_number !== currentVersion && (
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRestoreClick(version);
                        }}
                        aria-label={`Restore version ${version.version_number}`}
                      >
                        Restore
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            </div>
          ))}
        </div>
      </div>

      {/* Restore Confirmation Modal */}
      <Modal
        isOpen={restoreModalOpen}
        onClose={() => !restoring && setRestoreModalOpen(false)}
        title="Restore Version"
      >
        <div className="space-y-4">
          {selectedVersion && (
            <>
              <Alert variant="warning">
                Restoring this version will create a new version based on the selected version.
                Your current version will remain in history.
              </Alert>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">
                  Version {selectedVersion.version_number}
                </h4>
                <p className="text-sm text-gray-600 mb-2">{selectedVersion.change_summary}</p>
                <p className="text-xs text-gray-500">
                  Created {formatDate(selectedVersion.created_at)} by {selectedVersion.created_by}
                </p>
              </div>

              <div className="flex gap-3 justify-end">
                <Button
                  variant="secondary"
                  onClick={() => setRestoreModalOpen(false)}
                  disabled={restoring}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleRestoreConfirm}
                  disabled={restoring}
                >
                  {restoring ? (
                    <>
                      <Spinner size="sm" className="mr-2" />
                      Restoring...
                    </>
                  ) : (
                    'Restore Version'
                  )}
                </Button>
              </div>
            </>
          )}
        </div>
      </Modal>

      {/* Version Comparison Modal */}
      {compareVersions && (
        <VersionComparison
          reportId={reportId}
          versionA={compareVersions.versionA}
          versionB={compareVersions.versionB}
          isOpen={compareModalOpen}
          onClose={() => {
            setCompareModalOpen(false);
            setCompareVersions(null);
          }}
        />
      )}
    </div>
  );
};

export { VersionHistory };
