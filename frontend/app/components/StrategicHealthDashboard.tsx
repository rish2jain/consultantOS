'use client';

import { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

/**
 * Threat with urgency and impact scoring
 */
export interface HealthThreat {
  threat_id: string;
  title: string;
  urgency: number;  // 0-100
  impact: number;   // 0-100
  category: string;
  description: string;
  mitigation_actions: string[];
}

/**
 * Opportunity with ROI and feasibility scoring
 */
export interface HealthOpportunity {
  opportunity_id: string;
  title: string;
  roi_potential: number;  // 0-100
  feasibility: number;    // 0-100
  category: string;
  description: string;
  quick_wins: string[];
}

/**
 * Competitive position summary for mini-map
 */
export interface CompetitivePositionSummary {
  x_coordinate: number;
  y_coordinate: number;
  market_share_percentile: number;  // 0-100
  competitive_strength: 'leader' | 'challenger' | 'follower' | 'at-risk';
}

/**
 * Overall strategic health assessment
 */
export interface StrategicHealthData {
  overall_health: number;  // 0-100
  health_trend: number;    // delta from last assessment
  last_updated: string;
  top_threats: HealthThreat[];
  top_opportunities: HealthOpportunity[];
  competitive_position: CompetitivePositionSummary;
  risk_trend_30d: {
    date: string;
    risk_score: number;
  }[];
  category_breakdown: {
    market_position: number;
    innovation_capacity: number;
    operational_efficiency: number;
    financial_health: number;
  };
}

interface StrategicHealthDashboardProps {
  data: StrategicHealthData;
  onThreatAction?: (threatId: string, action: string) => void;
  onOpportunityAction?: (opportunityId: string) => void;
  onRefresh?: () => void;
  className?: string;
}

/**
 * Strategic Health Dashboard Component
 *
 * Executive summary dashboard providing 30-second strategic scan:
 * - Overall strategic health gauge (0-100)
 * - Top 3 threats (urgency × impact)
 * - Top 3 opportunities (ROI × feasibility)
 * - Quick action buttons
 * - 30-day risk trend chart
 * - Competitive position mini-map
 *
 * Designed for busy executives who need immediate strategic awareness.
 *
 * @component
 * @example
 * ```tsx
 * <StrategicHealthDashboard
 *   data={healthData}
 *   onThreatAction={(id, action) => handleThreat(id, action)}
 *   onRefresh={() => refreshData()}
 * />
 * ```
 */
export default function StrategicHealthDashboard({
  data,
  onThreatAction,
  onOpportunityAction,
  onRefresh,
  className = '',
}: StrategicHealthDashboardProps) {
  // Calculate health level and styling
  const healthLevel = useMemo(() => {
    if (data.overall_health >= 80) {
      return {
        label: 'Excellent',
        color: 'text-green-600',
        bgColor: 'bg-green-100',
        strokeColor: '#10b981',
        description: 'Strong strategic position',
      };
    }
    if (data.overall_health >= 60) {
      return {
        label: 'Good',
        color: 'text-blue-600',
        bgColor: 'bg-blue-100',
        strokeColor: '#3b82f6',
        description: 'Stable with opportunities',
      };
    }
    if (data.overall_health >= 40) {
      return {
        label: 'Fair',
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-100',
        strokeColor: '#f59e0b',
        description: 'Attention required',
      };
    }
    return {
      label: 'At Risk',
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      strokeColor: '#ef4444',
      description: 'Immediate action needed',
    };
  }, [data.overall_health]);

  // Sort threats by urgency × impact
  const topThreats = useMemo(() => {
    return [...data.top_threats]
      .sort((a, b) => (b.urgency * b.impact) - (a.urgency * a.impact))
      .slice(0, 3);
  }, [data.top_threats]);

  // Sort opportunities by ROI × feasibility
  const topOpportunities = useMemo(() => {
    return [...data.top_opportunities]
      .sort((a, b) => (b.roi_potential * b.feasibility) - (a.roi_potential * a.feasibility))
      .slice(0, 3);
  }, [data.top_opportunities]);

  // Competitive position styling
  const getCompetitivePositionStyle = (strength: string) => {
    switch (strength) {
      case 'leader':
        return { color: 'text-green-800', bgColor: 'bg-green-100', icon: '👑' };
      case 'challenger':
        return { color: 'text-blue-800', bgColor: 'bg-blue-100', icon: '⚔️' };
      case 'follower':
        return { color: 'text-yellow-800', bgColor: 'bg-yellow-100', icon: '🏃' };
      default:
        return { color: 'text-red-800', bgColor: 'bg-red-100', icon: '⚠️' };
    }
  };

  const competitiveStyle = getCompetitivePositionStyle(data.competitive_position.competitive_strength);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Strategic Health Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            Last updated: {new Date(data.last_updated).toLocaleString()}
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Health Gauge + Breakdown */}
        <div className="space-y-6">
          {/* Health Gauge */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6 text-center">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Overall Strategic Health</h3>

            {/* Circular Gauge */}
            <div className="relative w-48 h-48 mx-auto mb-4">
              <svg className="w-full h-full transform -rotate-90">
                {/* Background circle */}
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="16"
                />
                {/* Progress circle */}
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  fill="none"
                  stroke={healthLevel.strokeColor}
                  strokeWidth="16"
                  strokeDasharray={`${(data.overall_health / 100) * 502.4} 502.4`}
                  strokeLinecap="round"
                  className="transition-all duration-1000"
                />
              </svg>

              {/* Center text */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className={`text-5xl font-bold ${healthLevel.color}`}>
                  {data.overall_health.toFixed(0)}
                </div>
                <div className="text-sm text-gray-500">/ 100</div>
              </div>
            </div>

            <div className={`inline-flex items-center px-4 py-2 rounded-lg ${healthLevel.bgColor} mb-2`}>
              <span className={`font-semibold ${healthLevel.color}`}>{healthLevel.label}</span>
            </div>
            <p className="text-sm text-gray-600">{healthLevel.description}</p>

            {/* Trend Indicator */}
            {data.health_trend !== 0 && (
              <div className={`mt-3 flex items-center justify-center gap-2 ${data.health_trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                <svg className={`w-5 h-5 ${data.health_trend > 0 ? '' : 'rotate-180'}`} fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium">
                  {Math.abs(data.health_trend).toFixed(1)} points
                </span>
              </div>
            )}
          </div>

          {/* Category Breakdown */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Health Breakdown</h3>
            <div className="space-y-3">
              {Object.entries(data.category_breakdown).map(([key, value]) => {
                const label = key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                const color = value >= 70 ? 'bg-green-500' : value >= 40 ? 'bg-yellow-500' : 'bg-red-500';

                return (
                  <div key={key}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-600">{label}</span>
                      <span className="text-xs font-medium text-gray-900">{value.toFixed(0)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${color} transition-all duration-500`}
                        style={{ width: `${value}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Competitive Position Mini-Map */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Competitive Position</h3>
            <div className={`flex items-center gap-3 p-3 rounded-lg ${competitiveStyle.bgColor}`}>
              <div className="text-3xl">{competitiveStyle.icon}</div>
              <div className="flex-1">
                <div className={`font-semibold ${competitiveStyle.color} capitalize`}>
                  {data.competitive_position.competitive_strength}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  Market Share: Top {data.competitive_position.market_share_percentile.toFixed(0)}%
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Middle Column: Threats */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">Top Threats</h3>
            <span className="text-xs text-gray-500">Urgency × Impact</span>
          </div>

          {topThreats.length === 0 ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
              <svg className="w-12 h-12 mx-auto text-green-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-green-800 font-medium">No critical threats</p>
            </div>
          ) : (
            topThreats.map((threat, idx) => {
              const score = (threat.urgency * threat.impact) / 100;
              const severity = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low';
              const severityStyles = {
                high: { border: 'border-red-500', bg: 'bg-red-50', text: 'text-red-900', badge: 'bg-red-600' },
                medium: { border: 'border-yellow-500', bg: 'bg-yellow-50', text: 'text-yellow-900', badge: 'bg-yellow-600' },
                low: { border: 'border-blue-500', bg: 'bg-blue-50', text: 'text-blue-900', badge: 'bg-blue-600' },
              }[severity];

              return (
                <div key={threat.threat_id} className={`border-l-4 ${severityStyles.border} ${severityStyles.bg} rounded-lg p-4`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-6 h-6 ${severityStyles.badge} text-white rounded-full flex items-center justify-center text-xs font-bold`}>
                        {idx + 1}
                      </div>
                      <h4 className={`font-semibold ${severityStyles.text}`}>{threat.title}</h4>
                    </div>
                    <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">
                      {threat.category}
                    </span>
                  </div>

                  <p className="text-sm text-gray-700 mb-3">{threat.description}</p>

                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Urgency</div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="h-2 bg-orange-500 rounded-full" style={{ width: `${threat.urgency}%` }} />
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Impact</div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="h-2 bg-red-500 rounded-full" style={{ width: `${threat.impact}%` }} />
                      </div>
                    </div>
                  </div>

                  {threat.mitigation_actions.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {threat.mitigation_actions.slice(0, 2).map((action, aIdx) => (
                        <button
                          key={aIdx}
                          onClick={() => onThreatAction?.(threat.threat_id, action)}
                          className="px-3 py-1 text-xs bg-white border border-gray-300 rounded hover:border-blue-500 hover:text-blue-600"
                        >
                          {action}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Opportunities */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">Top Opportunities</h3>
            <span className="text-xs text-gray-500">ROI × Feasibility</span>
          </div>

          {topOpportunities.length === 0 ? (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
              <p className="text-gray-500">No opportunities identified</p>
            </div>
          ) : (
            topOpportunities.map((opp, idx) => {
              const score = (opp.roi_potential * opp.feasibility) / 100;
              const priority = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low';
              const priorityStyles = {
                high: { border: 'border-green-500', bg: 'bg-green-50', text: 'text-green-900', badge: 'bg-green-600' },
                medium: { border: 'border-blue-500', bg: 'bg-blue-50', text: 'text-blue-900', badge: 'bg-blue-600' },
                low: { border: 'border-gray-500', bg: 'bg-gray-50', text: 'text-gray-900', badge: 'bg-gray-600' },
              }[priority];

              return (
                <div key={opp.opportunity_id} className={`border-l-4 ${priorityStyles.border} ${priorityStyles.bg} rounded-lg p-4`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-6 h-6 ${priorityStyles.badge} text-white rounded-full flex items-center justify-center text-xs font-bold`}>
                        {idx + 1}
                      </div>
                      <h4 className={`font-semibold ${priorityStyles.text}`}>{opp.title}</h4>
                    </div>
                    <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">
                      {opp.category}
                    </span>
                  </div>

                  <p className="text-sm text-gray-700 mb-3">{opp.description}</p>

                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <div>
                      <div className="text-xs text-gray-600 mb-1">ROI Potential</div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="h-2 bg-green-500 rounded-full" style={{ width: `${opp.roi_potential}%` }} />
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Feasibility</div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="h-2 bg-blue-500 rounded-full" style={{ width: `${opp.feasibility}%` }} />
                      </div>
                    </div>
                  </div>

                  {opp.quick_wins.length > 0 && (
                    <div>
                      <div className="text-xs font-semibold text-gray-700 mb-1">Quick Wins:</div>
                      <ul className="text-xs text-gray-600 space-y-1">
                        {opp.quick_wins.slice(0, 2).map((win, wIdx) => (
                          <li key={wIdx} className="flex items-start gap-1">
                            <span className="text-green-600 mt-0.5">✓</span>
                            <span>{win}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <button
                    onClick={() => onOpportunityAction?.(opp.opportunity_id)}
                    className="mt-3 w-full px-3 py-2 text-sm bg-white border border-gray-300 rounded hover:bg-blue-50 hover:border-blue-500 hover:text-blue-600 font-medium"
                  >
                    Explore Opportunity
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Risk Trend Chart */}
      <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Risk Trend (30 Days)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data.risk_trend_30d}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              tick={{ fill: '#6b7280', fontSize: 11 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: '#6b7280', fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ fontSize: 12 }}
              labelFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <Line
              type="monotone"
              dataKey="risk_score"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
