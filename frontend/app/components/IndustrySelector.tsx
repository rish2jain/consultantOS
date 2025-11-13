"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Search, Check } from "lucide-react";

export interface IndustrySelectorProps {
  /** Selected industry value */
  value: string;
  /** Change handler */
  onChange: (industry: string) => void;
  /** Error message */
  error?: string;
  /** Disabled state */
  disabled?: boolean;
  /** Required field indicator */
  required?: boolean;
  /** Placeholder text */
  placeholder?: string;
}

const industries = [
  "Technology",
  "Healthcare",
  "Finance",
  "Retail",
  "Manufacturing",
  "Energy",
  "Telecommunications",
  "Transportation",
  "Real Estate",
  "Automotive",
  "Electric Vehicles",
  "Aerospace",
  "Agriculture",
  "Biotechnology",
  "Construction",
  "Consumer Goods",
  "E-commerce",
  "Education",
  "Entertainment",
  "Food & Beverage",
  "Hospitality",
  "Insurance",
  "Legal Services",
  "Media",
  "Pharmaceuticals",
  "Professional Services",
  "Software",
  "Utilities",
  "Other",
];

export const IndustrySelector: React.FC<IndustrySelectorProps> = ({
  value,
  onChange,
  error,
  disabled = false,
  required = false,
  placeholder = "Select an industry...",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const selectorId = `industry-selector-${React.useId()}`;

  const filteredIndustries = industries.filter((industry) =>
    industry.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchQuery("");
        setHighlightedIndex(-1);
      }
    };

    // Only add listener when dropdown is open
    if (isOpen) {
      // Use 'click' instead of 'mousedown' to allow option clicks to process first
      // Defer to next tick to avoid catching the opening click
      const timeoutId = setTimeout(() => {
        document.addEventListener("click", handleClickOutside, true);
      }, 0);
      
      return () => {
        clearTimeout(timeoutId);
        document.removeEventListener("click", handleClickOutside, true);
      };
    }
  }, [isOpen]);

  const handleSelect = (industry: string) => {
    onChange(industry);
    setIsOpen(false);
    setSearchQuery("");
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    switch (e.key) {
      case "Enter":
        e.preventDefault();
        if (isOpen) {
          if (
            highlightedIndex >= 0 &&
            highlightedIndex < filteredIndustries.length
          ) {
            handleSelect(filteredIndustries[highlightedIndex]);
          }
        } else {
          setIsOpen(true);
        }
        break;

      case "ArrowDown":
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setHighlightedIndex((prev) =>
            prev < filteredIndustries.length - 1 ? prev + 1 : 0
          );
        }
        break;

      case "ArrowUp":
        e.preventDefault();
        if (isOpen) {
          setHighlightedIndex((prev) =>
            prev > 0 ? prev - 1 : filteredIndustries.length - 1
          );
        }
        break;

      case "Escape":
        setIsOpen(false);
        setSearchQuery("");
        setHighlightedIndex(-1);
        break;

      case "Tab":
        if (isOpen) {
          setIsOpen(false);
          setSearchQuery("");
          setHighlightedIndex(-1);
        }
        break;
    }
  };

  return (
    <div ref={dropdownRef} className="relative">
      <label
        id={`${selectorId}-label`}
        htmlFor={selectorId}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        Industry
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <button
        id={selectorId}
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className={`
          w-full px-4 py-2 text-left bg-white border rounded-md transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
          ${error ? "border-red-300" : "border-gray-300"}
          ${
            disabled
              ? "bg-gray-50 cursor-not-allowed opacity-50"
              : "cursor-pointer hover:border-gray-400"
          }
        `}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby={`${selectorId}-label`}
        aria-describedby={error ? `${selectorId}-error` : undefined}
      >
        <div className="flex items-center justify-between">
          <span className={value ? "text-gray-900" : "text-gray-400"}>
            {value || placeholder}
          </span>
          <ChevronDown
            className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
              isOpen ? "transform rotate-180" : ""
            }`}
            aria-hidden="true"
          />
        </div>
      </button>

      {isOpen && !disabled && (
        <div
          className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-80 overflow-hidden"
          role="listbox"
          aria-labelledby={selectorId}
        >
          <div className="p-2 border-b border-gray-200 sticky top-0 bg-white z-10">
            <div className="relative">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
                aria-hidden="true"
              />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setHighlightedIndex(0);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Search industries..."
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                aria-label="Search industries"
              />
            </div>
          </div>

          <div className="overflow-y-auto max-h-64">
            {filteredIndustries.length > 0 ? (
              <ul className="py-1">
                {filteredIndustries.map((industry, index) => {
                  const isSelected = value === industry;
                  const isHighlighted = index === highlightedIndex;

                  return (
                    <li key={industry}>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleSelect(industry);
                        }}
                        className={`
                          w-full text-left px-4 py-2 text-sm transition-colors duration-150
                          flex items-center justify-between
                          ${isHighlighted ? "bg-primary-50" : ""}
                          ${
                            isSelected
                              ? "bg-primary-100 text-primary-900"
                              : "text-gray-900 hover:bg-gray-50"
                          }
                        `}
                        role="option"
                        aria-selected={isSelected}
                      >
                        <span>{industry}</span>
                        {isSelected && (
                          <Check
                            className="w-4 h-4 text-primary-600"
                            aria-label="Selected"
                          />
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <div className="px-4 py-8 text-center text-sm text-gray-500">
                No industries found matching "{searchQuery}"
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <p
          id={`${selectorId}-error`}
          className="mt-1 text-sm text-red-600"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
};
