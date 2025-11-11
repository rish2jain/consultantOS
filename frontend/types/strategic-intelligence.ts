/**
 * Strategic Intelligence Type Definitions
 * Comprehensive types for Phase 3 advanced visualizations
 */

// ============================================================================
// System Dynamics Map Types
// ============================================================================

export interface CausalLink {
  from_metric: string;
  to_metric: string;
  correlation: number; // -1 to 1
  time_delay_days: number;
  relationship_type: 'positive' | 'negative';
  strength?: number; // 0-1, for edge thickness
  confidence?: number; // 0-1
}

export interface FeedbackLoop {
  loop_id: string;
  loop_type: 'Reinforcing' | 'Balancing';
  nodes: string[];
  links: CausalLink[];
  loop_strength: number; // 0-1
  cycle_time_days: number;
  description?: string;
}

export interface LeveragePoint {
  intervention: string;
  impact_score: number; // 0-10
  node: string;
  expected_outcome: string;
  cost_estimate: number;
  roi: number;
  implementation_time_days?: number;
  risk_level?: 'low' | 'medium' | 'high';
}

export interface SystemNode {
  id: string;
  metric: string;
  value: number;
  trend: 'up' | 'down' | 'stable';
  category: 'market' | 'financial' | 'strategic' | 'operational';
  x?: number; // D3 computed position
  y?: number; // D3 computed position
}

export interface SystemDynamicsData {
  nodes: SystemNode[];
  links: CausalLink[];
  feedback_loops: FeedbackLoop[];
  leverage_points: LeveragePoint[];
  simulation_enabled?: boolean;
}

// ============================================================================
// Flywheel Dashboard Types
// ============================================================================

export interface MomentumComponent {
  name: string;
  score: number; // 0-100
  trend_data: number[]; // 90-day history
  acceleration: 'strong_up' | 'moderate_up' | 'stable' | 'declining';
  key_drivers: string[];
  last_updated: string;
}

export interface HistoricalMatch {
  company: string;
  time_period: string;
  match_confidence: number; // 0-1
  outcome: string;
  similarity_factors: string[];
  outcome_timeframe_months?: number;
}

export interface InflectionPoint {
  date: string;
  metric: string;
  threshold_crossed: number;
  significance: 'critical' | 'major' | 'moderate';
  strategic_note: string;
}

export interface FlywheelVelocity {
  overall_score: number; // 0-100
  market_momentum: number;
  financial_momentum: number;
  strategic_momentum: number;
  execution_momentum: number;
  talent_momentum: number;
  phase: 'Stalled' | 'Building' | 'Accelerating';
  phase_confidence: number; // 0-1
  historical_matches: HistoricalMatch[];
  prediction: string;
  inflection_points: InflectionPoint[];
  components: MomentumComponent[];
  last_updated: string;
}

// ============================================================================
// Strategic Intelligence Dashboard Types
// ============================================================================

export interface StrategicThreat {
  id: string;
  title: string;
  severity: number; // 0-100
  category: 'disruption' | 'position' | 'financial' | 'operational';
  source: string; // e.g., "Startup X", "Market Trend"
  timeline_months: number;
  mitigation_available: boolean;
  details: string;
}

export interface StrategicOpportunity {
  id: string;
  title: string;
  value_score: number; // 0-100
  category: 'geographic' | 'flywheel' | 'innovation' | 'partnership';
  estimated_value: number; // USD
  timeframe_months: number;
  roi_estimate: number;
  requirements: string[];
  details: string;
}

export interface DecisionCard {
  id: string;
  title: string;
  urgency_days: number;
  impact_value: number; // USD
  category: 'strategic' | 'operational' | 'financial';
  options: DecisionOption[];
  recommendation: string;
  decision_deadline: string;
  status: 'pending' | 'accepted' | 'rejected' | 'deferred';
}

export interface DecisionOption {
  option_id: string;
  title: string;
  pros: string[];
  cons: string[];
  estimated_cost: number;
  expected_outcome: string;
  risk_level: 'low' | 'medium' | 'high';
  implementation_time_days: number;
}

export interface ExecutiveBrief {
  strategic_health_score: number; // 0-100
  trend: 'up' | 'down' | 'stable';
  top_threats: StrategicThreat[];
  top_opportunities: StrategicOpportunity[];
  decisions_required: DecisionCard[];
  last_updated: string;
}

export interface StrategicContext {
  positioning: PositioningAnalysis;
  disruption: DisruptionAnalysis;
  dynamics: SystemDynamicsData;
  momentum: FlywheelVelocity;
  decisions: DecisionCard[];
}

export interface PositioningAnalysis {
  porter_five_forces: {
    competitive_rivalry: number;
    supplier_power: number;
    buyer_power: number;
    threat_of_substitution: number;
    threat_of_new_entry: number;
  };
  blue_ocean_score: number;
  differentiation_strength: number;
  market_share_trend: number[];
  competitive_moat_strength: number;
}

export interface DisruptionAnalysis {
  overall_risk: number; // 0-100
  disruptors: Array<{
    name: string;
    threat_level: number;
    growth_rate: number;
    time_to_impact_months: number;
  }>;
  innovation_pace: number;
  market_maturity: 'emerging' | 'growth' | 'mature' | 'declining';
}

// ============================================================================
// Intelligence Feed Types
// ============================================================================

export type IntelligenceCardType =
  | 'disruption_alert'
  | 'position_threat'
  | 'loop_detection'
  | 'flywheel_milestone'
  | 'pattern_match'
  | 'decision_due'
  | 'opportunity'
  | 'metric_threshold';

export interface IntelligenceCard {
  id: string;
  type: IntelligenceCardType;
  urgency: 'critical' | 'important' | 'info';
  title: string;
  description: string;
  timestamp: string;
  read: boolean;
  metadata: Record<string, any>;
  actions?: Array<{
    label: string;
    action: string;
    primary?: boolean;
  }>;
}

export interface IntelligenceFeedData {
  cards: IntelligenceCard[];
  unread_count: number;
  last_updated: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface StrategicIntelligenceOverview {
  executive_brief: ExecutiveBrief;
  strategic_context: StrategicContext;
  intelligence_feed: IntelligenceFeedData;
  company: string;
  industry: string;
  analysis_date: string;
}

// ============================================================================
// WebSocket Message Types
// ============================================================================

export interface LiveIntelligenceUpdate {
  type: 'new_card' | 'update_card' | 'delete_card' | 'health_update';
  data: IntelligenceCard | { strategic_health_score: number } | { card_id: string };
  timestamp: string;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface SystemDynamicsMapProps {
  data: SystemDynamicsData;
  onNodeClick?: (node: SystemNode) => void;
  onLeveragePointClick?: (point: LeveragePoint) => void;
  height?: number;
  width?: number;
  simulationEnabled?: boolean;
}

export interface FlywheelDashboardProps {
  velocity: FlywheelVelocity;
  onComponentClick?: (component: MomentumComponent) => void;
  compact?: boolean;
}

export interface IntelligenceFeedProps {
  initialData?: IntelligenceFeedData;
  enableRealtime?: boolean;
  filters?: IntelligenceCardType[];
  onActionClick?: (cardId: string, action: string) => void;
}

// ============================================================================
// Utility Types
// ============================================================================

export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface GaugeConfig {
  min: number;
  max: number;
  zones: Array<{
    from: number;
    to: number;
    color: string;
    label: string;
  }>;
}

export type TrendDirection = 'up' | 'down' | 'stable';
export type AccelerationLevel = 'strong_up' | 'moderate_up' | 'stable' | 'declining';
export type UrgencyLevel = 'critical' | 'important' | 'info';
