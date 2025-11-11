'use client';

import { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';

/**
 * Competitive Position Data Structure
 * Represents a company's position in the competitive landscape
 */
export interface CompetitivePosition {
  company: string;
  x_coordinate: number;  // Market share growth rate (%)
  y_coordinate: number;  // Profit margin (%)
  bubble_size: number;   // Market capitalization (scaled)
  sentiment_color: string;
  movement_vector: [number, number];
  velocity: number;
}

/**
 * Complete Positioning Data including competitors and opportunities
 */
export interface PositioningData {
  company_position: CompetitivePosition;
  competitor_positions: CompetitivePosition[];
  white_space_opportunities: string[];
  position_threats: string[];
  historical_snapshots?: {
    timestamp: string;
    positions: CompetitivePosition[];
  }[];
}

interface CompetitivePositioningMapProps {
  data: PositioningData;
  width?: number;
  height?: number;
  onCompanyClick?: (company: string) => void;
  className?: string;
}

/**
 * Competitive Positioning Map Component
 *
 * Interactive D3.js bubble chart showing competitive landscape with:
 * - Force-directed layout for bubble positioning
 * - Movement vectors showing 3-month trajectory
 * - Time scrubber for historical replay
 * - Sentiment-based color gradients
 * - Zoom/pan controls
 *
 * @component
 * @example
 * ```tsx
 * <CompetitivePositioningMap
 *   data={positioningData}
 *   onCompanyClick={(company) => console.log(company)}
 * />
 * ```
 */
export default function CompetitivePositioningMap({
  data,
  width = 800,
  height = 600,
  onCompanyClick,
  className = '',
}: CompetitivePositioningMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [currentSnapshotIndex, setCurrentSnapshotIndex] = useState<number>(
    data.historical_snapshots ? data.historical_snapshots.length - 1 : 0
  );
  const [isPlaying, setIsPlaying] = useState(false);
  const animationRef = useRef<number | null>(null);

  // Combine all positions for current view
  const allPositions = useMemo(() => {
    if (data.historical_snapshots && currentSnapshotIndex >= 0) {
      return data.historical_snapshots[currentSnapshotIndex].positions;
    }
    return [data.company_position, ...data.competitor_positions];
  }, [data, currentSnapshotIndex]);

  // Color scale for sentiment
  const sentimentColorScale = d3.scaleLinear<string>()
    .domain([-1, 0, 1])
    .range(['#ef4444', '#fbbf24', '#10b981']);

  // Radius scale for market cap
  const radiusScale = d3.scaleSqrt()
    .domain([0, d3.max(allPositions, d => d.bubble_size) || 100])
    .range([20, 60]);

  useEffect(() => {
    if (!svgRef.current || allPositions.length === 0) return;

    const svg = d3.select(svgRef.current);
    const margin = { top: 40, right: 100, bottom: 60, left: 80 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous content
    svg.selectAll('*').remove();

    // Create main group with margins
    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 5])
      .on('zoom', (event) => {
        g.attr('transform', `translate(${margin.left + event.transform.x},${margin.top + event.transform.y}) scale(${event.transform.k})`);
      });

    svg.call(zoom);

    // Scales
    const xScale = d3.scaleLinear()
      .domain([
        d3.min(allPositions, d => d.x_coordinate) || -10,
        d3.max(allPositions, d => d.x_coordinate) || 10
      ])
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([
        d3.min(allPositions, d => d.y_coordinate) || 0,
        d3.max(allPositions, d => d.y_coordinate) || 50
      ])
      .range([innerHeight, 0]);

    // Axes
    const xAxis = d3.axisBottom(xScale)
      .ticks(10)
      .tickFormat(d => `${d}%`);

    const yAxis = d3.axisLeft(yScale)
      .ticks(10)
      .tickFormat(d => `${d}%`);

    // Add grid lines
    g.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale).tickSize(-innerHeight).tickFormat(() => ''))
      .style('stroke-opacity', 0.1);

    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(() => ''))
      .style('stroke-opacity', 0.1);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .append('text')
      .attr('x', innerWidth / 2)
      .attr('y', 40)
      .attr('fill', 'currentColor')
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Market Share Growth Rate (%)');

    g.append('g')
      .call(yAxis)
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -innerHeight / 2)
      .attr('y', -60)
      .attr('fill', 'currentColor')
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Profit Margin (%)');

    // Create force simulation for bubble layout
    const simulation = d3.forceSimulation(allPositions as any)
      .force('x', d3.forceX((d: any) => xScale(d.x_coordinate)).strength(0.1))
      .force('y', d3.forceY((d: any) => yScale(d.y_coordinate)).strength(0.1))
      .force('collision', d3.forceCollide((d: any) => radiusScale(d.bubble_size) + 2))
      .stop();

    // Run simulation
    for (let i = 0; i < 300; i++) simulation.tick();

    // Movement vectors (arrows)
    const arrows = g.append('g').attr('class', 'arrows');

    allPositions.forEach((pos) => {
      if (pos.movement_vector && pos.movement_vector[0] !== 0 && pos.movement_vector[1] !== 0) {
        const [vx, vy] = pos.movement_vector;
        const x = xScale(pos.x_coordinate);
        const y = yScale(pos.y_coordinate);
        const endX = xScale(pos.x_coordinate + vx);
        const endY = yScale(pos.y_coordinate + vy);

        arrows.append('line')
          .attr('x1', x)
          .attr('y1', y)
          .attr('x2', endX)
          .attr('y2', endY)
          .attr('stroke', '#94a3b8')
          .attr('stroke-width', 2)
          .attr('marker-end', 'url(#arrowhead)')
          .style('opacity', 0.6);
      }
    });

    // Add arrowhead marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('markerWidth', 10)
      .attr('markerHeight', 10)
      .attr('refX', 8)
      .attr('refY', 3)
      .attr('orient', 'auto')
      .append('polygon')
      .attr('points', '0 0, 10 3, 0 6')
      .attr('fill', '#94a3b8');

    // Bubbles
    const bubbles = g.append('g').attr('class', 'bubbles');

    const bubble = bubbles.selectAll('g')
      .data(allPositions)
      .enter()
      .append('g')
      .attr('transform', (d: any) => `translate(${xScale(d.x_coordinate)},${yScale(d.y_coordinate)})`)
      .style('cursor', 'pointer')
      .on('click', (_event, d) => {
        setSelectedCompany(d.company);
        onCompanyClick?.(d.company);
      })
      .on('mouseenter', function(event, d) {
        // Highlight bubble
        d3.select(this).select('circle')
          .transition()
          .duration(200)
          .attr('stroke-width', 3)
          .attr('filter', 'url(#glow)');

        // Show tooltip
        if (tooltipRef.current) {
          const tooltip = d3.select(tooltipRef.current);
          tooltip
            .style('opacity', 1)
            .style('left', `${event.pageX + 10}px`)
            .style('top', `${event.pageY - 10}px`)
            .html(`
              <div class="font-semibold mb-2">${d.company}</div>
              <div class="text-xs space-y-1">
                <div>Growth: ${d.x_coordinate.toFixed(1)}%</div>
                <div>Margin: ${d.y_coordinate.toFixed(1)}%</div>
                <div>Market Cap: $${(d.bubble_size / 1000).toFixed(1)}B</div>
                <div>Velocity: ${d.velocity.toFixed(2)}</div>
              </div>
            `);
        }
      })
      .on('mouseleave', function() {
        d3.select(this).select('circle')
          .transition()
          .duration(200)
          .attr('stroke-width', 2)
          .attr('filter', null);

        if (tooltipRef.current) {
          d3.select(tooltipRef.current).style('opacity', 0);
        }
      });

    // Add glow filter
    const defs = svg.select('defs').empty() ? svg.append('defs') : svg.select('defs');
    const filter = defs.append('filter').attr('id', 'glow');
    filter.append('feGaussianBlur').attr('stdDeviation', '3.5').attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Circle
    bubble.append('circle')
      .attr('r', d => radiusScale(d.bubble_size))
      .attr('fill', d => {
        // Parse sentiment color or use scale
        const sentiment = parseFloat(d.sentiment_color);
        return isNaN(sentiment) ? d.sentiment_color : sentimentColorScale(sentiment);
      })
      .attr('stroke', d => d.company === data.company_position.company ? '#3b82f6' : '#fff')
      .attr('stroke-width', d => d.company === data.company_position.company ? 3 : 2)
      .style('opacity', 0.8)
      .transition()
      .duration(1000)
      .style('opacity', 0.9);

    // Label
    bubble.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '.3em')
      .style('font-size', d => `${Math.max(10, radiusScale(d.bubble_size) / 4)}px`)
      .style('fill', '#fff')
      .style('font-weight', 'bold')
      .style('pointer-events', 'none')
      .text(d => d.company.slice(0, 10));

  }, [allPositions, width, height, data.company_position.company, onCompanyClick, radiusScale, sentimentColorScale]);

  // Time scrubber animation
  useEffect(() => {
    if (isPlaying && data.historical_snapshots) {
      const interval = setInterval(() => {
        setCurrentSnapshotIndex((prev) => {
          if (prev >= (data.historical_snapshots?.length || 0) - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1000);

      animationRef.current = interval as unknown as number;

      return () => clearInterval(interval);
    }
  }, [isPlaying, data.historical_snapshots]);

  return (
    <div className={`relative ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Competitive Positioning Map</h3>
          <p className="text-sm text-gray-500">Interactive view of market landscape</p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-4">
          <button
            className="p-2 border border-gray-300 rounded hover:bg-gray-50"
            title="Reset Zoom"
            onClick={() => {
              if (svgRef.current) {
                d3.select(svgRef.current).transition().duration(750).call(
                  d3.zoom<SVGSVGElement, unknown>().transform as any,
                  d3.zoomIdentity
                );
              }
            }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
            </svg>
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="border border-gray-200 rounded-lg bg-white"
      />

      {/* Tooltip */}
      <div
        ref={tooltipRef}
        className="absolute bg-gray-900 text-white px-3 py-2 rounded shadow-lg pointer-events-none opacity-0 transition-opacity duration-200 text-sm z-10"
        style={{ maxWidth: '200px' }}
      />

      {/* Time Scrubber */}
      {data.historical_snapshots && data.historical_snapshots.length > 0 && (
        <div className="mt-4 bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {isPlaying ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
              )}
            </button>

            <input
              type="range"
              min={0}
              max={(data.historical_snapshots.length || 1) - 1}
              value={currentSnapshotIndex}
              onChange={(e) => {
                setIsPlaying(false);
                setCurrentSnapshotIndex(parseInt(e.target.value));
              }}
              className="flex-1"
            />

            <span className="text-sm text-gray-600 min-w-[120px]">
              {data.historical_snapshots[currentSnapshotIndex]?.timestamp || 'Current'}
            </span>
          </div>
        </div>
      )}

      {/* Insights Panel */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* White Space Opportunities */}
        {data.white_space_opportunities.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-900 mb-2">White Space Opportunities</h4>
            <ul className="text-sm text-green-800 space-y-1">
              {data.white_space_opportunities.map((opp, idx) => (
                <li key={idx}>• {opp}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Position Threats */}
        {data.position_threats.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-semibold text-red-900 mb-2">Position Threats</h4>
            <ul className="text-sm text-red-800 space-y-1">
              {data.position_threats.map((threat, idx) => (
                <li key={idx}>• {threat}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Selected Company Details */}
      {selectedCompany && (
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-semibold text-blue-900">Selected: {selectedCompany}</h4>
              {allPositions.find(p => p.company === selectedCompany) && (
                <div className="mt-2 text-sm text-blue-800 space-y-1">
                  <div>Growth Rate: {allPositions.find(p => p.company === selectedCompany)?.x_coordinate.toFixed(1)}%</div>
                  <div>Profit Margin: {allPositions.find(p => p.company === selectedCompany)?.y_coordinate.toFixed(1)}%</div>
                  <div>Velocity: {allPositions.find(p => p.company === selectedCompany)?.velocity.toFixed(2)}</div>
                </div>
              )}
            </div>
            <button
              onClick={() => setSelectedCompany(null)}
              className="text-blue-600 hover:text-blue-800"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
