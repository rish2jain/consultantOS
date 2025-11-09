"use client";

import React from "react";
import { Zap, Gauge, Microscope } from "lucide-react";

export interface DepthOption {
  id: "quick" | "standard" | "deep";
  name: string;
  description: string;
  estimatedTime: string;
  icon: React.ReactNode;
}

export interface DepthSelectorProps {
  /** Selected depth value */
  value: "quick" | "standard" | "deep";
  /** Change handler */
  onChange: (depth: "quick" | "standard" | "deep") => void;
  /** Error message */
  error?: string;
  /** Disabled state */
  disabled?: boolean;
}

const depthOptions: DepthOption[] = [
  {
    id: "quick",
    name: "Quick Analysis",
    description: "High-level overview with key insights",
    estimatedTime: "~10 minutes",
    icon: <Zap className="w-5 h-5" />,
  },
  {
    id: "standard",
    name: "Standard Analysis",
    description: "Balanced depth with comprehensive coverage",
    estimatedTime: "~20 minutes",
    icon: <Gauge className="w-5 h-5" />,
  },
  {
    id: "deep",
    name: "Deep Analysis",
    description: "Thorough investigation with detailed insights",
    estimatedTime: "~30 minutes",
    icon: <Microscope className="w-5 h-5" />,
  },
];

export const DepthSelector: React.FC<DepthSelectorProps> = ({
  value,
  onChange,
  error,
  disabled = false,
}) => {
  const selectorId = `depth-selector-${React.useId()}`;

  const handleKeyDown = (
    e: React.KeyboardEvent,
    depthId: "quick" | "standard" | "deep"
  ) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      if (!disabled) {
        onChange(depthId);
      }
    }
  };

  return (
    <div>
      <label
        id={`${selectorId}-label`}
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Analysis Depth
      </label>

      <div
        role="radiogroup"
        aria-labelledby={`${selectorId}-label`}
        aria-describedby={error ? `${selectorId}-error` : undefined}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        {depthOptions.map((option) => {
          const isSelected = value === option.id;

          return (
            <div key={option.id}>
              <input
                type="radio"
                id={`${selectorId}-${option.id}`}
                name={selectorId}
                value={option.id}
                checked={isSelected}
                onChange={() => !disabled && onChange(option.id)}
                disabled={disabled}
                className="sr-only"
                aria-describedby={`${selectorId}-${option.id}-description`}
                aria-checked={isSelected}
              />
              <label
                htmlFor={`${selectorId}-${option.id}`}
                onKeyDown={(e) => handleKeyDown(e, option.id)}
                tabIndex={disabled ? -1 : 0}
                className={`
                  block p-4 rounded-lg border-2 transition-all duration-200 cursor-pointer
                  ${
                    disabled
                      ? "opacity-50 cursor-not-allowed"
                      : "hover:shadow-md hover:scale-[1.02]"
                  }
                  ${
                    isSelected
                      ? "border-primary-500 bg-primary-50 shadow-md"
                      : "border-gray-200 hover:border-gray-300"
                  }
                `}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`
                      flex-shrink-0 p-2 rounded-lg
                      ${
                        isSelected
                          ? "bg-primary-100 text-primary-700"
                          : "bg-gray-100 text-gray-600"
                      }
                    `}
                    aria-hidden="true"
                  >
                    {option.icon}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-base font-semibold text-gray-900">
                        {option.name}
                      </h3>
                      <div
                        className={`
                          w-4 h-4 rounded-full border-2 flex items-center justify-center
                          ${
                            isSelected
                              ? "border-primary-600 bg-primary-600"
                              : "border-gray-300 bg-white"
                          }
                        `}
                        aria-hidden="true"
                      >
                        {isSelected && (
                          <div className="w-2 h-2 rounded-full bg-white" />
                        )}
                      </div>
                    </div>

                    <p
                      id={`${selectorId}-${option.id}-description`}
                      className="text-sm text-gray-600 mb-2"
                    >
                      {option.description}
                    </p>

                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <svg
                        className="w-3 h-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        aria-hidden="true"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <span>{option.estimatedTime}</span>
                    </div>
                  </div>
                </div>
              </label>
            </div>
          );
        })}
      </div>

      {error && (
        <p
          id={`${selectorId}-error`}
          className="mt-2 text-sm text-red-600"
          role="alert"
        >
          {error}
        </p>
      )}

      <p className="mt-2 text-xs text-gray-500">
        Choose analysis depth based on your time constraints and detail
        requirements.
      </p>
    </div>
  );
};
