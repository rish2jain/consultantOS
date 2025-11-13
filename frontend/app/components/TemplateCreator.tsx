"use client";

import React, { useState, useEffect } from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { Input } from './Input';
import { Dropdown, DropdownItem } from './Dropdown';
import { Save, X, Eye } from 'lucide-react';
import { Tabs, TabList, Tab, TabPanels, TabPanel } from './Tabs';
import { Alert } from './Alert';
import type { Template } from '@/types/templates';

export interface TemplateFormData {
  name: string;
  description: string;
  category: Template['category'];
  framework_type: Template['framework_type'];
  visibility: Template['visibility'];
  industry: string;
  region: string;
  prompt_template: string;
}

export interface TemplateCreatorProps {
  /** Whether modal is open */
  isOpen: boolean;
  /** Close handler */
  onClose: () => void;
  /** Save handler */
  onSave: (data: TemplateFormData) => void | Promise<void>;
  /** Initial data for editing */
  initialData?: Partial<TemplateFormData>;
  /** Whether saving */
  isSaving?: boolean;
  /** Mode: create or edit */
  mode?: 'create' | 'edit';
}

const categoryOptions: DropdownItem[] = [
  { value: 'strategic', label: 'Strategic' },
  { value: 'financial', label: 'Financial' },
  { value: 'operational', label: 'Operational' },
  { value: 'market', label: 'Market' },
  { value: 'risk', label: 'Risk' },
];

const frameworkOptions: DropdownItem[] = [
  { value: 'porter', label: "Porter's 5 Forces" },
  { value: 'swot', label: 'SWOT Analysis' },
  { value: 'pestel', label: 'PESTEL Analysis' },
  { value: 'blue_ocean', label: 'Blue Ocean Strategy' },
];

const visibilityOptions: DropdownItem[] = [
  { value: 'public', label: 'Public' },
  { value: 'private', label: 'Private' },
  { value: 'shared', label: 'Shared' },
];

const defaultPromptTemplate = `Analyze {{company}} in the {{industry}} industry using {{framework}} framework.

Focus on:
- Key strategic considerations
- Competitive dynamics
- Market opportunities and threats
- Actionable recommendations

Provide detailed analysis with supporting evidence.`;

export const TemplateCreator: React.FC<TemplateCreatorProps> = ({
  isOpen,
  onClose,
  onSave,
  initialData,
  isSaving = false,
  mode = 'create',
}) => {
  const [formData, setFormData] = useState<TemplateFormData>({
    name: initialData?.name || '',
    description: initialData?.description || '',
    category: initialData?.category || 'strategic',
    framework_type: initialData?.framework_type || 'porter',
    visibility: initialData?.visibility || 'private',
    industry: initialData?.industry || '',
    region: initialData?.region || '',
    prompt_template: initialData?.prompt_template || defaultPromptTemplate,
  });

  const [errors, setErrors] = useState<Partial<Record<keyof TemplateFormData, string>>>({});
  const [saveError, setSaveError] = useState<string | null>(null);

  // Sync form state with initialData prop changes
  useEffect(() => {
    setFormData({
      name: initialData?.name || '',
      description: initialData?.description || '',
      category: initialData?.category || 'strategic',
      framework_type: initialData?.framework_type || 'porter',
      visibility: initialData?.visibility || 'private',
      industry: initialData?.industry || '',
      region: initialData?.region || '',
      prompt_template: initialData?.prompt_template || defaultPromptTemplate,
    });
  }, [initialData]);

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof TemplateFormData, string>> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Template name is required';
    } else if (formData.name.length < 3) {
      newErrors.name = 'Template name must be at least 3 characters';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters';
    }

    if (!formData.prompt_template.trim()) {
      newErrors.prompt_template = 'Prompt template is required';
    } else if (formData.prompt_template.length < 20) {
      newErrors.prompt_template = 'Prompt template must be at least 20 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setSaveError(null);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Error saving template:', error);
      let errorMessage = 'Failed to save template. Please try again.';
      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === 'object' && error !== null && 'detail' in error) {
        errorMessage = String((error as { detail: unknown }).detail) || errorMessage;
      }
      setSaveError(errorMessage);
    }
  };

  const handleClose = () => {
    setFormData({
      name: '',
      description: '',
      category: 'strategic',
      framework_type: 'porter',
      visibility: 'private',
      industry: '',
      region: '',
      prompt_template: defaultPromptTemplate,
    });
    setErrors({});
    setSaveError(null);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={mode === 'create' ? 'Create New Template' : 'Edit Template'}
      description="Configure your analysis template with custom settings"
      size="xl"
      footer={
        <>
          <Button variant="outline" onClick={handleClose} disabled={isSaving}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            isLoading={isSaving}
            leftIcon={<Save className="w-4 h-4" />}
          >
            {mode === 'create' ? 'Create Template' : 'Save Changes'}
          </Button>
        </>
      }
    >
      <div className="space-y-6">
        {saveError && (
          <Alert
            variant="error"
            title="Save Failed"
            description={saveError}
            dismissible
            onClose={() => setSaveError(null)}
          />
        )}
        {/* Basic Information */}
        <div className="space-y-4">
          <Input
            label="Template Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            error={errors.name}
            placeholder="e.g., Tech Startup Strategic Analysis"
            required
            fullWidth
            maxLength={100}
            showCounter
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe what this template is used for and when to use it..."
              rows={3}
              maxLength={500}
              className={`
                w-full px-4 py-2 text-base rounded-md border transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-offset-1 resize-none
                ${errors.description
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                  : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500'
                }
              `}
            />
            <div className="flex justify-between mt-1">
              {errors.description ? (
                <p className="text-sm text-red-600">{errors.description}</p>
              ) : (
                <p className="text-sm text-gray-500">Provide a clear description of the template&apos;s purpose</p>
              )}
              <span className="text-xs text-gray-400">{formData.description.length}/500</span>
            </div>
          </div>
        </div>

        {/* Configuration */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category <span className="text-red-500">*</span>
            </label>
            <Dropdown
              value={formData.category}
              onChange={(value) => setFormData({ ...formData, category: value as Template['category'] })}
              items={categoryOptions}
              width="full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Framework Type <span className="text-red-500">*</span>
            </label>
            <Dropdown
              value={formData.framework_type}
              onChange={(value) => setFormData({ ...formData, framework_type: value as Template['framework_type'] })}
              items={frameworkOptions}
              width="full"
            />
          </div>
        </div>

        {/* Visibility */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Visibility <span className="text-red-500">*</span>
          </label>
          <div className="space-y-2">
            {visibilityOptions.map((option) => (
              <label
                key={option.value}
                className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <input
                  type="radio"
                  name="visibility"
                  value={option.value}
                  checked={formData.visibility === option.value}
                  onChange={(e) => setFormData({ ...formData, visibility: e.target.value as Template['visibility'] })}
                  className="mt-1 w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500 focus:ring-2 cursor-pointer"
                />
                <div>
                  <span className="font-medium text-gray-900">{option.label}</span>
                  <p className="text-sm text-gray-500 mt-0.5">
                    {option.value === 'public' && 'Anyone can view and use this template'}
                    {option.value === 'private' && 'Only you can view and use this template'}
                    {option.value === 'shared' && 'Specific users can view and use this template'}
                  </p>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Optional Fields */}
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Industry (Optional)"
            value={formData.industry}
            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            placeholder="e.g., Technology, Healthcare"
            fullWidth
          />

          <Input
            label="Region (Optional)"
            value={formData.region}
            onChange={(e) => setFormData({ ...formData, region: e.target.value })}
            placeholder="e.g., North America, APAC"
            fullWidth
          />
        </div>

        {/* Prompt Template */}
        <div>
          <Tabs defaultValue="edit">
            <TabList>
              <Tab value="edit">Edit Template</Tab>
              <Tab value="preview">Preview</Tab>
            </TabList>

            <TabPanels className="mt-4">
              <TabPanel value="edit">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="block text-sm font-medium text-gray-700">
                      Prompt Template <span className="text-red-500">*</span>
                    </label>
                    <p className="text-xs text-gray-500">
                      Use {'{{variable}}'} for dynamic values
                    </p>
                  </div>
                  <textarea
                    value={formData.prompt_template}
                    onChange={(e) => setFormData({ ...formData, prompt_template: e.target.value })}
                    rows={10}
                    className={`
                      w-full px-4 py-3 text-sm font-mono rounded-md border transition-all duration-200
                      focus:outline-none focus:ring-2 focus:ring-offset-1 resize-y bg-gray-900 text-gray-100
                      ${errors.prompt_template
                        ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                        : 'border-gray-700 focus:border-primary-500 focus:ring-primary-500'
                      }
                    `}
                  />
                  {errors.prompt_template && (
                    <p className="text-sm text-red-600">{errors.prompt_template}</p>
                  )}
                  <p className="text-xs text-gray-500">
                    Available variables: {'{{company}}'}, {'{{industry}}'}, {'{{region}}'}, {'{{framework}}'}
                  </p>
                </div>
              </TabPanel>

              <TabPanel value="preview">
                <div className="bg-gray-900 text-gray-100 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-medium">Preview</h4>
                    <Eye className="w-4 h-4 text-gray-400" aria-hidden="true" />
                  </div>
                  <pre className="text-sm whitespace-pre-wrap font-mono">
                    {formData.prompt_template || 'No template content yet...'}
                  </pre>
                </div>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </div>
      </div>
    </Modal>
  );
};
export default TemplateCreator;
