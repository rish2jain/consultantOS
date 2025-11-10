'use client';

import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
} from 'recharts';
import { forecastApi, ForecastData } from '@/lib/mvp-api';
import { Loader2, TrendingUp, Calendar } from 'lucide-react';

interface ChartDataPoint {
  date: string;
  prediction: number;
  lowerBound: number;
  upperBound: number;
}

export default function ForecastChart() {
  const [data, setData] = useState<ForecastData | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periods, setPeriods] = useState(30);

  const loadForecast = async () => {
    setLoading(true);
    setError(null);

    try {
      const forecastData = await forecastApi(periods);
      setData(forecastData);

      // Transform data for Recharts
      const transformed: ChartDataPoint[] = forecastData.dates.map((date, idx) => ({
        date: new Date(date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        }),
        prediction: forecastData.predictions[idx],
        lowerBound: forecastData.lower_bound[idx],
        upperBound: forecastData.upper_bound[idx],
      }));

      setChartData(transformed);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load forecast');
      console.error('Forecast error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadForecast();
  }, [periods]);

  if (loading) {
    return (
      <div className="flex flex-col h-full bg-white rounded-lg shadow-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-500 to-pink-600">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-white" />
            <h2 className="text-lg font-semibold text-white">Market Forecast</h2>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-3" />
            <p className="text-gray-600">Loading forecast data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-full bg-white rounded-lg shadow-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-500 to-pink-600">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-white" />
            <h2 className="text-lg font-semibold text-white">Market Forecast</h2>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center">
            <p className="text-red-600 mb-4">⚠️ {error}</p>
            <button
              onClick={loadForecast}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const firstValue = data?.predictions[0] || 0;
  const lastValue = data?.predictions[data.predictions.length - 1] || 0;
  const change = lastValue - firstValue;
  const changePercent = ((change / firstValue) * 100).toFixed(1);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-500 to-pink-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-white" />
            <h2 className="text-lg font-semibold text-white">Market Forecast</h2>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={periods}
              onChange={(e) => setPeriods(Number(e.target.value))}
              className="px-3 py-1 bg-white/20 text-white rounded-lg text-sm border border-white/30 hover:bg-white/30 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-white/50"
            >
              <option value={7} className="text-gray-900">7 Days</option>
              <option value={14} className="text-gray-900">14 Days</option>
              <option value={30} className="text-gray-900">30 Days</option>
              <option value={90} className="text-gray-900">90 Days</option>
            </select>
          </div>
        </div>
        <p className="text-sm text-purple-100 mt-1">
          AI-powered market predictions with confidence intervals
        </p>
      </div>

      {/* Stats */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-gray-600 mb-1">Current Value</p>
            <p className="text-lg font-semibold text-gray-900">
              {firstValue.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 mb-1">Predicted Value</p>
            <p className="text-lg font-semibold text-gray-900">
              {lastValue.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 mb-1">Change</p>
            <p
              className={`text-lg font-semibold ${
                change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {change >= 0 ? '+' : ''}
              {changePercent}%
            </p>
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2 text-sm">
          <Calendar className="w-4 h-4 text-gray-500" />
          <span className="text-gray-600">
            Confidence: <span className="font-semibold text-gray-900">{(data?.confidence || 0).toFixed(1)}%</span>
          </span>
        </div>
      </div>

      {/* Chart */}
      <div className="flex-1 p-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPrediction" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ec4899" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#ec4899" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              tick={{ fill: '#6b7280' }}
            />
            <YAxis
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              tick={{ fill: '#6b7280' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: '12px' }}
              iconType="line"
            />
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="transparent"
              fill="url(#colorConfidence)"
              name="Upper Bound"
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stroke="transparent"
              fill="url(#colorConfidence)"
              name="Lower Bound"
            />
            <Line
              type="monotone"
              dataKey="prediction"
              stroke="#8b5cf6"
              strokeWidth={3}
              dot={{ fill: '#8b5cf6', r: 4 }}
              activeDot={{ r: 6 }}
              name="Prediction"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
