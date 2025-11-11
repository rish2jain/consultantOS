'use client';

import { useEffect, useRef } from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';

/**
 * Individual disruption threat details
 */
export interface DisruptionThreat {
  threat_type: string;
  severity: number;  // 0-100
  description: string;
  evidence: string[];
  recommended_actions: string[];
  timeline: string;  // "immediate", "3-months", "6-months", "12-months"
}

/**
 * Complete disruption assessment data
 */
export interface DisruptionAssessment {
  overall_risk: number;  // 0-100
  risk_trend: number;    // delta from previous assessment
  vulnerability_breakdown: {
    incumbent_overserving: number;
    asymmetric_threat_velocity: number;
    technology_shift_momentum: number;
    customer_job_misalignment: number;
    business_model_innovation: number;
  };
  primary_threats: DisruptionThreat[];
  risk_history?: {
    timestamp: string;
    overall_risk: number;
    dimensions: {
      incumbent_overserving: number;
      asymmetric_threat_velocity: number;
      technology_shift_momentum: number;
      customer_job_misalignment: number;
      business_model_innovation: number;
    };
  }[];
}

interface DisruptionRadarProps {
  data: DisruptionAssessment;
  onActionClick?: (action: string, threat: DisruptionThreat) => void;
  className?: string;
}

/**
 * Disruption Radar Chart Component
 *
 * Visualizes disruption risk across 5 key dimensions using:
 * - Radar/spider chart with risk zones (green/yellow/red)
 * - Threat detail cards with evidence
 * - Risk trend sparklines (30/60/90-day)
 * - Recommended action buttons
 *
 * Based on Clayton Christensen's disruption theory with focus on:
 * 1. Incumbent overserving (sustaining vs disruptive innovation)
 * 2. Asymmetric threat velocity (pace of disruption)
 * 3. Technology shift momentum (S-curve transitions)
 * 4. Customer job misalignment (jobs-to-be-done gaps)
 * 5. Business model innovation (value network threats)
 *
 * @component
 * @example
 * ```tsx
 * <DisruptionRadar
 *   data={disruptionData}
 *   onActionClick={(action, threat) => handleAction(action, threat)}
 * />
 * ```
 */
export default function DisruptionRadar({
  data,
  onActionClick,
  className = '',
}: DisruptionRadarProps) {
  // Transform data for radar chart
  const radarData = [
    {
      dimension: 'Incumbent Overserving',
      value: data.vulnerability_breakdown.incumbent_overserving,
      fullMark: 100,
    },
    {
      dimension: 'Threat Velocity',
      value: data.vulnerability_breakdown.asymmetric_threat_velocity,
      fullMark: 100,
    },
    {
      dimension: 'Tech Shift',
      value: data.vulnerability_breakdown.technology_shift_momentum,
      fullMark: 100,
    },
    {
      dimension: 'Job Misalignment',
      value: data.vulnerability_breakdown.customer_job_misalignment,
      fullMark: 100,
    },
    {
      dimension: 'BM Innovation',
      value: data.vulnerability_breakdown.business_model_innovation,
      fullMark: 100,
    },
  ];

  // Risk level categorization
  const getRiskLevel = (score: number): { label: string; color: string; bgColor: string } => {
    if (score >= 70) return { label: 'High Risk', color: 'text-red-800', bgColor: 'bg-red-100' };
    if (score >= 40) return { label: 'Moderate Risk', color: 'text-yellow-800', bgColor: 'bg-yellow-100' };
    return { label: 'Low Risk', color: 'text-green-800', bgColor: 'bg-green-100' };
  };

  const overallRisk = getRiskLevel(data.overall_risk);

  // Timeline badge styles
  const getTimelineBadge = (timeline: string): { color: string; bgColor: string } => {
    const normalized = timeline.toLowerCase();
    if (normalized.includes('immediate')) return { color: 'text-red-800', bgColor: 'bg-red-100' };
    if (normalized.includes('3-month')) return { color: 'text-orange-800', bgColor: 'bg-orange-100' };
    if (normalized.includes('6-month')) return { color: 'text-yellow-800', bgColor: 'bg-yellow-100' };
    return { color: 'text-blue-800', bgColor: 'bg-blue-100' };
  };

  return (
    <div className={`${className}`}>
      {/* Header with Overall Risk */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Disruption Risk Assessment</h3>
            <p className="text-sm text-gray-500">5-dimensional disruption vulnerability analysis</p>
          </div>
          <div className="text-right">
            <div className={`inline-flex items-center px-4 py-2 rounded-lg ${overallRisk.bgColor}`}>
              <span className={`text-2xl font-bold ${overallRisk.color}`}>
                {data.overall_risk.toFixed(0)}
              </span>
              <span className={`text-sm ${overallRisk.color} ml-2`}>/ 100</span>
            </div>
            <div className="mt-1 flex items-center justify-end gap-2">
              <span className={`text-xs ${overallRisk.color} font-medium`}>{overallRisk.label}</span>
              {data.risk_trend !== 0 && (
                <span className={`text-xs flex items-center ${data.risk_trend > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {data.risk_trend > 0 ? '↑' : '↓'} {Math.abs(data.risk_trend).toFixed(1)}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-gray-900 mb-4">Vulnerability Breakdown</h4>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis
                dataKey="dimension"
                tick={{ fill: '#6b7280', fontSize: 11 }}
                tickLine={false}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fill: '#9ca3af', fontSize: 10 }}
                tickCount={6}
              />
              <Radar
                name="Risk Level"
                dataKey="value"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
                strokeWidth={2}
              />

              {/* Risk zones as background */}
              <Radar
                dataKey="fullMark"
                stroke="transparent"
                fill="#10b981"
                fillOpacity={0.05}
              />
            </RadarChart>
          </ResponsiveContainer>

          {/* Legend for risk zones */}
          <div className="mt-4 flex items-center justify-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-200 rounded"></div>
              <span className="text-gray-600">Low (0-39)</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-yellow-200 rounded"></div>
              <span className="text-gray-600">Moderate (40-69)</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-red-200 rounded"></div>
              <span className="text-gray-600">High (70+)</span>
            </div>
          </div>
        </div>

        {/* Risk Trend Sparklines */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-gray-900 mb-4">Risk Trend (90 days)</h4>
          {data.risk_history && data.risk_history.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.risk_history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="timestamp"
                  tick={{ fill: '#6b7280', fontSize: 10 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: '#6b7280', fontSize: 10 }}
                />
                <Tooltip
                  contentStyle={{ fontSize: 12 }}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Line
                  type="monotone"
                  dataKey="overall_risk"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 3 }}
                  name="Overall Risk"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400 text-sm">
              No historical data available
            </div>
          )}
        </div>
      </div>

      {/* Primary Threats Detail Cards */}
      <div className="mt-6">
        <h4 className="text-sm font-semibold text-gray-900 mb-4">Primary Threats</h4>
        <div className="space-y-4">
          {data.primary_threats.length === 0 ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
              <svg className="w-12 h-12 mx-auto text-green-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-green-800 font-medium">No immediate threats detected</p>
              <p className="text-green-600 text-sm mt-1">Your competitive position is currently stable</p>
            </div>
          ) : (
            data.primary_threats.map((threat, idx) => {
              const severityLevel = getRiskLevel(threat.severity);
              const timelineBadge = getTimelineBadge(threat.timeline);

              return (
                <div
                  key={idx}
                  className={`border-l-4 ${
                    threat.severity >= 70
                      ? 'border-red-500 bg-red-50'
                      : threat.severity >= 40
                      ? 'border-yellow-500 bg-yellow-50'
                      : 'border-green-500 bg-green-50'
                  } rounded-lg p-4`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h5 className="font-semibold text-gray-900">{threat.threat_type}</h5>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${severityLevel.bgColor} ${severityLevel.color}`}>
                          {threat.severity.toFixed(0)} / 100
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{threat.description}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded ${timelineBadge.bgColor} ${timelineBadge.color} whitespace-nowrap ml-4`}>
                      {threat.timeline}
                    </span>
                  </div>

                  {/* Evidence */}
                  {threat.evidence.length > 0 && (
                    <div className="mb-3">
                      <h6 className="text-xs font-semibold text-gray-700 mb-2">Evidence:</h6>
                      <ul className="text-xs text-gray-600 space-y-1">
                        {threat.evidence.map((evidence, evidenceIdx) => (
                          <li key={evidenceIdx} className="flex items-start gap-2">
                            <span className="text-gray-400 mt-0.5">•</span>
                            <span>{evidence}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommended Actions */}
                  {threat.recommended_actions.length > 0 && (
                    <div>
                      <h6 className="text-xs font-semibold text-gray-700 mb-2">Recommended Actions:</h6>
                      <div className="flex flex-wrap gap-2">
                        {threat.recommended_actions.map((action, actionIdx) => (
                          <button
                            key={actionIdx}
                            onClick={() => onActionClick?.(action, threat)}
                            className="px-3 py-1.5 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50 hover:border-blue-500 hover:text-blue-600 transition-colors"
                          >
                            {action}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Dimension Details */}
      <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Dimension Details</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(data.vulnerability_breakdown).map(([key, value]) => {
            const formattedKey = key
              .split('_')
              .map(word => word.charAt(0).toUpperCase() + word.slice(1))
              .join(' ');
            const level = getRiskLevel(value);

            return (
              <div key={key} className="flex items-center justify-between">
                <span className="text-xs text-gray-600">{formattedKey}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        value >= 70 ? 'bg-red-500' : value >= 40 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${value}%` }}
                    />
                  </div>
                  <span className={`text-xs font-medium ${level.color} min-w-[3rem] text-right`}>
                    {value.toFixed(0)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
