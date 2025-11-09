"use client";

import React, { useState, useEffect } from "react";
import { Modal } from "./Modal";
import { Button } from "./Button";
import { Spinner } from "./Spinner";
import { Alert } from "./Alert";
import { Tabs, TabList, Tab, TabPanels, TabPanel } from "./Tabs";
import { Badge } from "./Badge";
import { Card } from "./Card";

interface VersionDiff {
  version_a: {
    version_number: number;
    created_at: string;
    created_by: string;
  };
  version_b: {
    version_number: number;
    created_at: string;
    created_by: string;
  };
  changes: {
    frameworks_added: string[];
    frameworks_removed: string[];
    content_changes: Array<{
      section: string;
      changes: string[];
    }>;
    metrics_changed: Array<{
      metric: string;
      old_value: string | number;
      new_value: string | number;
    }>;
  };
}

export interface VersionComparisonProps {
  reportId: string;
  versionA: number;
  versionB: number;
  isOpen: boolean;
  onClose?: () => void;
  onRestore?: (versionNumber: number) => void;
}

const VersionComparison: React.FC<VersionComparisonProps> = ({
  reportId,
  versionA,
  versionB,
  isOpen,
  onClose,
  onRestore,
}) => {
  const [diff, setDiff] = useState<VersionDiff | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchComparison();
  }, [reportId, versionA, versionB]);

  const fetchComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/versions/${reportId}/compare?v1=${versionA}&v2=${versionB}`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch comparison: ${response.statusText}`);
      }

      const data = await response.json();
      setDiff(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load version comparison"
      );
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const renderDiffContent = () => {
    if (!diff) return null;

    return (
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabList>
          <Tab value="overview">Overview</Tab>
          <Tab value="frameworks">Frameworks</Tab>
          <Tab value="content">Content Changes</Tab>
          <Tab value="metrics">Metrics</Tab>
        </TabList>
        <TabPanels>
          <TabPanel value="overview">
            <div className="space-y-6">
              {/* Version Headers */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="bg-red-50 border-red-200">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">
                      Version {diff.version_a.version_number}
                    </h3>
                    <Badge variant="danger">Old</Badge>
                  </div>
                  <p className="text-xs text-gray-600">
                    {formatDate(diff.version_a.created_at)}
                  </p>
                  <p className="text-xs text-gray-500">
                    by {diff.version_a.created_by}
                  </p>
                </Card>

                <Card className="bg-green-50 border-green-200">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">
                      Version {diff.version_b.version_number}
                    </h3>
                    <Badge variant="success">New</Badge>
                  </div>
                  <p className="text-xs text-gray-600">
                    {formatDate(diff.version_b.created_at)}
                  </p>
                  <p className="text-xs text-gray-500">
                    by {diff.version_b.created_by}
                  </p>
                </Card>
              </div>

              {/* Summary Statistics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {diff.changes.frameworks_added.length}
                  </div>
                  <div className="text-xs text-gray-600">Frameworks Added</div>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {diff.changes.frameworks_removed.length}
                  </div>
                  <div className="text-xs text-gray-600">
                    Frameworks Removed
                  </div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {diff.changes.content_changes.length}
                  </div>
                  <div className="text-xs text-gray-600">Sections Changed</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {diff.changes.metrics_changed.length}
                  </div>
                  <div className="text-xs text-gray-600">Metrics Changed</div>
                </div>
              </div>
            </div>
          </TabPanel>

          <TabPanel value="frameworks">
            <div className="space-y-4">
              {diff.changes.frameworks_added.length > 0 && (
                <Card>
                  <h4 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
                    <span className="text-xl">+</span> Added Frameworks
                  </h4>
                  <ul className="space-y-2" role="list">
                    {diff.changes.frameworks_added.map((framework, idx) => (
                      <li
                        key={idx}
                        className="flex items-center gap-2 text-sm text-gray-700"
                      >
                        <span
                          className="w-2 h-2 bg-green-500 rounded-full"
                          aria-hidden="true"
                        />
                        {framework}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}

              {diff.changes.frameworks_removed.length > 0 && (
                <Card>
                  <h4 className="font-semibold text-red-700 mb-3 flex items-center gap-2">
                    <span className="text-xl">-</span> Removed Frameworks
                  </h4>
                  <ul className="space-y-2" role="list">
                    {diff.changes.frameworks_removed.map((framework, idx) => (
                      <li
                        key={idx}
                        className="flex items-center gap-2 text-sm text-gray-700"
                      >
                        <span
                          className="w-2 h-2 bg-red-500 rounded-full"
                          aria-hidden="true"
                        />
                        {framework}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}

              {diff.changes.frameworks_added.length === 0 &&
                diff.changes.frameworks_removed.length === 0 && (
                  <p className="text-center text-gray-500 py-8">
                    No framework changes
                  </p>
                )}
            </div>
          </TabPanel>

          <TabPanel value="content">
            <div className="space-y-4">
              {diff.changes.content_changes.length > 0 ? (
                diff.changes.content_changes.map((section, idx) => (
                  <Card key={idx}>
                    <h4 className="font-semibold text-gray-900 mb-3">
                      {section.section}
                    </h4>
                    <ul className="space-y-2" role="list">
                      {section.changes.map((change, changeIdx) => (
                        <li
                          key={changeIdx}
                          className="text-sm text-gray-700 pl-4 border-l-2 border-blue-300"
                        >
                          {change}
                        </li>
                      ))}
                    </ul>
                  </Card>
                ))
              ) : (
                <p className="text-center text-gray-500 py-8">
                  No content changes
                </p>
              )}
            </div>
          </TabPanel>

          <TabPanel value="metrics">
            <div className="space-y-4">
              {diff.changes.metrics_changed.length > 0 ? (
                <Card>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            Metric
                          </th>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            Old Value
                          </th>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            New Value
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {diff.changes.metrics_changed.map((metric, idx) => (
                          <tr key={idx}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {metric.metric}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                              {metric.old_value}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                              {metric.new_value}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              ) : (
                <p className="text-center text-gray-500 py-8">
                  No metric changes
                </p>
              )}
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose || (() => {})}
      title={`Compare Versions ${versionA} and ${versionB}`}
      size="xl"
    >
      <div className="space-y-6">
        {loading && (
          <div
            className="flex justify-center items-center py-12"
            role="status"
            aria-live="polite"
          >
            <Spinner size="lg" />
            <span className="sr-only">Loading version comparison</span>
          </div>
        )}

        {error && (
          <Alert variant="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {!loading && !error && diff && renderDiffContent()}

        <div className="flex gap-3 justify-end pt-4 border-t">
          {diff && onRestore && (
            <>
              <Button variant="secondary" onClick={() => onRestore(versionA)}>
                Restore v{versionA}
              </Button>
              <Button variant="primary" onClick={() => onRestore(versionB)}>
                Restore v{versionB}
              </Button>
            </>
          )}
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export { VersionComparison };
