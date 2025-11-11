"use client";

import React, { useState, useEffect } from 'react';
import { Building2, MapPin, FileText, Send } from 'lucide-react';
import axios from 'axios';
import {
  Input,
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Alert,
} from '@/app/components';
import { FrameworkSelector } from './FrameworkSelector';
import { IndustrySelector } from './IndustrySelector';
import { DepthSelector } from './DepthSelector';

// Submission timer component
const SubmissionTimer: React.FC<{ startTime: number; estimatedTime: number }> = ({ 
  startTime, 
  estimatedTime 
}) => {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Date.now() - startTime);
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime]);

  const remaining = Math.max(0, estimatedTime - elapsed);
  const minutesRemaining = Math.ceil(remaining / 60000);

  return (
    <div className="text-xs text-gray-500">
      <span className="inline-flex items-center gap-1">
        <span className="inline-block w-2 h-2 bg-primary-500 rounded-full animate-pulse"></span>
        Processing... {minutesRemaining > 0 ? `Estimated time: ${minutesRemaining} min remaining` : 'Finalizing...'}
      </span>
    </div>
  );
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export interface AnalysisRequestData {
  company: string;
  industry: string;
  frameworks: ('porter' | 'swot' | 'pestel' | 'blue_ocean')[];
  depth?: 'quick' | 'standard' | 'deep';
  additional_context?: string;
  region?: string;
}

export interface AnalysisRequestFormProps {
  /** Optional API key for authenticated requests */
  apiKey?: string;
  /** Success callback with report data */
  onSuccess?: (reportData: any) => void;
  /** Error callback */
  onError?: (error: Error) => void;
  /** Async mode - returns job_id instead of waiting for completion */
  async?: boolean;
}

interface FormErrors {
  company?: string;
  industry?: string;
  frameworks?: string;
  depth?: string;
  region?: string;
  additional_context?: string;
  submit?: string;
}

export const AnalysisRequestForm: React.FC<AnalysisRequestFormProps> = ({
  apiKey,
  onSuccess,
  onError,
  async = false,
}) => {
  const [formData, setFormData] = useState<AnalysisRequestData>({
    company: '',
    industry: '',
    frameworks: [],
    depth: 'standard',
    additional_context: '',
    region: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submissionStartTime, setSubmissionStartTime] = useState<number | null>(null);
  const [estimatedTime, setEstimatedTime] = useState<number | null>(null);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Company validation
    if (!formData.company.trim()) {
      newErrors.company = 'Company name is required';
    } else if (formData.company.trim().length < 2) {
      newErrors.company = 'Company name must be at least 2 characters';
    } else if (formData.company.trim().length > 100) {
      newErrors.company = 'Company name must be less than 100 characters';
    }

    // Industry validation
    if (!formData.industry.trim()) {
      newErrors.industry = 'Industry is required';
    }

    // Frameworks validation
    if (formData.frameworks.length === 0) {
      newErrors.frameworks = 'Please select at least one business framework';
    } else if (formData.frameworks.length > 4) {
      newErrors.frameworks = 'Maximum 4 frameworks allowed';
    }

    // Additional context validation (optional but length-limited)
    if (formData.additional_context && formData.additional_context.length > 1000) {
      newErrors.additional_context = 'Additional context must be less than 1000 characters';
    }

    // Region validation (optional but length-limited)
    if (formData.region && formData.region.length > 100) {
      newErrors.region = 'Region must be less than 100 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitSuccess(false);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});
    
    // Calculate estimated time based on depth
    const depthTimeMap: Record<string, number> = {
      quick: 10 * 60 * 1000, // 10 minutes in ms
      standard: 20 * 60 * 1000, // 20 minutes in ms
      deep: 30 * 60 * 1000, // 30 minutes in ms
    };
    const estimatedMs = depthTimeMap[formData.depth || 'standard'] || 20 * 60 * 1000;
    setEstimatedTime(estimatedMs);
    setSubmissionStartTime(Date.now());

    try {
      const endpoint = async ? '/analyze/async' : '/analyze';
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (apiKey) {
        headers['X-API-Key'] = apiKey;
      }

      // Clean up payload - remove empty optional fields
      const payload: any = {
        company: formData.company.trim(),
        industry: formData.industry.trim(),
        frameworks: formData.frameworks,
        depth: formData.depth,
      };

      if (formData.additional_context?.trim()) {
        payload.additional_context = formData.additional_context.trim();
      }

      if (formData.region?.trim()) {
        payload.region = formData.region.trim();
      }

      const response = await axios.post(`${API_URL}${endpoint}`, payload, {
        headers,
        timeout: async ? 30000 : 300000, // 30s for async, 5min for sync
      });

      setSubmitSuccess(true);

      // Reset form after successful submission
      setFormData({
        company: '',
        industry: '',
        frameworks: [],
        depth: 'standard',
        additional_context: '',
        region: '',
      });

      if (onSuccess) {
        onSuccess(response.data);
      }
    } catch (error: any) {
      console.error('Analysis request failed:', error);

      let errorMessage = 'Failed to submit analysis request. Please try again.';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        // Handle FastAPI validation errors (array of error objects)
        if (Array.isArray(detail)) {
          errorMessage = detail
            .map((err: any) => {
              const field = err.loc?.slice(1).join('.') || 'field';
              return `${field}: ${err.msg}`;
            })
            .join('; ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      setErrors({ submit: errorMessage });

      if (onError) {
        onError(error);
      }
    } finally {
      setIsSubmitting(false);
      setSubmissionStartTime(null);
      setEstimatedTime(null);
    }
  };

  const handleFieldChange = (field: keyof AnalysisRequestData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Clear field-specific error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field as keyof FormErrors];
        return newErrors;
      });
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Request Business Analysis</CardTitle>
        <CardDescription>
          Generate a professional-grade strategic analysis using AI-powered business frameworks
        </CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {/* Success Alert */}
          {submitSuccess && (
            <Alert variant="success" dismissible onClose={() => setSubmitSuccess(false)}>
              <strong>Analysis request submitted successfully!</strong>
              {async
                ? ' You will receive a notification when the analysis is complete.'
                : ' Processing your request...'}
            </Alert>
          )}

          {/* Error Alert */}
          {errors.submit && (
            <Alert variant="error" dismissible onClose={() => setErrors({ ...errors, submit: undefined })}>
              <div className="space-y-1">
                <strong>Submission failed:</strong>
                <p className="text-sm">{errors.submit}</p>
                <p className="text-xs text-gray-600 mt-1">
                  Please check your inputs and try again. If the problem persists, contact support.
                </p>
              </div>
            </Alert>
          )}

          {/* Company Name */}
          <Input
            label="Company Name"
            placeholder="e.g., Tesla, Apple, Microsoft"
            value={formData.company}
            onChange={(e) => handleFieldChange('company', e.target.value)}
            error={errors.company}
            disabled={isSubmitting}
            required
            fullWidth
            leftIcon={<Building2 className="w-5 h-5" />}
            maxLength={100}
            showCounter
            helperText="Enter the name of the company you want to analyze"
          />

          {/* Industry Selector */}
          <IndustrySelector
            value={formData.industry}
            onChange={(value) => handleFieldChange('industry', value)}
            error={errors.industry}
            disabled={isSubmitting}
            required
          />

          {/* Framework Selector */}
          <FrameworkSelector
            value={formData.frameworks}
            onChange={(value) => handleFieldChange('frameworks', value)}
            error={errors.frameworks}
            disabled={isSubmitting}
            required
          />

          {/* Analysis Depth */}
          <DepthSelector
            value={formData.depth || 'standard'}
            onChange={(value) => handleFieldChange('depth', value)}
            error={errors.depth}
            disabled={isSubmitting}
          />

          {/* Region (Optional) */}
          <Input
            label="Region"
            placeholder="e.g., North America, EMEA, Asia-Pacific (optional)"
            value={formData.region || ''}
            onChange={(e) => handleFieldChange('region', e.target.value)}
            error={errors.region}
            disabled={isSubmitting}
            fullWidth
            leftIcon={<MapPin className="w-5 h-5" />}
            maxLength={100}
            helperText="Specify geographic focus for the analysis (optional)"
          />

          {/* Additional Context (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Additional Context
            </label>
            <div className="relative">
              <FileText className="absolute left-3 top-3 w-5 h-5 text-gray-400 pointer-events-none" aria-hidden="true" />
              <textarea
                value={formData.additional_context || ''}
                onChange={(e) => handleFieldChange('additional_context', e.target.value)}
                disabled={isSubmitting}
                maxLength={1000}
                rows={4}
                placeholder="Provide any additional context, specific questions, or focus areas for the analysis (optional)"
                className={`
                  w-full pl-10 pr-4 py-3 border rounded-md transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                  disabled:opacity-50 disabled:cursor-not-allowed
                  ${errors.additional_context ? 'border-red-300' : 'border-gray-300'}
                `}
                aria-describedby={errors.additional_context ? 'additional-context-error' : 'additional-context-helper'}
              />
            </div>
            {errors.additional_context ? (
              <p id="additional-context-error" className="mt-1 text-sm text-red-600" role="alert">
                {errors.additional_context}
              </p>
            ) : (
              <div className="mt-1 flex justify-between items-center">
                <p id="additional-context-helper" className="text-sm text-gray-500">
                  Provide specific areas of focus or questions
                </p>
                <span className="text-xs text-gray-400">
                  {(formData.additional_context || '').length}/1000
                </span>
              </div>
            )}
          </div>
        </CardContent>

        <CardFooter className="flex flex-col sm:flex-row gap-3 justify-between items-center">
          <p className="text-xs text-gray-500">
            All fields marked with <span className="text-red-500">*</span> are required
          </p>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setFormData({
                  company: '',
                  industry: '',
                  frameworks: [],
                  depth: 'standard',
                  additional_context: '',
                  region: '',
                });
                setErrors({});
                setSubmitSuccess(false);
              }}
              disabled={isSubmitting}
            >
              Reset
            </Button>

            <div className="flex flex-col items-end gap-2">
              {isSubmitting && estimatedTime && submissionStartTime && (
                <SubmissionTimer 
                  startTime={submissionStartTime} 
                  estimatedTime={estimatedTime} 
                />
              )}
              <Button
                type="submit"
                variant="primary"
                isLoading={isSubmitting}
                disabled={isSubmitting}
                leftIcon={!isSubmitting ? <Send className="w-4 h-4" /> : undefined}
              >
                {isSubmitting 
                  ? (async ? 'Submitting...' : 'Generating Analysis...') 
                  : (async ? 'Submit Request' : 'Generate Analysis')}
              </Button>
            </div>
          </div>
        </CardFooter>
      </form>
    </Card>
  );
};
