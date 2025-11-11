'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import SystemDynamicsMap from '@/app/components/SystemDynamicsMap';
import FlywheelDashboard from '@/app/components/FlywheelDashboard';
import IntelligenceFeed from '@/app/components/IntelligenceFeed';
import {
  StrategicIntelligenceOverview,
  ExecutiveBrief,
  StrategicThreat,
  StrategicOpportunity,
  DecisionCard,
  StrategicContext,
} from '@/types/strategic-intelligence';

type ViewLayer = 'executive' | 'context' | 'evidence';
type ContextTab = 'positioning' | 'disruption' | 'dynamics' | 'momentum' | 'decisions';

const StrategicIntelligenceDashboard: React.FC = () => {
  const [activeLayer, setActiveLayer] = useState<ViewLayer>('executive');
  const [activeTab, setActiveTab] = useState<ContextTab>('positioning');
  const [data, setData] = useState<StrategicIntelligenceOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch data from API
    fetchStrategicIntelligence();
  }, []);

  const fetchStrategicIntelligence = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to fetch real data from API
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
        // TODO: Get monitor_id from user context or URL params
        // For now, try to fetch from a test monitor or use demo data
        const monitorId = 'demo-monitor'; // Replace with actual monitor selection

        const response = await fetch(`${apiUrl}/strategic-intelligence/overview/${monitorId}`, {
          headers: {
            'Content-Type': 'application/json',
            // Add API key if available
            ...(localStorage.getItem('api_key') && {
              'X-API-Key': localStorage.getItem('api_key') || ''
            })
          }
        });

        if (!response.ok) {
          throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }

        const apiData = await response.json();

        // Transform API data to match frontend interface
        const transformedData = transformApiDataToUI(apiData);
        setData(transformedData);

      } catch (apiError) {
        console.warn('Failed to fetch from API, falling back to demo data:', apiError);
        // Fall back to demo data if API fails
        setData(generateDemoData());
      }

      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setLoading(false);
    }
  };

  const transformApiDataToUI = (apiData: any): StrategicIntelligenceOverview => {
    // Transform backend API data to frontend UI format
    return {
      executive_brief: {
        strategic_health_score: apiData.strategic_health_score || 50,
        trend: apiData.health_trend === 'improving' ? 'up' : apiData.health_trend === 'declining' ? 'down' : 'stable',
        top_threats: (apiData.top_threats || []).slice(0, 3).map((threat: string, idx: number) => ({
          id: `threat-${idx}`,
          title: threat,
          severity: 70 - (idx * 10), // Decreasing severity
          category: 'strategic' as const,
          source: 'Strategic Analysis',
          timeline_months: 6 + (idx * 3),
          mitigation_available: idx === 0,
          details: threat,
        })),
        top_opportunities: (apiData.top_opportunities || []).slice(0, 3).map((opp: string, idx: number) => ({
          id: `opp-${idx}`,
          title: opp,
          value_score: 85 - (idx * 10),
          category: 'strategic' as const,
          estimated_value: 40000000 - (idx * 10000000),
          timeframe_months: 6 + (idx * 3),
          roi_estimate: 3.0 - (idx * 0.3),
          requirements: ['Strategic planning', 'Resource allocation'],
          details: opp,
        })),
        decisions_required: apiData.critical_decision ? [{
          id: 'decision-1',
          title: 'Critical Strategic Decision',
          urgency_days: 30,
          impact_value: 5000000,
          category: 'strategic' as const,
          options: [
            {
              option_id: 'a',
              title: apiData.critical_decision,
              pros: ['Addresses urgent need', 'High impact potential'],
              cons: ['Requires immediate action', 'Resource intensive'],
              estimated_cost: 1000000,
              expected_outcome: 'Resolved strategic issue',
              risk_level: 'medium' as const,
              implementation_time_days: 90,
            },
          ],
          recommendation: apiData.critical_decision,
          decision_deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          status: 'pending' as const,
        }] : [],
        last_updated: apiData.generated_at || new Date().toISOString(),
      },
      strategic_context: generateDemoData().strategic_context, // Use demo context for now
      intelligence_feed: {
        cards: [],
        unread_count: 0,
        last_updated: new Date().toISOString(),
      },
      company: apiData.company || 'Unknown',
      industry: apiData.industry || 'Unknown',
      analysis_date: apiData.generated_at || new Date().toISOString(),
    };
  };

  const handleDecisionAction = (decisionId: string, action: 'accept' | 'view') => {
    console.log(`Decision ${decisionId}: ${action}`);
    // Implement decision handling logic
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading Strategic Intelligence...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-red-600">
          <p className="text-xl font-semibold mb-2">Error Loading Data</p>
          <p>{error || 'No data available'}</p>
          <button
            onClick={fetchStrategicIntelligence}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Strategic Intelligence</h1>
              <p className="text-sm text-gray-600 mt-1">
                {data.company} • {data.industry} • {new Date(data.analysis_date).toLocaleDateString()}
              </p>
            </div>

            <button
              onClick={fetchStrategicIntelligence}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              🔄 Refresh
            </button>
          </div>

          {/* Layer Navigation */}
          <div className="flex gap-2">
            <button
              onClick={() => setActiveLayer('executive')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeLayer === 'executive'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              📊 Executive Brief
            </button>
            <button
              onClick={() => setActiveLayer('context')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeLayer === 'context'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🧭 Strategic Context
            </button>
            <button
              onClick={() => setActiveLayer('evidence')}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                activeLayer === 'evidence'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              📁 Supporting Evidence
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <AnimatePresence mode="wait">
          {activeLayer === 'executive' && (
            <ExecutiveBriefLayer
              key="executive"
              brief={data.executive_brief}
              onDecisionAction={handleDecisionAction}
            />
          )}

          {activeLayer === 'context' && (
            <StrategicContextLayer
              key="context"
              context={data.strategic_context}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />
          )}

          {activeLayer === 'evidence' && (
            <SupportingEvidenceLayer
              key="evidence"
              context={data.strategic_context}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// ============================================================================
// Executive Brief Layer (30-second view)
// ============================================================================

const ExecutiveBriefLayer: React.FC<{
  brief: ExecutiveBrief;
  onDecisionAction: (decisionId: string, action: 'accept' | 'view') => void;
}> = ({ brief, onDecisionAction }) => {
  const getHealthColor = (score: number): string => {
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrendIcon = (trend: string): string => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '→';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Strategic Health Score */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Strategic Health</h2>
            <div className="flex items-center gap-3">
              <span className={`text-5xl font-bold ${getHealthColor(brief.strategic_health_score)}`}>
                {brief.strategic_health_score}/100
              </span>
              <span className="text-3xl">{getTrendIcon(brief.trend)}</span>
            </div>
          </div>
          <div className="text-right text-sm text-gray-500">
            Last updated: {new Date(brief.last_updated).toLocaleString()}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Threats */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            ⚠️ TOP THREATS
          </h2>
          <div className="space-y-3">
            {brief.top_threats.slice(0, 3).map((threat, idx) => (
              <div key={threat.id} className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">
                      {idx + 1}. {threat.title}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">{threat.source}</p>
                  </div>
                  <span className="text-2xl font-bold text-red-600">{threat.severity}/100</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-600">
                  <span>Timeline: {threat.timeline_months}mo</span>
                  <span className="capitalize">{threat.category}</span>
                  {threat.mitigation_available && (
                    <span className="text-green-600">✓ Mitigation available</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Opportunities */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            💰 TOP OPPORTUNITIES
          </h2>
          <div className="space-y-3">
            {brief.top_opportunities.slice(0, 3).map((opp, idx) => (
              <div key={opp.id} className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">
                      {idx + 1}. {opp.title}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1 capitalize">{opp.category}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">
                      ${(opp.estimated_value / 1000000).toFixed(1)}M
                    </div>
                    <div className="text-xs text-gray-600">{opp.roi_estimate.toFixed(1)}x ROI</div>
                  </div>
                </div>
                <div className="text-xs text-gray-600">
                  Timeframe: {opp.timeframe_months} months
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Decisions Required */}
      {brief.decisions_required.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            🎯 DECISION REQUIRED
          </h2>
          <div className="space-y-4">
            {brief.decisions_required.map((decision) => (
              <div
                key={decision.id}
                className="bg-purple-50 border-2 border-purple-300 rounded-lg p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{decision.title}</h3>
                    <p className="text-sm text-gray-700 mb-3">{decision.recommendation}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="font-medium text-red-600">
                        Urgency: {decision.urgency_days} days
                      </span>
                      <span className="font-medium text-green-600">
                        Impact: ${(decision.impact_value / 1000000).toFixed(1)}M
                      </span>
                      <span className="capitalize text-gray-600">{decision.category}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => onDecisionAction(decision.id, 'accept')}
                    className="flex-1 bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition-colors font-medium"
                  >
                    Accept Recommendation
                  </button>
                  <button
                    onClick={() => onDecisionAction(decision.id, 'view')}
                    className="flex-1 bg-white text-gray-700 border-2 border-gray-300 py-3 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                  >
                    View Options
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

// ============================================================================
// Strategic Context Layer (5-minute exploration)
// ============================================================================

const StrategicContextLayer: React.FC<{
  context: StrategicContext;
  activeTab: ContextTab;
  onTabChange: (tab: ContextTab) => void;
}> = ({ context, activeTab, onTabChange }) => {
  const tabs: Array<{ id: ContextTab; label: string; icon: string }> = [
    { id: 'positioning', label: 'Positioning', icon: '📍' },
    { id: 'disruption', label: 'Disruption', icon: '⚡' },
    { id: 'dynamics', label: 'Dynamics', icon: '🔄' },
    { id: 'momentum', label: 'Momentum', icon: '🎯' },
    { id: 'decisions', label: 'Decisions', icon: '🎲' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-lg p-2 flex gap-2 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'positioning' && (
          <PositioningTab key="positioning" positioning={context.positioning} />
        )}
        {activeTab === 'disruption' && (
          <DisruptionTab key="disruption" disruption={context.disruption} />
        )}
        {activeTab === 'dynamics' && (
          <DynamicsTab key="dynamics" dynamics={context.dynamics} />
        )}
        {activeTab === 'momentum' && (
          <MomentumTab key="momentum" momentum={context.momentum} />
        )}
        {activeTab === 'decisions' && (
          <DecisionsTab key="decisions" decisions={context.decisions} />
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const PositioningTab: React.FC<{ positioning: any }> = ({ positioning }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    className="bg-white rounded-lg shadow-lg p-6"
  >
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Competitive Positioning</h2>
    <div className="grid grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Porter's Five Forces</h3>
        {Object.entries(positioning.porter_five_forces).map(([key, value]) => (
          <div key={key} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="capitalize">{key.replace(/_/g, ' ')}</span>
              <span className="font-medium">{(value as number * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${(value as number) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Strategic Metrics</h3>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Blue Ocean Score</div>
          <div className="text-3xl font-bold text-blue-600">{positioning.blue_ocean_score}/100</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Differentiation Strength</div>
          <div className="text-3xl font-bold text-purple-600">{positioning.differentiation_strength}/100</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Competitive Moat</div>
          <div className="text-3xl font-bold text-green-600">{positioning.competitive_moat_strength}/100</div>
        </div>
      </div>
    </div>
  </motion.div>
);

const DisruptionTab: React.FC<{ disruption: any }> = ({ disruption }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    className="bg-white rounded-lg shadow-lg p-6"
  >
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Disruption Analysis</h2>
    <div className="mb-6">
      <div className="text-center mb-4">
        <div className="text-6xl font-bold text-red-600">{disruption.overall_risk}/100</div>
        <div className="text-gray-600">Overall Disruption Risk</div>
      </div>
    </div>
    <div className="space-y-4">
      {disruption.disruptors.map((disruptor: any, idx: number) => (
        <div key={idx} className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-gray-900">{disruptor.name}</h3>
            <span className="text-red-600 font-bold">{disruptor.threat_level}/100</span>
          </div>
          <div className="flex gap-4 text-sm text-gray-600">
            <span>Growth: {disruptor.growth_rate}%</span>
            <span>Impact: {disruptor.time_to_impact_months}mo</span>
          </div>
        </div>
      ))}
    </div>
  </motion.div>
);

const DynamicsTab: React.FC<{ dynamics: any }> = ({ dynamics }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
  >
    <SystemDynamicsMap data={dynamics} height={600} width={1000} simulationEnabled />
  </motion.div>
);

const MomentumTab: React.FC<{ momentum: any }> = ({ momentum }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
  >
    <FlywheelDashboard velocity={momentum} />
  </motion.div>
);

const DecisionsTab: React.FC<{ decisions: DecisionCard[] }> = ({ decisions }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    className="space-y-4"
  >
    {decisions.map((decision) => (
      <div key={decision.id} className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">{decision.title}</h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          {decision.options.map((option) => (
            <div key={option.option_id} className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">{option.title}</h4>
              <div className="text-sm space-y-1">
                <div className="text-green-600">
                  Pros: {option.pros.slice(0, 2).join(', ')}
                </div>
                <div className="text-red-600">
                  Cons: {option.cons.slice(0, 2).join(', ')}
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="font-medium text-gray-900 mb-2">Recommendation</div>
          <p className="text-gray-700">{decision.recommendation}</p>
        </div>
      </div>
    ))}
  </motion.div>
);

// ============================================================================
// Supporting Evidence Layer (on-demand)
// ============================================================================

const SupportingEvidenceLayer: React.FC<{ context: StrategicContext }> = ({ context }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="space-y-6"
  >
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Supporting Evidence</h2>
      <p className="text-gray-600">
        Raw framework analyses, source data, confidence intervals, and export options would be displayed here.
      </p>
      <div className="mt-6 flex gap-3">
        <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
          📄 Export PDF
        </button>
        <button className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium">
          📊 Export Excel
        </button>
        <button className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
          🔌 API Access
        </button>
      </div>
    </div>
  </motion.div>
);

// ============================================================================
// Demo Data Generator
// ============================================================================

function generateDemoData(): StrategicIntelligenceOverview {
  return {
    executive_brief: {
      strategic_health_score: 67,
      trend: 'down',
      top_threats: [
        {
          id: '1',
          title: 'Disruption Risk from Startup X',
          severity: 73,
          category: 'disruption',
          source: 'Startup X',
          timeline_months: 6,
          mitigation_available: true,
          details: 'Rapidly growing competitor targeting same market segment',
        },
        {
          id: '2',
          title: 'Position Threat: Rivian entering luxury EV segment',
          severity: 68,
          category: 'position',
          source: 'Market Analysis',
          timeline_months: 12,
          mitigation_available: false,
          details: 'Direct competitive threat to premium positioning',
        },
        {
          id: '3',
          title: 'Margin Pressure from Negative Feedback Loop',
          severity: 55,
          category: 'financial',
          source: 'System Dynamics Analysis',
          timeline_months: 18,
          mitigation_available: true,
          details: 'Price competition driving down margins',
        },
      ],
      top_opportunities: [
        {
          id: '1',
          title: 'Geographic Expansion: Seattle Market',
          value_score: 85,
          category: 'geographic',
          estimated_value: 41000000,
          timeframe_months: 12,
          roi_estimate: 2.3,
          requirements: ['Market research', 'Distribution setup', 'Local partnerships'],
          details: 'Untapped market with high demand',
        },
        {
          id: '2',
          title: 'Flywheel Acceleration Opportunity',
          value_score: 78,
          category: 'flywheel',
          estimated_value: 28000000,
          timeframe_months: 6,
          roi_estimate: 3.1,
          requirements: ['Investment in momentum drivers', 'Strategic alignment'],
          details: 'System entering acceleration phase',
        },
        {
          id: '3',
          title: 'Blue Ocean: Feature Elimination Strategy',
          value_score: 72,
          category: 'innovation',
          estimated_value: 15000000,
          timeframe_months: 9,
          roi_estimate: 2.8,
          requirements: ['Product redesign', 'Market repositioning'],
          details: 'Eliminate costly features for simplified offering',
        },
      ],
      decisions_required: [
        {
          id: '1',
          title: 'Supplier Risk Mitigation Strategy',
          urgency_days: 45,
          impact_value: 4200000,
          category: 'strategic',
          options: [
            {
              option_id: 'a',
              title: 'Diversify supplier base',
              pros: ['Reduced risk', 'Better negotiation position'],
              cons: ['Higher costs', 'Complexity'],
              estimated_cost: 500000,
              expected_outcome: 'Lower supply chain risk',
              risk_level: 'medium',
              implementation_time_days: 90,
            },
            {
              option_id: 'b',
              title: 'Vertical integration',
              pros: ['Full control', 'Long-term savings'],
              cons: ['High upfront cost', 'Operational complexity'],
              estimated_cost: 2000000,
              expected_outcome: 'Complete supply chain ownership',
              risk_level: 'high',
              implementation_time_days: 180,
            },
          ],
          recommendation: 'Diversify supplier base with staged approach',
          decision_deadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000).toISOString(),
          status: 'pending',
        },
      ],
      last_updated: new Date().toISOString(),
    },
    strategic_context: {
      positioning: {
        porter_five_forces: {
          competitive_rivalry: 0.75,
          supplier_power: 0.45,
          buyer_power: 0.6,
          threat_of_substitution: 0.55,
          threat_of_new_entry: 0.7,
        },
        blue_ocean_score: 42,
        differentiation_strength: 68,
        market_share_trend: [10, 12, 15, 18, 19, 20, 21, 22, 23, 23.5],
        competitive_moat_strength: 55,
      },
      disruption: {
        overall_risk: 68,
        disruptors: [
          {
            name: 'TechDisruptor Inc',
            threat_level: 75,
            growth_rate: 340,
            time_to_impact_months: 8,
          },
          {
            name: 'AI Solutions Co',
            threat_level: 62,
            growth_rate: 210,
            time_to_impact_months: 14,
          },
        ],
        innovation_pace: 0.72,
        market_maturity: 'growth' as const,
      },
      dynamics: {
        nodes: [
          { id: '1', metric: 'Price', value: 85, trend: 'down' as const, category: 'financial' },
          { id: '2', metric: 'Sentiment', value: 72, trend: 'stable' as const, category: 'market' },
          { id: '3', metric: 'Market Share', value: 23.5, trend: 'up' as const, category: 'market' },
          { id: '4', metric: 'Revenue', value: 150, trend: 'up' as const, category: 'financial' },
          { id: '5', metric: 'Cost', value: 95, trend: 'up' as const, category: 'operational' },
        ],
        links: [
          {
            from_metric: 'Price',
            to_metric: 'Sentiment',
            correlation: -0.7,
            time_delay_days: 7,
            relationship_type: 'negative' as const,
          },
          {
            from_metric: 'Sentiment',
            to_metric: 'Market Share',
            correlation: 0.8,
            time_delay_days: 14,
            relationship_type: 'positive' as const,
          },
          {
            from_metric: 'Market Share',
            to_metric: 'Revenue',
            correlation: 0.9,
            time_delay_days: 30,
            relationship_type: 'positive' as const,
          },
        ],
        feedback_loops: [
          {
            loop_id: 'Loop-1',
            loop_type: 'Reinforcing' as const,
            nodes: ['Price', 'Sentiment', 'Market Share', 'Revenue'],
            links: [],
            loop_strength: 0.75,
            cycle_time_days: 60,
            description: 'Growth reinforcing loop',
          },
        ],
        leverage_points: [
          {
            intervention: 'Price optimization program',
            impact_score: 8.5,
            node: 'Price',
            expected_outcome: 'Improved margins without sentiment impact',
            cost_estimate: 250000,
            roi: 4.2,
          },
        ],
      },
      momentum: {
        overall_score: 67,
        market_momentum: 72,
        financial_momentum: 65,
        strategic_momentum: 68,
        execution_momentum: 70,
        talent_momentum: 60,
        phase: 'Building' as const,
        phase_confidence: 0.82,
        historical_matches: [
          {
            company: 'Salesforce',
            time_period: '2008-2010',
            match_confidence: 0.78,
            outcome: 'Successful transition to market leader',
            similarity_factors: ['Strong execution', 'Market positioning', 'Talent retention'],
            outcome_timeframe_months: 24,
          },
        ],
        prediction: 'Expected to enter Accelerating phase within 6 months',
        inflection_points: [
          {
            date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
            metric: 'Market Momentum',
            threshold_crossed: 70,
            significance: 'major' as const,
            strategic_note: 'Crossed critical growth threshold',
          },
        ],
        components: [
          {
            name: 'Market',
            score: 72,
            trend_data: Array.from({ length: 90 }, (_, i) => 50 + i * 0.25),
            acceleration: 'moderate_up' as const,
            key_drivers: ['Customer acquisition', 'Brand awareness'],
            last_updated: new Date().toISOString(),
          },
          {
            name: 'Financial',
            score: 65,
            trend_data: Array.from({ length: 90 }, (_, i) => 48 + i * 0.2),
            acceleration: 'stable' as const,
            key_drivers: ['Revenue growth', 'Margin improvement'],
            last_updated: new Date().toISOString(),
          },
          {
            name: 'Strategic',
            score: 68,
            trend_data: Array.from({ length: 90 }, (_, i) => 52 + i * 0.18),
            acceleration: 'moderate_up' as const,
            key_drivers: ['Market positioning', 'Competitive advantage'],
            last_updated: new Date().toISOString(),
          },
          {
            name: 'Execution',
            score: 70,
            trend_data: Array.from({ length: 90 }, (_, i) => 55 + i * 0.17),
            acceleration: 'moderate_up' as const,
            key_drivers: ['Operational efficiency', 'Delivery speed'],
            last_updated: new Date().toISOString(),
          },
          {
            name: 'Talent',
            score: 60,
            trend_data: Array.from({ length: 90 }, (_, i) => 45 + i * 0.17),
            acceleration: 'stable' as const,
            key_drivers: ['Retention rate', 'Hiring quality'],
            last_updated: new Date().toISOString(),
          },
        ],
        last_updated: new Date().toISOString(),
      },
      decisions: [],
    },
    intelligence_feed: {
      cards: [],
      unread_count: 0,
      last_updated: new Date().toISOString(),
    },
    company: 'Tesla',
    industry: 'Electric Vehicles',
    analysis_date: new Date().toISOString(),
  };
}

export default StrategicIntelligenceDashboard;
