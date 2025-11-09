"use client";

import React, { useState, useEffect } from 'react';
import { TemplateCard, Template } from './TemplateCard';
import { TemplateFilters, TemplateFiltersState } from './TemplateFilters';
import { TemplateDetail } from './TemplateDetail';
import { TemplateCreator, TemplateFormData } from './TemplateCreator';
import { Button } from './Button';
import { Input } from './Input';
import { InlineLoading } from './Spinner';
import { Grid, List, Plus, Search, Filter, X } from 'lucide-react';

export interface TemplateLibraryProps {
  /** API endpoint for templates */
  apiEndpoint?: string;
  /** Use template handler */
  onUseTemplate?: (template: Template) => void;
  /** Custom empty state message */
  emptyMessage?: string;
  /** Initial view mode */
  initialViewMode?: 'grid' | 'list';
}

export const TemplateLibrary: React.FC<TemplateLibraryProps> = ({
  apiEndpoint = '/api/templates',
  onUseTemplate,
  emptyMessage = 'No templates found. Create your first template to get started.',
  initialViewMode = 'grid',
}) => {
  // State
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(initialViewMode);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showCreatorModal, setShowCreatorModal] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const itemsPerPage = 12;

  // Filters state
  const [filters, setFilters] = useState<TemplateFiltersState>({
    categories: [],
    frameworks: [],
    visibility: null,
    industry: '',
    region: '',
  });

  // Fetch templates
  useEffect(() => {
    const fetchTemplates = async () => {
      setIsLoading(true);
      try {
        // Build query params
        const params = new URLSearchParams();

        if (filters.categories.length > 0) {
          params.append('category', filters.categories.join(','));
        }
        if (filters.frameworks.length > 0) {
          params.append('framework_type', filters.frameworks.join(','));
        }
        if (filters.visibility) {
          params.append('visibility', filters.visibility);
        }
        if (filters.industry) {
          params.append('industry', filters.industry);
        }
        if (filters.region) {
          params.append('region', filters.region);
        }

        const response = await fetch(`${apiEndpoint}?${params.toString()}`);

        if (!response.ok) {
          throw new Error('Failed to fetch templates');
        }

        const data = await response.json();
        setTemplates(data.templates || []);
      } catch (error) {
        console.error('Error fetching templates:', error);
        setTemplates([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTemplates();
  }, [apiEndpoint, filters]);

  // Filter templates by search query
  useEffect(() => {
    let filtered = templates;

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = templates.filter(
        (template) =>
          template.name.toLowerCase().includes(query) ||
          template.description.toLowerCase().includes(query) ||
          template.category.toLowerCase().includes(query) ||
          template.industry?.toLowerCase().includes(query) ||
          template.region?.toLowerCase().includes(query)
      );
    }

    setFilteredTemplates(filtered);
    setCurrentPage(1); // Reset to first page on search
  }, [templates, searchQuery]);

  // Pagination
  const totalPages = Math.ceil(filteredTemplates.length / itemsPerPage);
  const paginatedTemplates = filteredTemplates.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Handlers
  const handleViewTemplate = (template: Template) => {
    setSelectedTemplate(template);
    setShowDetailModal(true);
  };

  const handleUseTemplate = (template: Template) => {
    onUseTemplate?.(template);
  };

  const handleForkTemplate = async (template: Template) => {
    try {
      const response = await fetch(`${apiEndpoint}/${template.id}/fork`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fork template');
      }

      const forkedTemplate = await response.json();

      // Add forked template to list
      setTemplates([forkedTemplate, ...templates]);

      // Show success message or notification
      alert('Template forked successfully!');
    } catch (error) {
      console.error('Error forking template:', error);
      alert('Failed to fork template. Please try again.');
    }
  };

  const handleCreateTemplate = async (data: TemplateFormData) => {
    setIsSaving(true);
    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to create template');
      }

      const newTemplate = await response.json();

      // Add new template to list
      setTemplates([newTemplate, ...templates]);

      setShowCreatorModal(false);
    } catch (error) {
      console.error('Error creating template:', error);
      alert('Failed to create template. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  // Empty state
  const isEmpty = !isLoading && filteredTemplates.length === 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Template Library</h1>
          <p className="text-sm text-gray-500 mt-1">
            Reusable analysis configurations for faster insights
          </p>
        </div>
        <Button
          variant="primary"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => setShowCreatorModal(true)}
        >
          Create Template
        </Button>
      </div>

      {/* Search and Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={<Search className="w-5 h-5" />}
            fullWidth
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Toggle Filters (Mobile) */}
          <Button
            variant="outline"
            size="md"
            onClick={() => setShowFilters(!showFilters)}
            leftIcon={showFilters ? <X className="w-4 h-4" /> : <Filter className="w-4 h-4" />}
            className="sm:hidden"
          >
            {showFilters ? 'Hide' : 'Show'} Filters
          </Button>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 border border-gray-300 rounded-md p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`
                p-2 rounded transition-colors
                ${viewMode === 'grid'
                  ? 'bg-primary-100 text-primary-600'
                  : 'text-gray-600 hover:bg-gray-100'
                }
              `}
              aria-label="Grid view"
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`
                p-2 rounded transition-colors
                ${viewMode === 'list'
                  ? 'bg-primary-100 text-primary-600'
                  : 'text-gray-600 hover:bg-gray-100'
                }
              `}
              aria-label="List view"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Filters Sidebar */}
        <aside className={`lg:w-64 ${!showFilters ? 'hidden lg:block' : ''}`}>
          <TemplateFilters
            filters={filters}
            onChange={setFilters}
            show={showFilters}
          />
        </aside>

        {/* Templates Grid/List */}
        <main className="flex-1">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <InlineLoading message="Loading templates..." size="lg" centered />
            </div>
          ) : isEmpty ? (
            <div className="text-center py-12 px-4">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                <Search className="w-8 h-8 text-gray-400" aria-hidden="true" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Templates Found</h3>
              <p className="text-gray-500 mb-6 max-w-md mx-auto">{emptyMessage}</p>
              <Button
                variant="primary"
                leftIcon={<Plus className="w-4 h-4" />}
                onClick={() => setShowCreatorModal(true)}
              >
                Create Your First Template
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Results Count */}
              <div className="text-sm text-gray-600">
                Showing {paginatedTemplates.length} of {filteredTemplates.length} templates
              </div>

              {/* Templates */}
              <div
                className={
                  viewMode === 'grid'
                    ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
                    : 'space-y-4'
                }
              >
                {paginatedTemplates.map((template) => (
                  <TemplateCard
                    key={template.id}
                    template={template}
                    onView={handleViewTemplate}
                    onUse={handleUseTemplate}
                    onFork={handleForkTemplate}
                    clickable
                  />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 pt-6">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>

                  <div className="flex items-center gap-1">
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`
                          px-3 py-1 text-sm rounded transition-colors
                          ${page === currentPage
                            ? 'bg-primary-600 text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                          }
                        `}
                      >
                        {page}
                      </button>
                    ))}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      {/* Template Detail Modal */}
      <TemplateDetail
        template={selectedTemplate}
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedTemplate(null);
        }}
        onUse={handleUseTemplate}
        onFork={handleForkTemplate}
      />

      {/* Template Creator Modal */}
      <TemplateCreator
        isOpen={showCreatorModal}
        onClose={() => setShowCreatorModal(false)}
        onSave={handleCreateTemplate}
        isSaving={isSaving}
        mode="create"
      />
    </div>
  );
};
