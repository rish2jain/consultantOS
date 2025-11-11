/**
 * Verification Script for Advanced Visualization Components
 *
 * This file verifies that all visualization components and their types
 * can be imported correctly. Run with TypeScript compiler to verify.
 *
 * Usage: npx tsc --noEmit verify-visualizations.ts
 */

import type {
  CompetitivePosition,
  PositioningData,
  DisruptionThreat,
  DisruptionAssessment,
  DecisionOption,
  StrategicDecision,
  HealthThreat,
  HealthOpportunity,
  CompetitivePositionSummary,
  StrategicHealthData,
} from './index';

// Type verification - these should all compile without errors
const sampleCompetitivePosition: CompetitivePosition = {
  company: 'Test Company',
  x_coordinate: 15,
  y_coordinate: 25,
  bubble_size: 50000,
  sentiment_color: '#10b981',
  movement_vector: [3, 2],
  velocity: 3.6,
};

const samplePositioningData: PositioningData = {
  company_position: sampleCompetitivePosition,
  competitor_positions: [sampleCompetitivePosition],
  white_space_opportunities: ['Test opportunity'],
  position_threats: ['Test threat'],
};

const sampleDisruptionThreat: DisruptionThreat = {
  threat_type: 'Test Threat',
  severity: 75,
  description: 'Test description',
  evidence: ['Evidence 1', 'Evidence 2'],
  recommended_actions: ['Action 1', 'Action 2'],
  timeline: 'immediate',
};

const sampleDisruptionAssessment: DisruptionAssessment = {
  overall_risk: 62,
  risk_trend: 5.2,
  vulnerability_breakdown: {
    incumbent_overserving: 45,
    asymmetric_threat_velocity: 72,
    technology_shift_momentum: 68,
    customer_job_misalignment: 55,
    business_model_innovation: 50,
  },
  primary_threats: [sampleDisruptionThreat],
};

const sampleDecisionOption: DecisionOption = {
  option_id: 'opt-1',
  title: 'Test Option',
  description: 'Test description',
  financial_impact: 1000000,
  implementation_time: '6 months',
  resource_requirements: ['Resource 1'],
  pros: ['Pro 1'],
  cons: ['Con 1'],
  risk_level: 'medium',
  confidence: 0.75,
};

const sampleStrategicDecision: StrategicDecision = {
  decision_id: 'dec-001',
  title: 'Test Decision',
  description: 'Test description',
  urgency_days: 14,
  financial_impact: 5000000,
  category: 'strategic',
  evidence: ['Evidence 1'],
  options: [sampleDecisionOption],
  recommended_option: 'opt-1',
  recommendation_rationale: 'Test rationale',
};

const sampleHealthThreat: HealthThreat = {
  threat_id: 'thr-1',
  title: 'Test Threat',
  urgency: 85,
  impact: 75,
  category: 'Competitive',
  description: 'Test description',
  mitigation_actions: ['Action 1'],
};

const sampleHealthOpportunity: HealthOpportunity = {
  opportunity_id: 'opp-1',
  title: 'Test Opportunity',
  roi_potential: 90,
  feasibility: 75,
  category: 'Growth',
  description: 'Test description',
  quick_wins: ['Quick win 1'],
};

const sampleCompetitivePositionSummary: CompetitivePositionSummary = {
  x_coordinate: 15,
  y_coordinate: 25,
  market_share_percentile: 35,
  competitive_strength: 'challenger',
};

const sampleStrategicHealthData: StrategicHealthData = {
  overall_health: 72,
  health_trend: 3.5,
  last_updated: new Date().toISOString(),
  top_threats: [sampleHealthThreat],
  top_opportunities: [sampleHealthOpportunity],
  competitive_position: sampleCompetitivePositionSummary,
  risk_trend_30d: [
    { date: '2025-10-10', risk_score: 35 },
  ],
  category_breakdown: {
    market_position: 68,
    innovation_capacity: 75,
    operational_efficiency: 72,
    financial_health: 73,
  },
};

// Export to avoid unused variable warnings
export {
  sampleCompetitivePosition,
  samplePositioningData,
  sampleDisruptionThreat,
  sampleDisruptionAssessment,
  sampleDecisionOption,
  sampleStrategicDecision,
  sampleHealthThreat,
  sampleHealthOpportunity,
  sampleCompetitivePositionSummary,
  sampleStrategicHealthData,
};

console.log('✅ All visualization component types verified successfully!');
