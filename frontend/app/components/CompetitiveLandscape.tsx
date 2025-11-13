'use client';

/**
 * Competitive Landscape Map
 *
 * Interactive 2D positioning map showing competitive dynamics
 * with bubble size representing market share.
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Download, Info } from 'lucide-react';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface Competitor {
  name: string;
  price_index: number; // 0-100 scale
  quality_index: number; // 0-100 scale
  market_share: number; // %
  revenue: number; // $
  growth_rate: number; // %
  is_target: boolean; // True for the company being analyzed
}

interface CompetitiveLandscapeProps {
  company: string;
  competitors?: Competitor[];
}

export function CompetitiveLandscape({
  company,
  competitors: initialCompetitors,
}: CompetitiveLandscapeProps) {
  // Sample data - in production, fetch from API
  const [competitors] = useState<Competitor[]>(
    initialCompetitors || [
      {
        name: company,
        price_index: 75,
        quality_index: 85,
        market_share: 25,
        revenue: 50000000000,
        growth_rate: 15,
        is_target: true,
      },
      {
        name: 'Competitor A',
        price_index: 60,
        quality_index: 70,
        market_share: 20,
        revenue: 40000000000,
        growth_rate: 10,
        is_target: false,
      },
      {
        name: 'Competitor B',
        price_index: 85,
        quality_index: 90,
        market_share: 18,
        revenue: 35000000000,
        growth_rate: 8,
        is_target: false,
      },
      {
        name: 'Competitor C',
        price_index: 50,
        quality_index: 60,
        market_share: 15,
        revenue: 30000000000,
        growth_rate: 12,
        is_target: false,
      },
      {
        name: 'Competitor D',
        price_index: 90,
        quality_index: 75,
        market_share: 12,
        revenue: 25000000000,
        growth_rate: 5,
        is_target: false,
      },
      {
        name: 'Others',
        price_index: 65,
        quality_index: 65,
        market_share: 10,
        revenue: 20000000000,
        growth_rate: 7,
        is_target: false,
      },
    ]
  );

  const [_selectedCompetitor, setSelectedCompetitor] = useState<Competitor | null>(null);

  // Prepare plot data
  const plotData = competitors.map((comp) => ({
    x: [comp.price_index],
    y: [comp.quality_index],
    mode: 'markers+text',
    type: 'scatter',
    name: comp.name,
    text: [comp.name],
    textposition: 'top center',
    marker: {
      size: [Math.sqrt(comp.market_share) * 10], // Scale bubble size
      color: comp.is_target ? '#3b82f6' : '#94a3b8',
      line: {
        color: comp.is_target ? '#1e40af' : '#64748b',
        width: comp.is_target ? 3 : 1,
      },
    },
    hovertemplate:
      '<b>%{text}</b><br>' +
      'Price Index: %{x}<br>' +
      'Quality Index: %{y}<br>' +
      `Market Share: ${comp.market_share}%<br>` +
      `Growth: ${comp.growth_rate}%<br>` +
      '<extra></extra>',
  }));

  const layout = {
    autosize: true,
    margin: { l: 60, r: 60, t: 40, b: 60 },
    xaxis: {
      title: 'Price Index (Lower = More Affordable)',
      range: [0, 100],
      showgrid: true,
      gridcolor: '#e5e7eb',
    },
    yaxis: {
      title: 'Quality / Features Index',
      range: [0, 100],
      showgrid: true,
      gridcolor: '#e5e7eb',
    },
    showlegend: false,
    hovermode: 'closest',
    // Add quadrant lines
    shapes: [
      {
        type: 'line',
        x0: 50,
        y0: 0,
        x1: 50,
        y1: 100,
        line: {
          color: '#cbd5e1',
          width: 1,
          dash: 'dash',
        },
      },
      {
        type: 'line',
        x0: 0,
        y0: 50,
        x1: 100,
        y1: 50,
        line: {
          color: '#cbd5e1',
          width: 1,
          dash: 'dash',
        },
      },
    ],
    annotations: [
      {
        x: 25,
        y: 75,
        text: 'Premium<br>Value',
        showarrow: false,
        font: { size: 10, color: '#94a3b8' },
      },
      {
        x: 75,
        y: 75,
        text: 'Premium<br>Positioning',
        showarrow: false,
        font: { size: 10, color: '#94a3b8' },
      },
      {
        x: 25,
        y: 25,
        text: 'Budget<br>Market',
        showarrow: false,
        font: { size: 10, color: '#94a3b8' },
      },
      {
        x: 75,
        y: 25,
        text: 'Questionable<br>Value',
        showarrow: false,
        font: { size: 10, color: '#94a3b8' },
      },
    ],
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Competitive Positioning Map</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Bubble size represents market share
              </p>
            </div>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Plot
            data={plotData as any}
            layout={layout}
            useResizeHandler
            style={{ width: '100%', height: '600px' }}
            config={{
              displayModeBar: true,
              displaylogo: false,
              responsive: true,
              modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            }}
            onClick={(data: any) => {
              if (data.points && data.points.length > 0) {
                const curveNumber = data.points[0].curveNumber;
                setSelectedCompetitor(competitors[curveNumber]);
              }
            }}
          />

          {/* Legend */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Info className="h-4 w-4 text-gray-600" />
              <p className="text-sm font-medium text-gray-700">Quadrant Interpretation</p>
            </div>
            <div className="grid grid-cols-2 gap-3 text-xs text-gray-600">
              <div>
                <strong>Premium Value (Top Left):</strong> High quality at competitive prices
              </div>
              <div>
                <strong>Premium Positioning (Top Right):</strong> High quality, premium pricing
              </div>
              <div>
                <strong>Budget Market (Bottom Left):</strong> Lower quality, competitive prices
              </div>
              <div>
                <strong>Questionable Value (Bottom Right):</strong> Lower quality at high prices
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Competitor Details Table */}
      <Card>
        <CardHeader>
          <CardTitle>Competitor Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Company
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Market Share
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Revenue
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Growth Rate
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Price Index
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Quality Index
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {competitors
                  .sort((a, b) => b.market_share - a.market_share)
                  .map((comp) => (
                    <tr
                      key={comp.name}
                      className={comp.is_target ? 'bg-blue-50' : 'hover:bg-gray-50'}
                    >
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {comp.name}
                        {comp.is_target && (
                          <span className="ml-2 text-xs text-blue-600">(You)</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        {comp.market_share.toFixed(1)}%
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        ${(comp.revenue / 1000000000).toFixed(1)}B
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        <span
                          className={
                            comp.growth_rate > 10
                              ? 'text-green-600'
                              : comp.growth_rate > 5
                              ? 'text-yellow-600'
                              : 'text-red-600'
                          }
                        >
                          {comp.growth_rate > 0 ? '+' : ''}
                          {comp.growth_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        {comp.price_index}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">
                        {comp.quality_index}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Strategic Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Strategic Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <StrategicInsights company={company} competitors={competitors} />
        </CardContent>
      </Card>
    </div>
  );
}

function StrategicInsights({
  company,
  competitors,
}: {
  company: string;
  competitors: Competitor[];
}) {
  const target = competitors.find((c) => c.is_target);
  if (!target) return null;

  const insights: string[] = [];

  // Quality positioning insight
  if (target.quality_index > 80) {
    insights.push(
      `${company} is positioned in the premium quality segment - maintain quality leadership while monitoring price sensitivity.`
    );
  } else if (target.quality_index < 50) {
    insights.push(
      `${company} has opportunity to improve quality perception to justify pricing and gain market share.`
    );
  }

  // Price positioning insight
  if (target.price_index > 80) {
    insights.push(
      `High price positioning may limit market penetration - consider value-based pricing strategies.`
    );
  } else if (target.price_index < 40) {
    insights.push(
      `Competitive pricing provides strong value proposition - opportunity to capture price-sensitive segments.`
    );
  }

  // Market share insight
  if (target.market_share > 20) {
    insights.push(
      `Strong market position (${target.market_share}% share) - focus on retention and premium positioning.`
    );
  } else {
    insights.push(
      `Market share growth opportunity - identify underserved segments and competitive gaps.`
    );
  }

  // Growth insight
  if (target.growth_rate > 12) {
    insights.push(
      `Exceptional growth momentum (${target.growth_rate}%) - ensure operational scalability to support expansion.`
    );
  }

  return (
    <ul className="space-y-3">
      {insights.map((insight, idx) => (
        <li key={idx} className="flex items-start gap-2">
          <span className="text-blue-500 mt-1 flex-shrink-0">•</span>
          <span className="text-sm text-gray-700">{insight}</span>
        </li>
      ))}
    </ul>
  );
}
