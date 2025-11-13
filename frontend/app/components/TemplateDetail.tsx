"use client";

import React from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { Badge } from './Badge';
import { Tabs, TabList, Tab, TabPanels, TabPanel } from './Tabs';
import { FileText, Copy, Calendar, User, Eye, GitFork } from 'lucide-react';
import type { Template } from '@/types/templates';

export interface TemplateDetailProps {
  /** Template to display */
  template: Template | null;
  /** Whether modal is open */
  isOpen: boolean;
  /** Close handler */
  onClose: () => void;
  /** Use template handler */
  onUse?: (template: Template) => void;
  /** Fork template handler */
  onFork?: (template: Template) => void;
}

const categoryColors: Record<string, string> = {
  strategic: 'primary',
  financial: 'success',
  operational: 'info',
  market: 'warning',
  risk: 'danger',
  porter: 'primary',
  swot: 'warning',
  pestel: 'info',
  blue_ocean: 'success',
};

const frameworkLabels: Record<string, string> = {
  porter: "Porter's 5 Forces",
  swot: 'SWOT Analysis',
  pestel: 'PESTEL Analysis',
  blue_ocean: 'Blue Ocean Strategy',
};

export const TemplateDetail: React.FC<TemplateDetailProps> = ({
  template,
  isOpen,
  onClose,
  onUse,
  onFork,
}) => {
  if (!template) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={template.name}
      size="xl"
      footer={
        <>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          {onFork && (
            <Button
              variant="outline"
              leftIcon={<Copy className="w-4 h-4" />}
              onClick={() => {
                onFork(template);
                onClose();
              }}
            >
              Fork Template
            </Button>
          )}
          {onUse && (
            <Button
              variant="primary"
              leftIcon={<FileText className="w-4 h-4" />}
              onClick={() => {
                onUse(template);
                onClose();
              }}
            >
              Use Template
            </Button>
          )}
        </>
      }
    >
      <div className="space-y-6">
        {/* Badges and Meta Info */}
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant={(categoryColors[template.category] as any) || 'default'} size="md">
            {template.category}
          </Badge>
          <Badge variant="default" size="md">
            {frameworkLabels[template.framework_type] || template.framework_type}
          </Badge>
          <Badge
            variant={template.visibility === 'public' ? 'success' : 'default'}
            size="md"
          >
            {template.visibility}
          </Badge>
        </div>

        {/* Description */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Description</h3>
          <p className="text-gray-600">{template.description}</p>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-start gap-3">
            <User className="w-5 h-5 text-gray-400 mt-0.5" aria-hidden="true" />
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase">Created By</p>
              <p className="text-sm text-gray-900 mt-1">{template.created_by}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Calendar className="w-5 h-5 text-gray-400 mt-0.5" aria-hidden="true" />
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase">Created On</p>
              <p className="text-sm text-gray-900 mt-1">{formatDate(template.created_at)}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <GitFork className="w-5 h-5 text-gray-400 mt-0.5" aria-hidden="true" />
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase">Fork Count</p>
              <p className="text-sm text-gray-900 mt-1">{template.fork_count ?? 0}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Eye className="w-5 h-5 text-gray-400 mt-0.5" aria-hidden="true" />
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase">Visibility</p>
              <p className="text-sm text-gray-900 mt-1 capitalize">{template.visibility}</p>
            </div>
          </div>

          {template.industry && (
            <div className="flex items-start gap-3">
              <FileText className="w-5 h-5 text-gray-400 mt-0.5" aria-hidden="true" />
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase">Industry</p>
                <p className="text-sm text-gray-900 mt-1">{template.industry}</p>
              </div>
            </div>
          )}

          {template.region && (
            <div className="flex items-start gap-3">
              <FileText className="w-5 h-5 text-gray-400 mt-0.5" aria-hidden="true" />
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase">Region</p>
                <p className="text-sm text-gray-900 mt-1">{template.region}</p>
              </div>
            </div>
          )}
        </div>

        {/* Tabbed Content */}
        <Tabs defaultValue="prompt">
          <TabList>
            <Tab value="prompt">Prompt Template</Tab>
            <Tab value="usage">Usage Instructions</Tab>
          </TabList>

          <TabPanels className="mt-4">
            <TabPanel value="prompt">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-700">Prompt Template</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={async () => {
                      try {
                        await navigator.clipboard.writeText(template.prompt_template);
                        // You can add a toast notification here if available
                        // For now, we'll just handle errors gracefully
                      } catch (error) {
                        console.error('Failed to copy to clipboard:', error);
                        // You can add error notification here if available
                        alert('Failed to copy to clipboard. Please try again.');
                      }
                    }}
                    leftIcon={<Copy className="w-4 h-4" />}
                  >
                    Copy
                  </Button>
                </div>
                <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                  <pre className="text-sm whitespace-pre-wrap font-mono">
                    {template.prompt_template}
                  </pre>
                </div>
              </div>
            </TabPanel>

            <TabPanel value="usage">
              <div className="prose prose-sm max-w-none">
                <h4>How to Use This Template</h4>
                <ol>
                  <li>
                    Click the &quot;Use Template&quot; button to navigate to the analysis form
                  </li>
                  <li>
                    The form will be pre-filled with this template&apos;s configuration:
                    <ul>
                      <li>Framework type: {frameworkLabels[template.framework_type] || template.framework_type}</li>
                      <li>Category: {template.category}</li>
                      {template.industry && <li>Industry: {template.industry}</li>}
                      {template.region && <li>Region: {template.region}</li>}
                    </ul>
                  </li>
                  <li>
                    Customize the prompt template or other fields as needed
                  </li>
                  <li>
                    Submit the form to generate your analysis
                  </li>
                </ol>

                <h4>Forking This Template</h4>
                <p>
                  If you want to create your own version of this template, click the &quot;Fork Template&quot;
                  button. This will create a private copy that you can customize and save.
                </p>

                <h4>Template Variables</h4>
                <p>
                  The prompt template may include variables that will be replaced with actual values:
                </p>
                <ul>
                  <li><code>{'{{company}}'}</code> - Company name</li>
                  <li><code>{'{{industry}}'}</code> - Industry sector</li>
                  <li><code>{'{{region}}'}</code> - Geographic region</li>
                  <li><code>{'{{framework}}'}</code> - Analysis framework</li>
                </ul>
              </div>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>
    </Modal>
  );
};
export default TemplateDetail;
