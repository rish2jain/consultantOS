"use client";

import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "./Card";
import { Button } from "./Button";
import { Badge } from "./Badge";
import { Alert } from "./Alert";
import { Send, Info } from "lucide-react";

export interface AsyncAnalysisFormData {
  company: string;
  industry: string;
  frameworks: string[];
  depth?: "quick" | "standard" | "deep";
  custom_requirements?: string;
}

export interface AsyncAnalysisFormProps {
  /** API base URL */
  apiUrl?: string;
  /** Callback when job is submitted successfully */
  onJobSubmitted?: (jobId: string) => void;
  /** Callback when submission fails */
  onError?: (error: string) => void;
  /** Initial form values */
  initialValues?: Partial<AsyncAnalysisFormData>;
  /** Custom className */
  className?: string;
}

const AVAILABLE_FRAMEWORKS = [
  {
    id: "porter",
    name: "Porter's 5 Forces",
    description: "Industry competitive analysis",
  },
  {
    id: "swot",
    name: "SWOT Analysis",
    description: "Strengths, Weaknesses, Opportunities, Threats",
  },
  {
    id: "pestel",
    name: "PESTEL Analysis",
    description: "Macro-environmental factors",
  },
  {
    id: "blue_ocean",
    name: "Blue Ocean Strategy",
    description: "Uncontested market space",
  },
  { id: "bcg", name: "BCG Matrix", description: "Portfolio analysis" },
  { id: "ansoff", name: "Ansoff Matrix", description: "Growth strategies" },
];

type DepthValue = "quick" | "standard" | "deep";

const DEPTH_OPTIONS: Array<{
  value: DepthValue;
  label: string;
  description: string;
}> = [
  {
    value: "quick",
    label: "Quick",
    description: "Fast analysis with core insights (~5 min)",
  },
  {
    value: "standard",
    label: "Standard",
    description: "Balanced depth and speed (~15 min)",
  },
  {
    value: "deep",
    label: "Deep",
    description: "Comprehensive analysis (~30 min)",
  },
];

export const AsyncAnalysisForm: React.FC<AsyncAnalysisFormProps> = ({
  apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  onJobSubmitted,
  onError,
  initialValues = {},
  className = "",
}) => {
  const [formData, setFormData] = useState<AsyncAnalysisFormData>({
    company: initialValues.company || "",
    industry: initialValues.industry || "",
    frameworks: initialValues.frameworks || [],
    depth: initialValues.depth || "standard",
    custom_requirements: initialValues.custom_requirements || "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.company.trim()) {
      errors.company = "Company name is required";
    }

    if (!formData.industry.trim()) {
      errors.industry = "Industry is required";
    }

    if (formData.frameworks.length === 0) {
      errors.frameworks = "Select at least one framework";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setValidationErrors({});

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch(`${apiUrl}/analyze/async`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail || `Failed to submit job: ${response.statusText}`
        );
      }

      const result = await response.json();
      const jobId = result.job_id;

      // Reset form
      setFormData({
        company: "",
        industry: "",
        frameworks: [],
        depth: "standard",
        custom_requirements: "",
      });

      onJobSubmitted?.(jobId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleFramework = (frameworkId: string) => {
    setFormData((prev) => ({
      ...prev,
      frameworks: prev.frameworks.includes(frameworkId)
        ? prev.frameworks.filter((id) => id !== frameworkId)
        : [...prev.frameworks, frameworkId],
    }));
    // Clear validation error when user makes selection
    if (validationErrors.frameworks) {
      setValidationErrors((prev) => {
        const { frameworks, ...rest } = prev;
        return rest;
      });
    }
  };

  return (
    <Card className={className}>
      <form onSubmit={handleSubmit}>
        <CardHeader>
          <CardTitle>Submit Async Analysis</CardTitle>
          <CardDescription>
            Submit a business analysis job and track its progress in real-time
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {error && (
            <Alert
              variant="error"
              title="Submission failed"
              description={error}
              dismissible
              onClose={() => setError(null)}
            />
          )}

          <Alert
            variant="info"
            showIcon
            description="Async jobs are processed in the background. You can track progress and download results when complete."
          />

          {/* Company Name */}
          <div>
            <label
              htmlFor="company"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Company Name <span className="text-red-500">*</span>
            </label>
            <input
              id="company"
              type="text"
              value={formData.company}
              onChange={(e) => {
                setFormData((prev) => ({ ...prev, company: e.target.value }));
                if (validationErrors.company) {
                  setValidationErrors((prev) => {
                    const { company, ...rest } = prev;
                    return rest;
                  });
                }
              }}
              placeholder="e.g., Tesla, Apple, Microsoft"
              className={`
                w-full px-3 py-2 border rounded-md shadow-sm
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                ${
                  validationErrors.company
                    ? "border-red-500"
                    : "border-gray-300"
                }
              `}
              aria-invalid={!!validationErrors.company}
              aria-describedby={
                validationErrors.company ? "company-error" : undefined
              }
            />
            {validationErrors.company && (
              <p id="company-error" className="text-sm text-red-600 mt-1">
                {validationErrors.company}
              </p>
            )}
          </div>

          {/* Industry */}
          <div>
            <label
              htmlFor="industry"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Industry <span className="text-red-500">*</span>
            </label>
            <input
              id="industry"
              type="text"
              value={formData.industry}
              onChange={(e) => {
                setFormData((prev) => ({ ...prev, industry: e.target.value }));
                if (validationErrors.industry) {
                  setValidationErrors((prev) => {
                    const { industry, ...rest } = prev;
                    return rest;
                  });
                }
              }}
              placeholder="e.g., Electric Vehicles, Technology, Retail"
              className={`
                w-full px-3 py-2 border rounded-md shadow-sm
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                ${
                  validationErrors.industry
                    ? "border-red-500"
                    : "border-gray-300"
                }
              `}
              aria-invalid={!!validationErrors.industry}
              aria-describedby={
                validationErrors.industry ? "industry-error" : undefined
              }
            />
            {validationErrors.industry && (
              <p id="industry-error" className="text-sm text-red-600 mt-1">
                {validationErrors.industry}
              </p>
            )}
          </div>

          {/* Frameworks */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Business Frameworks <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {AVAILABLE_FRAMEWORKS.map((framework) => (
                <button
                  key={framework.id}
                  type="button"
                  onClick={() => toggleFramework(framework.id)}
                  className={`
                    p-3 border-2 rounded-lg text-left transition-all
                    ${
                      formData.frameworks.includes(framework.id)
                        ? "border-primary-500 bg-primary-50"
                        : "border-gray-200 hover:border-gray-300 bg-white"
                    }
                  `}
                  aria-pressed={formData.frameworks.includes(framework.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {framework.name}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {framework.description}
                      </p>
                    </div>
                    {formData.frameworks.includes(framework.id) && (
                      <Badge variant="primary" size="sm">
                        Selected
                      </Badge>
                    )}
                  </div>
                </button>
              ))}
            </div>
            {validationErrors.frameworks && (
              <p className="text-sm text-red-600 mt-1">
                {validationErrors.frameworks}
              </p>
            )}
          </div>

          {/* Analysis Depth */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis Depth
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {DEPTH_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() =>
                    setFormData((prev: AsyncAnalysisFormData) => ({
                      ...prev,
                      depth: option.value,
                    }))
                  }
                  className={`
                    p-3 border-2 rounded-lg text-left transition-all
                    ${
                      formData.depth === option.value
                        ? "border-primary-500 bg-primary-50"
                        : "border-gray-200 hover:border-gray-300 bg-white"
                    }
                  `}
                  aria-pressed={formData.depth === option.value}
                >
                  <p className="text-sm font-medium text-gray-900">
                    {option.label}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {option.description}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Custom Requirements */}
          <div>
            <label
              htmlFor="custom_requirements"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Custom Requirements{" "}
              <span className="text-gray-500">(Optional)</span>
            </label>
            <textarea
              id="custom_requirements"
              value={formData.custom_requirements}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  custom_requirements: e.target.value,
                }))
              }
              placeholder="Any specific requirements or areas of focus..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </CardContent>

        <CardFooter className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            <Info className="w-4 h-4 inline mr-1" aria-hidden="true" />
            Estimated time:{" "}
            {formData.depth === "quick"
              ? "5 min"
              : formData.depth === "deep"
              ? "30 min"
              : "15 min"}
          </div>
          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isSubmitting}
            leftIcon={<Send className="w-5 h-5" />}
          >
            Submit Analysis
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};
