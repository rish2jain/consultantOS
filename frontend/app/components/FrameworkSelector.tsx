"use client";

import React from "react";
import { Target, TrendingUp, Globe, Waves, CheckCircle, HelpCircle } from "lucide-react";
import { Card, CardContent, Tooltip } from "@/app/components";

export interface FrameworkOption {
  id: "porter" | "swot" | "pestel" | "blue_ocean";
  name: string;
  description: string;
  icon: React.ReactNode;
}

export interface FrameworkSelectorProps {
  /** Selected framework IDs */
  value: ("porter" | "swot" | "pestel" | "blue_ocean")[];
  /** Change handler */
  onChange: (
    frameworks: ("porter" | "swot" | "pestel" | "blue_ocean")[]
  ) => void;
  /** Error message */
  error?: string;
  /** Disabled state */
  disabled?: boolean;
  /** Required field indicator */
  required?: boolean;
}

const frameworkOptions: FrameworkOption[] = [
  {
    id: "porter",
    name: "Porter's Five Forces",
    description:
      "Analyze competitive intensity and attractiveness of an industry",
    icon: <Target className="w-5 h-5" />,
  },
  {
    id: "swot",
    name: "SWOT Analysis",
    description: "Identify strengths, weaknesses, opportunities, and threats",
    icon: <TrendingUp className="w-5 h-5" />,
  },
  {
    id: "pestel",
    name: "PESTEL Analysis",
    description:
      "Examine political, economic, social, technological, environmental, and legal factors",
    icon: <Globe className="w-5 h-5" />,
  },
  {
    id: "blue_ocean",
    name: "Blue Ocean Strategy",
    description:
      "Discover uncontested market spaces and make competition irrelevant",
    icon: <Waves className="w-5 h-5" />,
  },
];

export const FrameworkSelector: React.FC<FrameworkSelectorProps> = ({
  value,
  onChange,
  error,
  disabled = false,
  required = false,
}) => {
  const selectorId = `framework-selector-${React.useId()}`;

  const handleToggle = (
    frameworkId: "porter" | "swot" | "pestel" | "blue_ocean"
  ) => {
    if (disabled) return;

    if (value.includes(frameworkId)) {
      onChange(value.filter((id) => id !== frameworkId));
    } else {
      onChange([...value, frameworkId]);
    }
  };

  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <label
          id={`${selectorId}-label`}
          className="block text-sm font-medium text-gray-700"
        >
          Business Frameworks
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        <Tooltip
          content={
            <div className="space-y-1">
              <p className="font-semibold">Business Frameworks</p>
              <p className="text-xs">
                Select one or more strategic analysis frameworks. Each framework provides different insights:
              </p>
              <ul className="text-xs list-disc list-inside mt-1 space-y-0.5">
                <li><strong>Porter's 5 Forces:</strong> Industry competitive analysis</li>
                <li><strong>SWOT:</strong> Internal strengths & weaknesses, external opportunities & threats</li>
                <li><strong>PESTEL:</strong> Political, Economic, Social, Technological, Environmental, Legal factors</li>
                <li><strong>Blue Ocean:</strong> Uncontested market space creation</li>
              </ul>
            </div>
          }
          placement="right"
          maxWidth="350px"
        >
          <HelpCircle className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help" aria-label="Help: Business Frameworks" />
        </Tooltip>
      </div>

      <div
        role="group"
        aria-labelledby={`${selectorId}-label`}
        aria-describedby={error ? `${selectorId}-error` : undefined}
        className="space-y-3"
      >
        {frameworkOptions.map((framework) => {
          const isSelected = value.includes(framework.id);

          return (
            <button
              key={framework.id}
              type="button"
              onClick={() => handleToggle(framework.id)}
              disabled={disabled}
              className={`
                w-full text-left transition-all duration-200 rounded-lg
                ${disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer"}
              `}
              aria-pressed={isSelected}
              aria-label={`${framework.name}: ${framework.description}`}
            >
              <Card
                className={`
                  border-2 transition-all duration-200
                  ${
                    isSelected
                      ? "border-primary-500 bg-primary-50 shadow-md"
                      : "border-gray-200 hover:border-gray-300 hover:shadow-sm"
                  }
                  ${disabled ? "" : "hover:scale-[1.01]"}
                `}
              >
                <CardContent className="p-4">
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
                      {framework.icon}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <h3 className="text-base font-semibold text-gray-900">
                          {framework.name}
                        </h3>

                        {isSelected && (
                          <CheckCircle
                            className="flex-shrink-0 w-5 h-5 text-primary-600"
                            aria-label="Selected"
                          />
                        )}
                      </div>

                      <p className="text-sm text-gray-600 mt-1">
                        {framework.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </button>
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
        Select at least one framework for analysis. Multiple frameworks provide
        comprehensive insights.
      </p>
    </div>
  );
};
