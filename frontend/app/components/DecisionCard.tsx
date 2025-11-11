'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Individual decision option with pros/cons and financial impact
 */
export interface DecisionOption {
  option_id: string;
  title: string;
  description: string;
  financial_impact: number;  // Expected impact ($)
  implementation_time: string;  // e.g., "2-4 weeks"
  resource_requirements: string[];
  pros: string[];
  cons: string[];
  risk_level: 'low' | 'medium' | 'high';
  confidence: number;  // 0-1
}

/**
 * Strategic decision requiring action
 */
export interface StrategicDecision {
  decision_id: string;
  title: string;
  description: string;
  urgency_days: number;  // Days until decision must be made
  financial_impact: number;  // Total potential impact ($)
  category: 'strategic' | 'operational' | 'tactical';
  evidence: string[];
  options: DecisionOption[];
  recommended_option: string;  // option_id
  recommendation_rationale: string;
  implementation_roadmap?: {
    phase: string;
    duration: string;
    deliverables: string[];
  }[];
}

interface DecisionCardProps {
  decision: StrategicDecision;
  onAccept?: (decisionId: string, optionId: string) => void;
  onDefer?: (decisionId: string, daysToDefer: number) => void;
  onCustomize?: (decisionId: string) => void;
  className?: string;
}

/**
 * Decision Card Component
 *
 * Interactive card for presenting strategic decisions with:
 * - Urgency countdown timer
 * - Financial impact visualization
 * - Expandable options comparison
 * - Evidence list (collapsible)
 * - Implementation roadmap timeline
 * - Action buttons: Accept, Defer, Customize
 *
 * Designed for executive decision-making with clear tradeoffs and recommendations.
 *
 * @component
 * @example
 * ```tsx
 * <DecisionCard
 *   decision={strategicDecision}
 *   onAccept={(decisionId, optionId) => handleAccept(decisionId, optionId)}
 *   onDefer={(decisionId, days) => handleDefer(decisionId, days)}
 * />
 * ```
 */
export default function DecisionCard({
  decision,
  onAccept,
  onDefer,
  onCustomize,
  className = '',
}: DecisionCardProps) {
  const [expandedOption, setExpandedOption] = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState(false);
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [selectedOption, setSelectedOption] = useState<string>(decision.recommended_option);

  // Calculate urgency level
  const getUrgencyLevel = (): { label: string; color: string; bgColor: string } => {
    if (decision.urgency_days <= 7) {
      return { label: 'Critical', color: 'text-red-800', bgColor: 'bg-red-100' };
    }
    if (decision.urgency_days <= 30) {
      return { label: 'High', color: 'text-orange-800', bgColor: 'bg-orange-100' };
    }
    if (decision.urgency_days <= 90) {
      return { label: 'Medium', color: 'text-yellow-800', bgColor: 'bg-yellow-100' };
    }
    return { label: 'Low', color: 'text-blue-800', bgColor: 'bg-blue-100' };
  };

  const urgencyLevel = getUrgencyLevel();

  // Format financial impact
  const formatCurrency = (amount: number): string => {
    if (Math.abs(amount) >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    }
    if (Math.abs(amount) >= 1000) {
      return `$${(amount / 1000).toFixed(0)}K`;
    }
    return `$${amount.toFixed(0)}`;
  };

  // Risk level badge
  const getRiskBadge = (risk: string): { color: string; bgColor: string } => {
    switch (risk) {
      case 'high':
        return { color: 'text-red-800', bgColor: 'bg-red-100' };
      case 'medium':
        return { color: 'text-yellow-800', bgColor: 'bg-yellow-100' };
      default:
        return { color: 'text-green-800', bgColor: 'bg-green-100' };
    }
  };

  // Category badge
  const getCategoryBadge = (): { color: string; bgColor: string } => {
    switch (decision.category) {
      case 'strategic':
        return { color: 'text-purple-800', bgColor: 'bg-purple-100' };
      case 'operational':
        return { color: 'text-blue-800', bgColor: 'bg-blue-100' };
      default:
        return { color: 'text-gray-800', bgColor: 'bg-gray-100' };
    }
  };

  const categoryBadge = getCategoryBadge();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white border-2 border-gray-200 rounded-lg shadow-lg ${className}`}
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-xl font-bold text-gray-900">{decision.title}</h3>
              <span className={`px-2 py-1 text-xs rounded ${categoryBadge.bgColor} ${categoryBadge.color} capitalize`}>
                {decision.category}
              </span>
            </div>
            <p className="text-sm text-gray-600">{decision.description}</p>
          </div>

          {/* Urgency Indicator */}
          <div className={`ml-4 px-4 py-3 rounded-lg ${urgencyLevel.bgColor} text-center min-w-[120px]`}>
            <div className={`text-2xl font-bold ${urgencyLevel.color}`}>
              {decision.urgency_days}
            </div>
            <div className={`text-xs ${urgencyLevel.color} font-medium`}>
              days remaining
            </div>
            <div className={`text-xs ${urgencyLevel.color} mt-1`}>
              {urgencyLevel.label} Priority
            </div>
          </div>
        </div>

        {/* Financial Impact Highlight */}
        <div className="mt-4 flex items-center gap-4">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-gray-600">Potential Impact:</span>
            <span className="text-lg font-bold text-green-600">
              {formatCurrency(decision.financial_impact)}
            </span>
          </div>

          {/* Evidence Toggle */}
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="ml-auto px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Evidence ({decision.evidence.length})
          </button>
        </div>

        {/* Evidence Panel */}
        <AnimatePresence>
          {showEvidence && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-4 bg-gray-50 rounded-lg p-4 overflow-hidden"
            >
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Supporting Evidence:</h4>
              <ul className="text-sm text-gray-700 space-y-2">
                {decision.evidence.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Options Comparison */}
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-semibold text-gray-900">Decision Options</h4>
          <span className="text-xs text-gray-500">{decision.options.length} options available</span>
        </div>

        <div className="space-y-3">
          {decision.options.map((option) => {
            const isRecommended = option.option_id === decision.recommended_option;
            const isSelected = option.option_id === selectedOption;
            const isExpanded = option.option_id === expandedOption;
            const riskBadge = getRiskBadge(option.risk_level);

            return (
              <div
                key={option.option_id}
                className={`border-2 rounded-lg transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : isRecommended
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <div
                  className="p-4 cursor-pointer"
                  onClick={() => setExpandedOption(isExpanded ? null : option.option_id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <input
                          type="radio"
                          checked={isSelected}
                          onChange={() => setSelectedOption(option.option_id)}
                          onClick={(e) => e.stopPropagation()}
                          className="w-4 h-4 text-blue-600"
                        />
                        <h5 className="font-semibold text-gray-900">{option.title}</h5>
                        {isRecommended && (
                          <span className="px-2 py-0.5 text-xs bg-green-600 text-white rounded-full">
                            Recommended
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 ml-6">{option.description}</p>
                    </div>

                    <div className="ml-4 text-right flex-shrink-0">
                      <div className="text-lg font-bold text-gray-900">
                        {formatCurrency(option.financial_impact)}
                      </div>
                      <div className="text-xs text-gray-500">{option.implementation_time}</div>
                    </div>
                  </div>

                  {/* Quick Stats */}
                  <div className="mt-3 ml-6 flex items-center gap-4">
                    <span className={`px-2 py-1 text-xs rounded ${riskBadge.bgColor} ${riskBadge.color} capitalize`}>
                      {option.risk_level} Risk
                    </span>
                    <span className="text-xs text-gray-600">
                      {(option.confidence * 100).toFixed(0)}% confidence
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedOption(isExpanded ? null : option.option_id);
                      }}
                      className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                    >
                      {isExpanded ? 'Hide' : 'Show'} Details
                      <svg
                        className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="border-t border-gray-200 overflow-hidden"
                    >
                      <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Pros */}
                        <div>
                          <h6 className="text-xs font-semibold text-gray-700 mb-2">Pros:</h6>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {option.pros.map((pro, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <svg className="w-3 h-3 text-green-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                                <span>{pro}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Cons */}
                        <div>
                          <h6 className="text-xs font-semibold text-gray-700 mb-2">Cons:</h6>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {option.cons.map((con, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <svg className="w-3 h-3 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                                <span>{con}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Resource Requirements */}
                        {option.resource_requirements.length > 0 && (
                          <div className="md:col-span-2">
                            <h6 className="text-xs font-semibold text-gray-700 mb-2">Resource Requirements:</h6>
                            <div className="flex flex-wrap gap-2">
                              {option.resource_requirements.map((resource, idx) => (
                                <span key={idx} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                  {resource}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>

        {/* Recommendation Rationale */}
        {decision.recommendation_rationale && (
          <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h5 className="text-sm font-semibold text-blue-900 mb-2">Why We Recommend This:</h5>
            <p className="text-sm text-blue-800">{decision.recommendation_rationale}</p>
          </div>
        )}
      </div>

      {/* Implementation Roadmap */}
      {decision.implementation_roadmap && decision.implementation_roadmap.length > 0 && (
        <div className="px-6 pb-6">
          <button
            onClick={() => setShowRoadmap(!showRoadmap)}
            className="w-full px-4 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {showRoadmap ? 'Hide' : 'Show'} Implementation Roadmap
          </button>

          <AnimatePresence>
            {showRoadmap && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="mt-4 overflow-hidden"
              >
                <div className="space-y-4">
                  {decision.implementation_roadmap.map((phase, idx) => (
                    <div key={idx} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {idx + 1}
                        </div>
                        {idx < decision.implementation_roadmap!.length - 1 && (
                          <div className="w-0.5 flex-1 bg-blue-200 my-2"></div>
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <div className="flex items-center gap-2 mb-1">
                          <h6 className="font-semibold text-gray-900">{phase.phase}</h6>
                          <span className="text-xs text-gray-500">({phase.duration})</span>
                        </div>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {phase.deliverables.map((deliverable, dIdx) => (
                            <li key={dIdx} className="flex items-start gap-2">
                              <span className="text-blue-600 mt-1">•</span>
                              <span>{deliverable}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Action Buttons */}
      <div className="border-t border-gray-200 p-6 bg-gray-50 rounded-b-lg">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onAccept?.(decision.decision_id, selectedOption)}
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Accept Decision
          </button>

          <button
            onClick={() => {
              const days = prompt('Defer for how many days?', '7');
              if (days) {
                onDefer?.(decision.decision_id, parseInt(days));
              }
            }}
            className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-100 font-medium transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Defer
          </button>

          <button
            onClick={() => onCustomize?.(decision.decision_id)}
            className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-100 font-medium transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Customize
          </button>
        </div>
      </div>
    </motion.div>
  );
}
