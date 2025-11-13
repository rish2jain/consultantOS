"use client";

import React, { useState, useEffect } from "react";
import { Building2, MapPin, FileText, Send, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import axios from "axios";
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
  Spinner,
} from "@/app/components";
import { motion, AnimatePresence } from "framer-motion";
import { FrameworkSelector } from "./FrameworkSelector";
import { IndustrySelector } from "./IndustrySelector";
import { DepthSelector } from "./DepthSelector";
import { AnalysisProgress } from "./AnalysisProgress";

// Submission timer component with enhanced UI
const SubmissionTimer: React.FC<{
  startTime: number;
  estimatedTime: number;
}> = ({ startTime, estimatedTime }) => {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Date.now() - startTime);
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime]);

  const remaining = Math.max(0, estimatedTime - elapsed);
  const minutesRemaining = Math.ceil(remaining / 60000);
  const progress = Math.min(100, (elapsed / estimatedTime) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full"
    >
      <div className="flex items-center gap-2 mb-2">
        <Spinner size="sm" variant="circular" />
        <span className="text-xs text-gray-600 font-medium">
          {minutesRemaining > 0
            ? `Processing... ${minutesRemaining} min remaining`
            : "Finalizing analysis..."}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
        <motion.div
          className="bg-blue-600 h-full rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
    </motion.div>
  );
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const PRESET_TEMPLATES: Array<{
  id: string;
  label: string;
  description: string;
  frameworks: AnalysisRequestData["frameworks"];
  depth: NonNullable<AnalysisRequestData["depth"]>;
}> = [
  {
    id: "competitive_brief",
    label: "Competitive Brief",
    description: "Porter + SWOT at standard depth",
    frameworks: ["porter", "swot"],
    depth: "standard",
  },
  {
    id: "market_entry",
    label: "Market Entry",
    description: "SWOT + PESTEL deep dive",
    frameworks: ["swot", "pestel"],
    depth: "deep",
  },
  {
    id: "quick_scan",
    label: "Quick Scan",
    description: "Porter snapshot in minutes",
    frameworks: ["porter"],
    depth: "quick",
  },
];

export interface AnalysisRequestData {
  company: string;
  industry: string;
  frameworks: ("porter" | "swot" | "pestel" | "blue_ocean")[];
  depth?: "quick" | "standard" | "deep";
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
  const router = useRouter();
  const [formData, setFormData] = useState<AnalysisRequestData>({
    company: "",
    industry: "",
    frameworks: [],
    depth: "standard",
    additional_context: "",
    region: "",
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentReportId, setCurrentReportId] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submissionStartTime, setSubmissionStartTime] = useState<number | null>(
    null
  );
  const [estimatedTime, setEstimatedTime] = useState<number | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);
  const [lastJobId, setLastJobId] = useState<string | null>(null);

  // Validation function for parsed localStorage data
  const validateParsedFormData = (data: any): data is AnalysisRequestData => {
    if (!data || typeof data !== "object") {
      return false;
    }

    // Check required fields exist and have correct types
    if (typeof data.company !== "string") {
      return false;
    }

    if (typeof data.industry !== "string") {
      return false;
    }

    if (!Array.isArray(data.frameworks)) {
      return false;
    }

    // Validate frameworks array contains only valid values
    const validFrameworks = ["porter", "swot", "pestel", "blue_ocean"];
    if (!data.frameworks.every((f: any) => validFrameworks.includes(f))) {
      return false;
    }

    // Validate optional fields if present
    if (
      data.depth !== undefined &&
      !["quick", "standard", "deep"].includes(data.depth)
    ) {
      return false;
    }

    if (
      data.additional_context !== undefined &&
      typeof data.additional_context !== "string"
    ) {
      return false;
    }

    if (data.region !== undefined && typeof data.region !== "string") {
      return false;
    }

    return true;
  };

  // Load form data from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("analysis_form_draft");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);

        // Validate parsed object against expected form schema
        const isValid = validateParsedFormData(parsed);

        if (isValid) {
          setFormData(parsed);
        } else {
          // Invalid data - clear it and log warning
          console.warn("Invalid form draft data in localStorage, clearing it");
          localStorage.removeItem("analysis_form_draft");
        }
      } catch (error) {
        console.error("Failed to load form draft:", error);
        // Clear corrupted data
        localStorage.removeItem("analysis_form_draft");
      }
    }
  }, []);

  // Save form data to localStorage on change (debounced)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      localStorage.setItem("analysis_form_draft", JSON.stringify(formData));
    }, 500); // Debounce by 500ms

    return () => clearTimeout(timeoutId);
  }, [formData]);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Company validation
    if (!formData.company.trim()) {
      newErrors.company = "Company name is required";
    } else if (formData.company.trim().length < 2) {
      newErrors.company = "Company name must be at least 2 characters";
    } else if (formData.company.trim().length > 100) {
      newErrors.company = "Company name must be less than 100 characters";
    }

    // Industry validation
    if (!formData.industry.trim()) {
      newErrors.industry = "Industry is required";
    }

    // Frameworks validation
    if (formData.frameworks.length === 0) {
      newErrors.frameworks = "Please select at least one business framework";
    } else if (formData.frameworks.length > 4) {
      newErrors.frameworks = "Maximum 4 frameworks allowed";
    }

    // Additional context validation (optional but length-limited)
    if (
      formData.additional_context &&
      formData.additional_context.length > 1000
    ) {
      newErrors.additional_context =
        "Additional context must be less than 1000 characters";
    }

    // Region validation (optional but length-limited)
    if (formData.region && formData.region.length > 100) {
      newErrors.region = "Region must be less than 100 characters";
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
    const estimatedMs =
      depthTimeMap[formData.depth || "standard"] || 20 * 60 * 1000;
    setEstimatedTime(estimatedMs);
    setSubmissionStartTime(Date.now());

    try {
      const endpoint = async ? "/analyze/async" : "/analyze";
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      if (apiKey) {
        headers["X-API-Key"] = apiKey;
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

      // Extract report_id from response for progress tracking
      // Note: For sync requests, report_id is returned after completion
      // For async requests, we get job_id immediately
      let reportId: string | null = null;
      if (async && response.data?.job_id) {
        // For async jobs, use job_id for progress tracking
        reportId = response.data.job_id;
        setCurrentReportId(reportId);
      } else if (response.data?.report_id) {
        // For sync requests, report_id is available after completion
        // Progress tracking won't work for sync (request blocks until done)
        reportId = response.data.report_id;
      }

      setSubmitSuccess(true);
      setLastJobId(async && response.data?.job_id ? response.data.job_id : null);

      // Reset form after successful submission
      const resetData = {
        company: "",
        industry: "",
        frameworks: [],
        depth: "standard" as const,
        additional_context: "",
        region: "",
      };
      setFormData(resetData);
      // Clear saved draft on successful submission
      localStorage.removeItem("analysis_form_draft");

      if (onSuccess) {
        onSuccess(async ? { job_id: response.data.job_id } : response.data);
      }
    } catch (error: any) {
      console.error("Analysis request failed:", error);

      let errorMessage = "Failed to submit analysis request. Please try again.";

      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        // Handle FastAPI validation errors (array of error objects)
        if (Array.isArray(detail)) {
          errorMessage = detail
            .map((err: any) => {
              const field = err.loc?.slice(1).join(".") || "field";
              return `${field}: ${err.msg}`;
            })
            .join("; ");
        } else if (typeof detail === "string") {
          errorMessage = detail;
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      setErrors({ submit: errorMessage });
      setLastJobId(null);

      if (onError) {
        onError(error);
      }
    } finally {
      // Don't reset isSubmitting if we have a reportId (progress component will handle it)
      if (!currentReportId) {
        setIsSubmitting(false);
        setSubmissionStartTime(null);
        setEstimatedTime(null);
      }
    }
  };

  const handleFieldChange = (field: keyof AnalysisRequestData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    if (field === 'frameworks' || field === 'depth') {
      setSelectedPreset(null);
    }

    // Clear field-specific error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field as keyof FormErrors];
        return newErrors;
      });
    }
  };

  const handlePresetApply = (presetId: string) => {
    const preset = PRESET_TEMPLATES.find((p) => p.id === presetId);
    if (!preset) return;
    setSelectedPreset(presetId);
    setFormData((prev) => ({
      ...prev,
      frameworks: preset.frameworks,
      depth: preset.depth,
    }));
    // Remove framework/depth validation errors immediately
    setErrors((prev) => {
      const updated = { ...prev };
      delete updated.frameworks;
      delete updated.depth;
      return updated;
    });
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Request Business Analysis</CardTitle>
        <CardDescription>
          Generate a professional-grade strategic analysis using AI-powered
          business frameworks
        </CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {/* Success Alert */}
          <AnimatePresence>
            {submitSuccess && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <Alert
                  variant="success"
                  dismissible
                  onClose={() => {
                    setSubmitSuccess(false);
                    setLastJobId(null);
                  }}
                  actions={
                    <div className="flex flex-wrap gap-2">
                      {async && lastJobId ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => router.push(`/jobs?highlight=${lastJobId}`)}
                        >
                          Track Job
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => router.push('/reports')}
                        >
                          View Reports
                        </Button>
                      )}
                    </div>
                  }
                >
                  <strong>Analysis request submitted successfully!</strong>
                  {async
                    ? " You will receive a notification when the analysis is complete."
                    : " Processing your request..."}
                </Alert>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error Alert */}
          <AnimatePresence>
            {errors.submit && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <Alert
                  variant="error"
                  dismissible
                  onClose={() => setErrors({ ...errors, submit: undefined })}
                >
                  <div className="space-y-2">
                    <strong>Submission failed:</strong>
                    <p className="text-sm">{errors.submit}</p>
                    <div className="text-xs text-gray-600 mt-2 space-y-1">
                      <p>
                        <strong>What you can do:</strong>
                      </p>
                      <ul className="list-disc list-inside space-y-0.5 ml-2">
                        <li>Check that all required fields are filled correctly</li>
                        <li>Verify your internet connection is stable</li>
                        <li>Try refreshing the page and submitting again</li>
                        <li>
                          If the problem persists, contact support with the error
                          details
                        </li>
                      </ul>
                    </div>
                  </div>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

          {/* Preset templates */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Sparkles className="w-4 h-4 text-primary-500" aria-hidden="true" />
              <span>Need inspiration? Start from a preset and customize from there.</span>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {PRESET_TEMPLATES.map((preset) => (
                <button
                  type="button"
                  key={preset.id}
                  onClick={() => handlePresetApply(preset.id)}
                  className={`text-left border rounded-lg p-3 transition-all focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                    selectedPreset === preset.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                  }`}
                  aria-pressed={selectedPreset === preset.id}
                >
                  <p className="font-medium text-gray-900">{preset.label}</p>
                  <p className="text-sm text-gray-600">{preset.description}</p>
                  <p className="mt-2 text-xs text-gray-500">
                    Frameworks: {preset.frameworks.map((f) => f.toUpperCase()).join(', ')} · Depth: {preset.depth}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Company Name */}
          <Input
            label="Company Name"
            placeholder="e.g., Tesla, Apple, Microsoft"
            value={formData.company}
            onChange={(e) => handleFieldChange("company", e.target.value)}
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
            onChange={(value) => handleFieldChange("industry", value)}
            error={errors.industry}
            disabled={isSubmitting}
            required
          />

          {/* Framework Selector */}
          <FrameworkSelector
            value={formData.frameworks}
            onChange={(value) => handleFieldChange("frameworks", value)}
            error={errors.frameworks}
            disabled={isSubmitting}
            required
          />

          {/* Analysis Depth */}
          <DepthSelector
            value={formData.depth || "standard"}
            onChange={(value) => handleFieldChange("depth", value)}
            error={errors.depth}
            disabled={isSubmitting}
          />

          {/* Region (Optional) */}
          <Input
            label="Region"
            placeholder="e.g., North America, EMEA, Asia-Pacific (optional)"
            value={formData.region || ""}
            onChange={(e) => handleFieldChange("region", e.target.value)}
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
              <FileText
                className="absolute left-3 top-3 w-5 h-5 text-gray-400 pointer-events-none"
                aria-hidden="true"
              />
              <textarea
                value={formData.additional_context || ""}
                onChange={(e) =>
                  handleFieldChange("additional_context", e.target.value)
                }
                disabled={isSubmitting}
                maxLength={1000}
                rows={4}
                placeholder="Provide any additional context, specific questions, or focus areas for the analysis (optional)"
                className={`
                  w-full pl-10 pr-4 py-3 border rounded-md transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                  disabled:opacity-50 disabled:cursor-not-allowed
                  ${
                    errors.additional_context
                      ? "border-red-300"
                      : "border-gray-300"
                  }
                `}
                aria-describedby={
                  errors.additional_context
                    ? "additional-context-error"
                    : "additional-context-helper"
                }
              />
            </div>
            {errors.additional_context ? (
              <p
                id="additional-context-error"
                className="mt-1 text-sm text-red-600"
                role="alert"
              >
                {errors.additional_context}
              </p>
            ) : (
              <div className="mt-1 flex justify-between items-center">
                <p
                  id="additional-context-helper"
                  className="text-sm text-gray-500"
                >
                  Provide specific areas of focus or questions
                </p>
                <span className="text-xs text-gray-400">
                  {(formData.additional_context || "").length}/1000
                </span>
              </div>
            )}
          </div>
        </CardContent>

        <CardFooter className="flex flex-col sm:flex-row gap-3 justify-between items-center">
          <p className="text-xs text-gray-500">
            All fields marked with <span className="text-red-500">*</span> are
            required
          </p>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                const resetData = {
                  company: "",
                  industry: "",
                  frameworks: [],
                  depth: "standard" as const,
                  additional_context: "",
                  region: "",
                };
                setFormData(resetData);
                setErrors({});
                setSubmitSuccess(false);
                // Clear saved draft
                localStorage.removeItem("analysis_form_draft");
              }}
              disabled={isSubmitting}
            >
              Reset
            </Button>

            <div className="flex flex-col items-end gap-2">
              {isSubmitting && currentReportId ? (
                <div className="w-full mb-4">
                  <AnalysisProgress
                    reportId={currentReportId}
                    apiUrl={API_URL}
                    onComplete={() => {
                      setIsSubmitting(false);
                      setCurrentReportId(null);
                    }}
                    onError={(error) => {
                      setIsSubmitting(false);
                      setCurrentReportId(null);
                      setErrors({ submit: error });
                    }}
                  />
                </div>
              ) : isSubmitting && estimatedTime && submissionStartTime ? (
                <SubmissionTimer
                  startTime={submissionStartTime}
                  estimatedTime={estimatedTime}
                />
              ) : null}
              <motion.div
                whileHover={!isSubmitting ? { scale: 1.02 } : {}}
                whileTap={!isSubmitting ? { scale: 0.98 } : {}}
              >
                <Button
                  type="submit"
                  variant="primary"
                  isLoading={isSubmitting}
                  disabled={isSubmitting}
                  leftIcon={
                    !isSubmitting ? <Send className="w-4 h-4" /> : undefined
                  }
                  className="relative"
                >
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <Spinner size="sm" variant="circular" color="white" />
                      {async ? "Submitting..." : "Generating Analysis..."}
                    </span>
                  ) : (
                    <>
                      {async ? "Submit Request" : "Generate Analysis"}
                    </>
                  )}
                </Button>
              </motion.div>
            </div>
          </div>
        </CardFooter>
      </form>
    </Card>
  );
};
export default AnalysisRequestForm;
