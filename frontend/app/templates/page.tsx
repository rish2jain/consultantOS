'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  TemplateLibrary,
  TemplateCreator,
  Modal,
  Button,
  Alert
} from '@/app/components';
import { api } from '@/lib/api';
import { Download } from 'lucide-react';

interface Template {
  id: string;
  name: string;
  description: string;
  industry: string;
  frameworks: string[];
  depth: string;
  custom_focus?: string[];
  created_by: string;
  created_at: string;
  updated_at: string;
  fork_count: number;
  usage_count: number;
  is_public: boolean;
  tags: string[];
}

export default function TemplatesPage() {
  const router = useRouter();

  // State
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  // Alert state
  const [alert, setAlert] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
  } | null>(null);

  // Load templates on mount
  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await api.templates.list();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
      setAlert({
        type: 'error',
        message: 'Failed to load templates. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async (templateData: any) => {
    try {
      const newTemplate = await api.templates.create(templateData);
      setTemplates([newTemplate, ...templates]);
      setShowCreateModal(false);
      setAlert({
        type: 'success',
        message: `Template "${newTemplate.name}" created successfully!`
      });
    } catch (error: any) {
      setAlert({
        type: 'error',
        message: error.message || 'Failed to create template. Please try again.'
      });
    }
  };

  const handleForkTemplate = async (template: Template) => {
    try {
      const forkedTemplate = await api.templates.fork(template.id);
      setTemplates([forkedTemplate, ...templates]);
      setAlert({
        type: 'success',
        message: `Template forked as "${forkedTemplate.name}"!`
      });
      setShowDetailsModal(false);
    } catch (error: any) {
      setAlert({
        type: 'error',
        message: error.message || 'Failed to fork template. Please try again.'
      });
    }
  };

  const handleUseTemplate = async (template: Template) => {
    try {
      // Navigate to analysis page with template data pre-filled
      const params = new URLSearchParams({
        template: template.id,
        company: '',
        industry: template.industry,
        frameworks: template.frameworks.join(','),
        depth: template.depth,
        ...(template.custom_focus && { custom_focus: template.custom_focus.join(',') })
      });

      router.push(`/analysis?${params.toString()}`);
    } catch (error: any) {
      setAlert({
        type: 'error',
        message: error.message || 'Failed to use template. Please try again.'
      });
    }
  };

  const handleViewDetails = async (template: Template) => {
    try {
      const fullTemplate = await api.templates.get(template.id);
      setSelectedTemplate(fullTemplate);
      setShowDetailsModal(true);
    } catch (error: any) {
      setAlert({
        type: 'error',
        message: error.message || 'Failed to load template details.'
      });
    }
  };

  const handleDeleteTemplate = async (template: Template) => {
    if (!confirm(`Are you sure you want to delete "${template.name}"?`)) {
      return;
    }

    try {
      await api.templates.delete(template.id);
      setTemplates(templates.filter(t => t.id !== template.id));
      setShowDetailsModal(false);
      setAlert({
        type: 'success',
        message: 'Template deleted successfully.'
      });
    } catch (error: any) {
      setAlert({
        type: 'error',
        message: error.message || 'Failed to delete template.'
      });
    }
  };

  const handleExportTemplates = (format: 'csv' | 'json') => {
    const exportData = templates.map(t => ({
      Name: t.name,
      Description: t.description,
      Industry: t.industry,
      Frameworks: t.frameworks.join(', '),
      Depth: t.depth,
      'Focus Areas': t.custom_focus?.join(', ') || 'N/A',
      Tags: t.tags?.join(', ') || 'N/A',
      'Is Public': t.is_public ? 'Yes' : 'No',
      'Fork Count': t.fork_count,
      'Usage Count': t.usage_count,
      'Created At': new Date(t.created_at).toLocaleDateString(),
      'Updated At': new Date(t.updated_at).toLocaleDateString(),
    }));

    if (format === 'csv') {
      const csvContent = [
        Object.keys(exportData[0] || {}).join(','),
        ...exportData.map(row =>
          Object.values(row).map(val => {
            const str = String(val ?? '');
            return str.includes(',') || str.includes('"') ? `"${str.replace(/"/g, '""')}"` : str;
          }).join(',')
        ),
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `templates-${Date.now()}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else {
      const jsonContent = JSON.stringify(exportData, null, 2);
      const blob = new Blob([jsonContent], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `templates-${Date.now()}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="min-h-screen bg-gray-50"
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white border-b border-gray-200"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-1">Template Library</h1>
              <p className="text-base text-gray-600">
                Browse and use pre-configured analysis templates to get started faster
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExportTemplates('csv')}
                leftIcon={<Download className="w-4 h-4" />}
                disabled={templates.length === 0}
              >
                Export CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExportTemplates('json')}
                leftIcon={<Download className="w-4 h-4" />}
                disabled={templates.length === 0}
              >
                Export JSON
              </Button>
              <Button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Create Template
              </Button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Alert */}
      {alert && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
          </div>
        ) : (
          <TemplateLibrary
            apiEndpoint={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/templates`}
            onUseTemplate={handleUseTemplate}
          />
        )}
      </div>

      {/* Create Template Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Template"
      >
        <TemplateCreator
          onSubmit={handleCreateTemplate}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>

      {/* Template Details Modal */}
      {selectedTemplate && (
        <Modal
          isOpen={showDetailsModal}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedTemplate(null);
          }}
          title={selectedTemplate.name}
          size="large"
        >
          <div className="space-y-6">
            {/* Description */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Description</h3>
              <p className="text-gray-600">{selectedTemplate.description}</p>
            </div>

            {/* Industry */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Industry</h3>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {selectedTemplate.industry}
              </span>
            </div>

            {/* Frameworks */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Frameworks</h3>
              <div className="flex flex-wrap gap-2">
                {selectedTemplate.frameworks.map((framework) => (
                  <span
                    key={framework}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800"
                  >
                    {framework}
                  </span>
                ))}
              </div>
            </div>

            {/* Analysis Depth */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Analysis Depth</h3>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                {selectedTemplate.depth}
              </span>
            </div>

            {/* Custom Focus Areas */}
            {selectedTemplate.custom_focus && selectedTemplate.custom_focus.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Focus Areas</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.custom_focus.map((focus, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800"
                    >
                      {focus}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Tags */}
            {selectedTemplate.tags && selectedTemplate.tags.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              <div>
                <p className="text-sm text-gray-500">Forks</p>
                <p className="text-2xl font-semibold text-gray-900">{selectedTemplate.fork_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Times Used</p>
                <p className="text-2xl font-semibold text-gray-900">{selectedTemplate.usage_count}</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-6 border-t border-gray-200">
              <Button
                onClick={() => handleUseTemplate(selectedTemplate)}
                className="flex-1"
              >
                Use Template
              </Button>
              <Button
                onClick={() => handleForkTemplate(selectedTemplate)}
                variant="secondary"
                className="flex-1"
              >
                Fork Template
              </Button>
              {/* Show delete button only for own templates - in production check user ownership */}
              <Button
                onClick={() => handleDeleteTemplate(selectedTemplate)}
                variant="danger"
                className="px-4"
              >
                Delete
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </motion.div>
  );
}
