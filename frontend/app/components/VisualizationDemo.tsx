'use client';

import { useState } from 'react';
import CompetitivePositioningMap from './CompetitivePositioningMap';
import DisruptionRadar from './DisruptionRadar';
import DecisionCard from './DecisionCard';
import StrategicHealthDashboard from './StrategicHealthDashboard';
import type {
  PositioningData,
  DisruptionAssessment,
  StrategicDecision,
  StrategicHealthData,
} from './visualizations';

/**
 * Visualization Demo Component
 *
 * Demonstrates all advanced visualization components with sample data.
 * Use this as a reference for integration patterns and data structures.
 *
 * @component
 */
export default function VisualizationDemo() {
  type DemoId = 'positioning' | 'disruption' | 'decision' | 'health';
  const [activeDemo, setActiveDemo] = useState<DemoId>('health');

  // Sample data for Competitive Positioning Map
  const positioningData: PositioningData = {
    company_position: {
      company: 'Your Company',
      x_coordinate: 15,
      y_coordinate: 25,
      bubble_size: 50000,
      sentiment_color: '#10b981',
      movement_vector: [3, 2],
      velocity: 3.6,
    },
    competitor_positions: [
      {
        company: 'Competitor A',
        x_coordinate: 20,
        y_coordinate: 30,
        bubble_size: 80000,
        sentiment_color: '#3b82f6',
        movement_vector: [2, 1],
        velocity: 2.2,
      },
      {
        company: 'Competitor B',
        x_coordinate: 10,
        y_coordinate: 20,
        bubble_size: 40000,
        sentiment_color: '#f59e0b',
        movement_vector: [-1, 3],
        velocity: 3.2,
      },
      {
        company: 'Competitor C',
        x_coordinate: 25,
        y_coordinate: 35,
        bubble_size: 100000,
        sentiment_color: '#ef4444',
        movement_vector: [1, -2],
        velocity: 2.2,
      },
    ],
    white_space_opportunities: [
      'High-margin, moderate growth segment underserved',
      'Premium market with low competition intensity',
    ],
    position_threats: [
      'Competitor A moving aggressively into your segment',
      'Market commoditization reducing margins',
    ],
    historical_snapshots: [
      {
        timestamp: '3 months ago',
        positions: [
          {
            company: 'Your Company',
            x_coordinate: 12,
            y_coordinate: 23,
            bubble_size: 45000,
            sentiment_color: '#3b82f6',
            movement_vector: [0, 0],
            velocity: 0,
          },
          {
            company: 'Competitor A',
            x_coordinate: 18,
            y_coordinate: 29,
            bubble_size: 75000,
            sentiment_color: '#3b82f6',
            movement_vector: [0, 0],
            velocity: 0,
          },
        ],
      },
      {
        timestamp: 'Current',
        positions: [
          {
            company: 'Your Company',
            x_coordinate: 15,
            y_coordinate: 25,
            bubble_size: 50000,
            sentiment_color: '#10b981',
            movement_vector: [3, 2],
            velocity: 3.6,
          },
          {
            company: 'Competitor A',
            x_coordinate: 20,
            y_coordinate: 30,
            bubble_size: 80000,
            sentiment_color: '#3b82f6',
            movement_vector: [2, 1],
            velocity: 2.2,
          },
        ],
      },
    ],
  };

  // Sample data for Disruption Radar
  const disruptionData: DisruptionAssessment = {
    overall_risk: 62,
    risk_trend: 5.2,
    vulnerability_breakdown: {
      incumbent_overserving: 45,
      asymmetric_threat_velocity: 72,
      technology_shift_momentum: 68,
      customer_job_misalignment: 55,
      business_model_innovation: 50,
    },
    primary_threats: [
      {
        threat_type: 'AI-Powered Automation Disruption',
        severity: 78,
        description: 'New AI-native competitors automating core workflows at 1/10th the cost',
        evidence: [
          'Startup X raised $50M Series B with 300% YoY growth',
          'Customer surveys show 40% would switch for automation',
          'Technology now viable for 80% of use cases',
        ],
        recommended_actions: ['Launch AI pilot program', 'Acquire automation capability', 'Partner with AI provider'],
        timeline: 'immediate',
      },
      {
        threat_type: 'Platform Business Model Shift',
        severity: 65,
        description: 'Marketplace platforms aggregating supply/demand, bypassing traditional channels',
        evidence: [
          'Platform Y achieved $100M GMV in 18 months',
          'Network effects creating winner-take-all dynamics',
        ],
        recommended_actions: ['Build platform strategy', 'Explore strategic partnerships'],
        timeline: '6-months',
      },
    ],
    risk_history: [
      { timestamp: '2025-08-10', overall_risk: 52, dimensions: { incumbent_overserving: 40, asymmetric_threat_velocity: 60, technology_shift_momentum: 55, customer_job_misalignment: 50, business_model_innovation: 45 } },
      { timestamp: '2025-09-10', overall_risk: 57, dimensions: { incumbent_overserving: 42, asymmetric_threat_velocity: 65, technology_shift_momentum: 60, customer_job_misalignment: 52, business_model_innovation: 48 } },
      { timestamp: '2025-10-10', overall_risk: 62, dimensions: { incumbent_overserving: 45, asymmetric_threat_velocity: 72, technology_shift_momentum: 68, customer_job_misalignment: 55, business_model_innovation: 50 } },
    ],
  };

  // Sample data for Decision Card
  const decisionData: StrategicDecision = {
    decision_id: 'dec-001',
    title: 'Market Expansion Strategy',
    description: 'Decide on geographic expansion approach to capture emerging markets',
    urgency_days: 14,
    financial_impact: 5000000,
    category: 'strategic',
    evidence: [
      'Market research shows $50M TAM in target regions',
      'Competitors already establishing presence',
      'Product-market fit validated in pilot cities',
      'Current infrastructure can scale to 3 new markets',
    ],
    options: [
      {
        option_id: 'opt-1',
        title: 'Organic Expansion',
        description: 'Build local teams and operations from scratch in each market',
        financial_impact: 2000000,
        implementation_time: '12-18 months',
        resource_requirements: ['5 local hires per market', 'Marketing budget $500K', 'Operations setup'],
        pros: [
          'Full control over brand and operations',
          'Higher long-term margins',
          'Build proprietary local knowledge',
        ],
        cons: [
          'Slower time to market',
          'Higher upfront investment',
          'Execution risk in unfamiliar markets',
        ],
        risk_level: 'medium',
        confidence: 0.75,
      },
      {
        option_id: 'opt-2',
        title: 'Strategic Partnerships',
        description: 'Partner with established local players for market access',
        financial_impact: 3500000,
        implementation_time: '6-9 months',
        resource_requirements: ['Partnership team (3 people)', 'Legal/contracts', 'Integration support'],
        pros: [
          'Faster market entry',
          'Leverage partner infrastructure',
          'Lower risk and investment',
          'Local market expertise included',
        ],
        cons: [
          'Share revenue with partners',
          'Less operational control',
          'Partner dependency risk',
        ],
        risk_level: 'low',
        confidence: 0.85,
      },
      {
        option_id: 'opt-3',
        title: 'Acquisition Strategy',
        description: 'Acquire smaller local competitors to gain instant market presence',
        financial_impact: 5000000,
        implementation_time: '3-6 months',
        resource_requirements: ['M&A team', 'Integration budget $1M', 'Legal/due diligence'],
        pros: [
          'Immediate market presence',
          'Acquire customer base and talent',
          'Eliminate potential competitor',
        ],
        cons: [
          'Highest upfront cost',
          'Integration complexity',
          'Cultural alignment challenges',
        ],
        risk_level: 'high',
        confidence: 0.65,
      },
    ],
    recommended_option: 'opt-2',
    recommendation_rationale: 'Strategic partnerships offer the optimal balance of speed, risk, and ROI. The 6-9 month timeline addresses competitive urgency while minimizing capital exposure. Partner networks provide proven local expertise that would take years to build organically.',
    implementation_roadmap: [
      {
        phase: 'Partner Selection & Negotiation',
        duration: '6-8 weeks',
        deliverables: [
          'Shortlist 3-5 qualified partners per market',
          'Complete due diligence and capability assessment',
          'Negotiate partnership terms and agreements',
        ],
      },
      {
        phase: 'Integration & Launch Prep',
        duration: '8-10 weeks',
        deliverables: [
          'Integrate systems and processes',
          'Train partner teams on products/services',
          'Develop go-to-market strategy',
        ],
      },
      {
        phase: 'Market Launch',
        duration: '4-6 weeks',
        deliverables: [
          'Execute coordinated launch in all markets',
          'Monitor KPIs and customer feedback',
          'Optimize based on early results',
        ],
      },
    ],
  };

  // Sample data for Strategic Health Dashboard
  const healthData: StrategicHealthData = {
    overall_health: 72,
    health_trend: 3.5,
    last_updated: new Date().toISOString(),
    top_threats: [
      {
        threat_id: 'thr-1',
        title: 'Emerging AI-Native Competitor',
        urgency: 85,
        impact: 75,
        category: 'Competitive',
        description: 'New entrant leveraging AI to automate core workflows at significantly lower cost',
        mitigation_actions: ['Accelerate AI integration', 'Launch competitive response'],
      },
      {
        threat_id: 'thr-2',
        title: 'Customer Churn Trend',
        urgency: 70,
        impact: 80,
        category: 'Customer',
        description: 'Uptick in customer churn due to pricing pressure and feature gaps',
        mitigation_actions: ['Enhance value proposition', 'Conduct win-back campaign'],
      },
      {
        threat_id: 'thr-3',
        title: 'Regulatory Changes',
        urgency: 60,
        impact: 65,
        category: 'Regulatory',
        description: 'Proposed regulations could increase compliance costs by 30%',
        mitigation_actions: ['Engage policy team', 'Build compliance roadmap'],
      },
    ],
    top_opportunities: [
      {
        opportunity_id: 'opp-1',
        title: 'Adjacent Market Expansion',
        roi_potential: 90,
        feasibility: 75,
        category: 'Growth',
        description: 'High-margin adjacent market with low competitive intensity',
        quick_wins: ['Leverage existing customer base', 'Minimal product adaptation needed'],
      },
      {
        opportunity_id: 'opp-2',
        title: 'Strategic Partnership',
        roi_potential: 80,
        feasibility: 85,
        category: 'Partnership',
        description: 'Partnership with complementary platform for cross-selling',
        quick_wins: ['Pilot program in 30 days', 'No integration required'],
      },
      {
        opportunity_id: 'opp-3',
        title: 'Process Automation',
        roi_potential: 70,
        feasibility: 90,
        category: 'Efficiency',
        description: 'Automate manual workflows to reduce costs by 25%',
        quick_wins: ['RPA for invoice processing', 'AI for customer support'],
      },
    ],
    competitive_position: {
      x_coordinate: 15,
      y_coordinate: 25,
      market_share_percentile: 35,
      competitive_strength: 'challenger',
    },
    risk_trend_30d: [
      { date: '2025-10-10', risk_score: 35 },
      { date: '2025-10-15', risk_score: 32 },
      { date: '2025-10-20', risk_score: 30 },
      { date: '2025-10-25', risk_score: 28 },
      { date: '2025-10-30', risk_score: 25 },
      { date: '2025-11-04', risk_score: 27 },
      { date: '2025-11-09', risk_score: 28 },
    ],
    category_breakdown: {
      market_position: 68,
      innovation_capacity: 75,
      operational_efficiency: 72,
      financial_health: 73,
    },
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Strategic Intelligence Visualizations
          </h1>
          <p className="text-gray-600">
            Advanced visualization components for real-time strategic insights
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'health', label: 'Strategic Health', icon: '🎯' },
              { id: 'positioning', label: 'Competitive Map', icon: '🗺️' },
              { id: 'disruption', label: 'Disruption Radar', icon: '📡' },
              { id: 'decision', label: 'Decision Card', icon: '🎴' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  if (tab.id === 'health' || tab.id === 'positioning' || tab.id === 'disruption' || tab.id === 'decision') {
                    setActiveDemo(tab.id);
                  }
                }}
                className={`${
                  activeDemo === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Demo Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {activeDemo === 'positioning' && (
            <CompetitivePositioningMap
              data={positioningData}
              onCompanyClick={(company) => console.log('Clicked:', company)}
            />
          )}

          {activeDemo === 'disruption' && (
            <DisruptionRadar
              data={disruptionData}
              onActionClick={(action, threat) =>
                console.log('Action:', action, 'for threat:', threat.threat_type)
              }
            />
          )}

          {activeDemo === 'decision' && (
            <DecisionCard
              decision={decisionData}
              onAccept={(decisionId, optionId) =>
                console.log('Accepted:', decisionId, 'with option:', optionId)
              }
              onDefer={(decisionId, days) =>
                console.log('Deferred:', decisionId, 'for', days, 'days')
              }
              onCustomize={(decisionId) =>
                console.log('Customize:', decisionId)
              }
            />
          )}

          {activeDemo === 'health' && (
            <StrategicHealthDashboard
              data={healthData}
              onThreatAction={(threatId, action) =>
                console.log('Threat action:', action, 'for:', threatId)
              }
              onOpportunityAction={(oppId) =>
                console.log('Explore opportunity:', oppId)
              }
              onRefresh={() => console.log('Refresh data')}
            />
          )}
        </div>

        {/* Documentation */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-3">Integration Guide</h2>
          <div className="text-sm text-blue-800 space-y-2">
            <p>
              <strong>Import:</strong> <code className="bg-blue-100 px-2 py-1 rounded">
                import {'{'} CompetitivePositioningMap {'}'} from '@/app/components/CompetitivePositioningMap'
              </code>
            </p>
            <p>
              <strong>Data Source:</strong> Connect to backend agents for real-time data updates
            </p>
            <p>
              <strong>WebSocket:</strong> Use polling or WebSocket for live updates every 30 seconds
            </p>
            <p>
              <strong>Accessibility:</strong> All components meet WCAG AA standards with keyboard navigation
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
