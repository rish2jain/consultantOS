'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FlywheelVelocity,
  MomentumComponent,
  HistoricalMatch,
  InflectionPoint,
  FlywheelDashboardProps,
} from '@/types/strategic-intelligence';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';

const FlywheelDashboard: React.FC<FlywheelDashboardProps> = ({
  velocity,
  onComponentClick,
  compact = false,
}) => {
  const [selectedComponent, setSelectedComponent] = useState<MomentumComponent | null>(null);
  const [showHistoricalMatches, setShowHistoricalMatches] = useState(true);

  const getScoreColor = (score: number): string => {
    if (score >= 71) return 'text-green-600';
    if (score >= 41) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 71) return 'bg-green-100';
    if (score >= 41) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getAccelerationIcon = (acceleration: string): string => {
    switch (acceleration) {
      case 'strong_up':
        return '↑↑';
      case 'moderate_up':
        return '↑';
      case 'stable':
        return '→';
      case 'declining':
        return '↓';
      default:
        return '→';
    }
  };

  const getPhaseColor = (phase: string): string => {
    switch (phase) {
      case 'Accelerating':
        return 'bg-green-600';
      case 'Building':
        return 'bg-yellow-600';
      case 'Stalled':
        return 'bg-red-600';
      default:
        return 'bg-gray-600';
    }
  };

  const handleComponentClick = (component: MomentumComponent) => {
    setSelectedComponent(component);
    if (onComponentClick) {
      onComponentClick(component);
    }
  };

  // Transform trend data for sparklines
  const transformTrendData = (data: number[]) => {
    return data.map((value, index) => ({
      index,
      value,
    }));
  };

  if (compact) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Flywheel Momentum</h2>
          <div className={`px-4 py-2 rounded-lg ${getPhaseColor(velocity.phase)} text-white font-bold text-lg`}>
            {velocity.phase.toUpperCase()}
          </div>
        </div>

        <div className="flex items-center justify-center mb-6">
          <div className="relative w-48 h-48">
            <svg viewBox="0 0 200 200" className="transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="20"
              />
              {/* Progress circle */}
              <circle
                cx="100"
                cy="100"
                r="80"
                fill="none"
                stroke={velocity.overall_score >= 71 ? '#10b981' : velocity.overall_score >= 41 ? '#f59e0b' : '#ef4444'}
                strokeWidth="20"
                strokeDasharray={`${(velocity.overall_score / 100) * 502.4} 502.4`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className={`text-4xl font-bold ${getScoreColor(velocity.overall_score)}`}>
                  {velocity.overall_score}
                </div>
                <div className="text-sm text-gray-500">Velocity</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-4">
          {velocity.components.map((component) => (
            <div key={component.name} className="text-center">
              <div className={`text-2xl font-bold ${getScoreColor(component.score)}`}>
                {component.score}
              </div>
              <div className="text-xs text-gray-600 mt-1">{component.name}</div>
              <div className="text-lg">{getAccelerationIcon(component.acceleration)}</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Flywheel Momentum Dashboard</h2>
        <div className={`px-6 py-3 rounded-lg ${getPhaseColor(velocity.phase)} text-white font-bold text-xl shadow-lg`}>
          {velocity.phase.toUpperCase()}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Central Gauge */}
        <div className="lg:col-span-1">
          <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
              Overall Velocity
            </h3>
            <div className="flex items-center justify-center">
              <div className="relative w-64 h-64">
                <svg viewBox="0 0 200 200" className="transform -rotate-90">
                  {/* Background circle */}
                  <circle
                    cx="100"
                    cy="100"
                    r="85"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="15"
                  />
                  {/* Red zone (0-40) */}
                  <circle
                    cx="100"
                    cy="100"
                    r="85"
                    fill="none"
                    stroke="#fecaca"
                    strokeWidth="15"
                    strokeDasharray={`${(40 / 100) * 534.1} 534.1`}
                    opacity="0.5"
                  />
                  {/* Yellow zone (41-70) */}
                  <circle
                    cx="100"
                    cy="100"
                    r="85"
                    fill="none"
                    stroke="#fde68a"
                    strokeWidth="15"
                    strokeDasharray={`${(30 / 100) * 534.1} 534.1`}
                    strokeDashoffset={`${-(40 / 100) * 534.1}`}
                    opacity="0.5"
                  />
                  {/* Green zone (71-100) */}
                  <circle
                    cx="100"
                    cy="100"
                    r="85"
                    fill="none"
                    stroke="#bbf7d0"
                    strokeWidth="15"
                    strokeDasharray={`${(30 / 100) * 534.1} 534.1`}
                    strokeDashoffset={`${-(70 / 100) * 534.1}`}
                    opacity="0.5"
                  />
                  {/* Progress indicator */}
                  <motion.circle
                    cx="100"
                    cy="100"
                    r="85"
                    fill="none"
                    stroke={velocity.overall_score >= 71 ? '#10b981' : velocity.overall_score >= 41 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="15"
                    strokeLinecap="round"
                    initial={{ strokeDasharray: '0 534.1' }}
                    animate={{ strokeDasharray: `${(velocity.overall_score / 100) * 534.1} 534.1` }}
                    transition={{ duration: 1.5, ease: 'easeOut' }}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <motion.div
                      className={`text-6xl font-bold ${getScoreColor(velocity.overall_score)}`}
                      initial={{ opacity: 0, scale: 0.5 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.5, delay: 0.5 }}
                    >
                      {velocity.overall_score}
                    </motion.div>
                    <div className="text-sm text-gray-500 mt-2">Velocity Score</div>
                    <div className="text-xs text-gray-400 mt-1">
                      Confidence: {(velocity.phase_confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600 italic">{velocity.prediction}</p>
            </div>
          </div>
        </div>

        {/* Component Breakdown */}
        <div className="lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Component Breakdown</h3>
          <div className="grid grid-cols-1 gap-4">
            {velocity.components.map((component) => (
              <motion.button
                key={component.name}
                onClick={() => handleComponentClick(component)}
                className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors text-left border-2 border-transparent hover:border-blue-300"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-16 h-16 rounded-full ${getScoreBgColor(component.score)} flex items-center justify-center`}>
                      <span className={`text-2xl font-bold ${getScoreColor(component.score)}`}>
                        {component.score}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{component.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-2xl">{getAccelerationIcon(component.acceleration)}</span>
                        <span className="text-xs text-gray-500 capitalize">
                          {component.acceleration.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 90-day sparkline */}
                  <div className="w-40 h-12">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={transformTrendData(component.trend_data)}>
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke={component.score >= 71 ? '#10b981' : component.score >= 41 ? '#f59e0b' : '#ef4444'}
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {component.key_drivers.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {component.key_drivers.map((driver, idx) => (
                      <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        {driver}
                      </span>
                    ))}
                  </div>
                )}
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      {/* Historical Pattern Matches */}
      {showHistoricalMatches && velocity.historical_matches.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Historical Pattern Matches</h3>
            <button
              onClick={() => setShowHistoricalMatches(false)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Hide
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {velocity.historical_matches.map((match, idx) => (
              <motion.div
                key={idx}
                className="bg-purple-50 rounded-lg p-4 border-2 border-purple-200"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{match.company}</h4>
                  <span className="text-xs bg-purple-600 text-white px-2 py-1 rounded-full">
                    {(match.match_confidence * 100).toFixed(0)}% match
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-2">{match.time_period}</div>
                <div className="bg-white rounded p-3 mb-3">
                  <p className="text-sm text-gray-900 font-medium">{match.outcome}</p>
                  {match.outcome_timeframe_months && (
                    <p className="text-xs text-gray-500 mt-1">
                      Timeframe: {match.outcome_timeframe_months} months
                    </p>
                  )}
                </div>
                {match.similarity_factors.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-gray-700">Similar Factors:</p>
                    {match.similarity_factors.slice(0, 3).map((factor, factorIdx) => (
                      <p key={factorIdx} className="text-xs text-gray-600 ml-2">
                        • {factor}
                      </p>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Inflection Points Timeline */}
      {velocity.inflection_points.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Inflection Points Detected</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="space-y-3">
              {velocity.inflection_points.map((point, idx) => (
                <div key={idx} className="flex items-start gap-3 pb-3 border-b border-gray-200 last:border-0">
                  <div className={`w-2 h-2 mt-2 rounded-full ${
                    point.significance === 'critical' ? 'bg-red-600' :
                    point.significance === 'major' ? 'bg-yellow-600' :
                    'bg-blue-600'
                  }`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900">{point.metric}</span>
                      <span className="text-xs text-gray-500">{new Date(point.date).toLocaleDateString()}</span>
                    </div>
                    <p className="text-sm text-gray-700">{point.strategic_note}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        point.significance === 'critical' ? 'bg-red-100 text-red-800' :
                        point.significance === 'major' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {point.significance}
                      </span>
                      <span className="text-xs text-gray-500">
                        Threshold: {point.threshold_crossed}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Component Detail Modal */}
      {selectedComponent && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setSelectedComponent(null)}
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-2xl font-bold text-gray-900 mb-4">{selectedComponent.name} Momentum</h3>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Current Score</div>
                <div className={`text-4xl font-bold ${getScoreColor(selectedComponent.score)}`}>
                  {selectedComponent.score}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-1">Acceleration</div>
                <div className="text-4xl font-bold text-gray-900">
                  {getAccelerationIcon(selectedComponent.acceleration)}
                </div>
                <div className="text-sm text-gray-600 capitalize">
                  {selectedComponent.acceleration.replace('_', ' ')}
                </div>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 mb-3">90-Day Trend</h4>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={transformTrendData(selectedComponent.trend_data)}>
                    <XAxis dataKey="index" hide />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#3b82f6"
                      strokeWidth={3}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 mb-3">Key Drivers</h4>
              <div className="flex flex-wrap gap-2">
                {selectedComponent.key_drivers.map((driver, idx) => (
                  <span key={idx} className="bg-blue-100 text-blue-800 px-3 py-2 rounded-lg text-sm">
                    {driver}
                  </span>
                ))}
              </div>
            </div>

            <div className="text-xs text-gray-500 mb-4">
              Last updated: {(() => {
                try {
                  const date = new Date(selectedComponent.last_updated);
                  if (isNaN(date.getTime())) {
                    return 'Unknown';
                  }
                  return date.toLocaleString();
                } catch {
                  return 'Unknown';
                }
              })()}
            </div>

            <button
              onClick={() => setSelectedComponent(null)}
              className="w-full bg-gray-900 text-white py-3 rounded-lg hover:bg-gray-800 transition-colors font-medium"
            >
              Close
            </button>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default FlywheelDashboard;
