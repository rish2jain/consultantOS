'use client';

/**
 * Scenario Planning Tool
 *
 * Interactive what-if analysis with adjustable assumptions
 * and real-time forecast visualization.
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Label } from '@/app/components/ui/label';
import { Slider } from '@/app/components/ui/slider';
import { Switch } from '@/app/components/ui/switch';
import { Play, Download, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface ScenarioPlannerProps {
  company: string;
  industry: string;
  apiUrl?: string;
}

interface ScenarioAssumptions {
  market_growth_rate: number;
  competitor_entry: boolean;
  regulatory_change: boolean;
  price_change: number;
  cost_change: number;
  market_share_target?: number;
}

interface ScenarioForecast {
  scenario_id: string;
  revenue_forecast: number[];
  profit_forecast: number[];
  market_share_forecast: number[];
  risk_score: number;
  confidence: number;
  key_insights: string[];
}

export function ScenarioPlanner({ company, industry, apiUrl = '/api' }: ScenarioPlannerProps) {
  const [assumptions, setAssumptions] = useState<ScenarioAssumptions>({
    market_growth_rate: 5.0,
    competitor_entry: false,
    regulatory_change: false,
    price_change: 0,
    cost_change: 0,
    market_share_target: 25.0,
  });

  const [forecast, setForecast] = useState<ScenarioForecast | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runScenario = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${apiUrl}/dashboards/scenarios/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company,
          industry,
          assumptions,
          forecast_period: 12,
        }),
      });

      if (!response.ok) throw new Error('Failed to run scenario');

      const result = await response.json();
      setForecast(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run scenario');
    } finally {
      setLoading(false);
    }
  };

  const resetAssumptions = () => {
    setAssumptions({
      market_growth_rate: 5.0,
      competitor_entry: false,
      regulatory_change: false,
      price_change: 0,
      cost_change: 0,
      market_share_target: 25.0,
    });
    setForecast(null);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Scenario Planning: {company}</CardTitle>
          <p className="text-sm text-gray-600">
            Adjust assumptions below to explore different strategic scenarios
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Market Growth Rate */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>Market Growth Rate</Label>
              <span className="text-sm font-medium">{assumptions.market_growth_rate.toFixed(1)}%</span>
            </div>
            <Slider
              value={[assumptions.market_growth_rate]}
              onValueChange={([value]) =>
                setAssumptions({ ...assumptions, market_growth_rate: value })
              }
              min={-20}
              max={50}
              step={0.5}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              Annual market growth rate (-20% to +50%)
            </p>
          </div>

          {/* Price Change */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>Price Adjustment</Label>
              <span className="text-sm font-medium">{assumptions.price_change.toFixed(1)}%</span>
            </div>
            <Slider
              value={[assumptions.price_change]}
              onValueChange={([value]) =>
                setAssumptions({ ...assumptions, price_change: value })
              }
              min={-30}
              max={30}
              step={0.5}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              Price increase or decrease (-30% to +30%)
            </p>
          </div>

          {/* Cost Change */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>Cost Change</Label>
              <span className="text-sm font-medium">{assumptions.cost_change.toFixed(1)}%</span>
            </div>
            <Slider
              value={[assumptions.cost_change]}
              onValueChange={([value]) =>
                setAssumptions({ ...assumptions, cost_change: value })
              }
              min={-20}
              max={40}
              step={0.5}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              Cost increase or decrease (-20% to +40%)
            </p>
          </div>

          {/* Market Share Target */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>Market Share Target</Label>
              <span className="text-sm font-medium">{assumptions.market_share_target?.toFixed(1)}%</span>
            </div>
            <Slider
              value={[assumptions.market_share_target || 25]}
              onValueChange={([value]) =>
                setAssumptions({ ...assumptions, market_share_target: value })
              }
              min={5}
              max={50}
              step={0.5}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              Target market share (5% to 50%)
            </p>
          </div>

          {/* Boolean Switches */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <Label>Competitor Entry</Label>
                <p className="text-xs text-gray-500 mt-1">New competitor enters market</p>
              </div>
              <Switch
                checked={assumptions.competitor_entry}
                onCheckedChange={(checked) =>
                  setAssumptions({ ...assumptions, competitor_entry: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <Label>Regulatory Change</Label>
                <p className="text-xs text-gray-500 mt-1">Major regulation change</p>
              </div>
              <Switch
                checked={assumptions.regulatory_change}
                onCheckedChange={(checked) =>
                  setAssumptions({ ...assumptions, regulatory_change: checked })
                }
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button onClick={runScenario} disabled={loading} className="flex-1">
              <Play className="h-4 w-4 mr-2" />
              {loading ? 'Running Scenario...' : 'Run Scenario'}
            </Button>
            <Button onClick={resetAssumptions} variant="outline">
              Reset
            </Button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Forecast Results */}
      {forecast && (
        <div className="space-y-6">
          {/* Risk and Confidence */}
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Risk Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <AlertTriangle
                    className={`h-8 w-8 ${
                      forecast.risk_score > 0.7
                        ? 'text-red-500'
                        : forecast.risk_score > 0.4
                        ? 'text-yellow-500'
                        : 'text-green-500'
                    }`}
                  />
                  <div>
                    <p className="text-2xl font-bold">
                      {(forecast.risk_score * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-gray-600">
                      {forecast.risk_score > 0.7
                        ? 'High Risk'
                        : forecast.risk_score > 0.4
                        ? 'Moderate Risk'
                        : 'Low Risk'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Confidence Level</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-8 w-8 text-blue-500" />
                  <div>
                    <p className="text-2xl font-bold">
                      {(forecast.confidence * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-gray-600">Forecast Confidence</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Key Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Key Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {forecast.key_insights.map((insight, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-blue-500 mt-1">•</span>
                    <span className="text-sm">{insight}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Forecast Charts */}
          <ForecastVisualization forecast={forecast} />
        </div>
      )}
    </div>
  );
}

function ForecastVisualization({ forecast }: { forecast: ScenarioForecast }) {
  const months = Array.from({ length: forecast.revenue_forecast.length }, (_, i) => i + 1);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Revenue Forecast */}
      <Card>
        <CardHeader>
          <CardTitle>Revenue Forecast</CardTitle>
        </CardHeader>
        <CardContent>
          <Plot
            data={[
              {
                x: months,
                y: forecast.revenue_forecast,
                type: 'scatter',
                mode: 'lines+markers',
                marker: { color: '#3b82f6' },
                line: { width: 2 },
                name: 'Revenue',
              },
            ]}
            layout={{
              autosize: true,
              margin: { l: 60, r: 20, t: 20, b: 40 },
              xaxis: { title: 'Month' },
              yaxis: { title: 'Revenue ($)' },
              showlegend: false,
            }}
            useResizeHandler
            style={{ width: '100%', height: '300px' }}
            config={{ displayModeBar: false, responsive: true }}
          />
        </CardContent>
      </Card>

      {/* Profit Forecast */}
      <Card>
        <CardHeader>
          <CardTitle>Profit Forecast</CardTitle>
        </CardHeader>
        <CardContent>
          <Plot
            data={[
              {
                x: months,
                y: forecast.profit_forecast,
                type: 'scatter',
                mode: 'lines+markers',
                marker: { color: '#10b981' },
                line: { width: 2 },
                name: 'Profit',
              },
            ]}
            layout={{
              autosize: true,
              margin: { l: 60, r: 20, t: 20, b: 40 },
              xaxis: { title: 'Month' },
              yaxis: { title: 'Profit ($)' },
              showlegend: false,
            }}
            useResizeHandler
            style={{ width: '100%', height: '300px' }}
            config={{ displayModeBar: false, responsive: true }}
          />
        </CardContent>
      </Card>

      {/* Market Share Forecast */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Market Share Forecast</CardTitle>
        </CardHeader>
        <CardContent>
          <Plot
            data={[
              {
                x: months,
                y: forecast.market_share_forecast,
                type: 'scatter',
                mode: 'lines+markers',
                marker: { color: '#8b5cf6' },
                line: { width: 2 },
                name: 'Market Share',
              },
            ]}
            layout={{
              autosize: true,
              margin: { l: 60, r: 20, t: 20, b: 40 },
              xaxis: { title: 'Month' },
              yaxis: { title: 'Market Share (%)' },
              showlegend: false,
            }}
            useResizeHandler
            style={{ width: '100%', height: '300px' }}
            config={{ displayModeBar: false, responsive: true }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
