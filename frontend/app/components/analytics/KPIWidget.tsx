/**
 * KPI Widget Component
 * Displays KPI with current value, target, trend, and alerts
 */
import React from 'react';

interface KPIWidgetProps {
  kpiId: string;
  name: string;
  currentValue?: number;
  targetValue?: number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  percentageChange?: number;
  alerts?: number;
  status?: 'normal' | 'warning' | 'critical';
  onClick?: () => void;
}

export const KPIWidget: React.FC<KPIWidgetProps> = ({
  kpiId,
  name,
  currentValue = 0,
  targetValue,
  unit = '',
  trend = 'stable',
  percentageChange = 0,
  alerts = 0,
  status = 'normal',
  onClick,
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <span className="text-green-500 text-2xl">↑</span>;
      case 'down':
        return <span className="text-red-500 text-2xl">↓</span>;
      default:
        return <span className="text-gray-500 text-2xl">→</span>;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'critical':
        return 'border-red-500 bg-red-50';
      case 'warning':
        return 'border-yellow-500 bg-yellow-50';
      default:
        return 'border-gray-200 bg-white';
    }
  };

  const getProgressPercentage = () => {
    if (!targetValue || targetValue === 0) return 0;
    return Math.min((currentValue / targetValue) * 100, 100);
  };

  return (
    <div
      onClick={onClick}
      className={`kpi-widget p-6 rounded-lg border-2 shadow-md cursor-pointer transition hover:shadow-lg ${getStatusColor()}`}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-800">{name}</h3>
          <p className="text-xs text-gray-500">ID: {kpiId}</p>
        </div>
        {alerts > 0 && (
          <div className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
            {alerts}
          </div>
        )}
      </div>

      {/* Current Value */}
      <div className="mb-4">
        <div className="text-4xl font-bold text-gray-900">
          {currentValue.toLocaleString()}
          <span className="text-lg text-gray-500 ml-2">{unit}</span>
        </div>
      </div>

      {/* Trend and Change */}
      <div className="flex items-center gap-3 mb-4">
        {getTrendIcon()}
        <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
          {percentageChange > 0 ? '+' : ''}
          {percentageChange.toFixed(1)}%
        </span>
      </div>

      {/* Progress Bar */}
      {targetValue && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">Target</span>
            <span className="text-sm font-medium text-gray-700">
              {getProgressPercentage().toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-xs text-gray-500">
              Current: {currentValue.toLocaleString()}
            </span>
            <span className="text-xs text-gray-500">
              Target: {targetValue.toLocaleString()}
            </span>
          </div>
        </div>
      )}

      {/* Status Badge */}
      <div className="flex gap-2">
        <span
          className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
            status === 'critical'
              ? 'bg-red-200 text-red-800'
              : status === 'warning'
              ? 'bg-yellow-200 text-yellow-800'
              : 'bg-green-200 text-green-800'
          }`}
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>
    </div>
  );
};

export default KPIWidget;
