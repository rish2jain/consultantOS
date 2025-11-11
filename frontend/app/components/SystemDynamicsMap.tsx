'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { motion, AnimatePresence } from 'framer-motion';
import {
  SystemDynamicsData,
  SystemNode,
  CausalLink,
  FeedbackLoop,
  LeveragePoint,
  SystemDynamicsMapProps,
} from '@/types/strategic-intelligence';

interface D3Node extends SystemNode, d3.SimulationNodeDatum {}

interface D3Link extends d3.SimulationLinkDatum<D3Node> {
  source: D3Node | string;
  target: D3Node | string;
  data: CausalLink;
}

const SystemDynamicsMap: React.FC<SystemDynamicsMapProps> = ({
  data,
  onNodeClick,
  onLeveragePointClick,
  height = 600,
  width = 800,
  simulationEnabled = false,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<SystemNode | null>(null);
  const [selectedLoop, setSelectedLoop] = useState<FeedbackLoop | null>(null);
  const [highlightedPaths, setHighlightedPaths] = useState<Set<string>>(new Set());
  const [showLeveragePoints, setShowLeveragePoints] = useState(true);
  const [activeLoops, setActiveLoops] = useState<Set<string>>(new Set());
  const simulationRef = useRef<d3.Simulation<D3Node, D3Link> | null>(null);

  const getCategoryColor = (category: string): string => {
    const colors: Record<string, string> = {
      market: '#3b82f6', // blue
      financial: '#10b981', // green
      strategic: '#8b5cf6', // purple
      operational: '#f59e0b', // amber
    };
    return colors[category] || '#6b7280'; // gray default
  };

  const getLoopColor = (loopType: string): string => {
    return loopType === 'Reinforcing' ? '#ef4444' : '#3b82f6'; // red or blue
  };

  const handleNodeHover = useCallback((node: SystemNode | null) => {
    if (!node) {
      setHighlightedPaths(new Set());
      return;
    }

    // Find all connected links
    const connectedPaths = new Set<string>();
    data.links.forEach((link) => {
      if (link.from_metric === node.metric || link.to_metric === node.metric) {
        connectedPaths.add(`${link.from_metric}-${link.to_metric}`);
      }
    });
    setHighlightedPaths(connectedPaths);
  }, [data.links]);

  const handleNodeClick = useCallback((node: SystemNode) => {
    setSelectedNode(node);
    if (onNodeClick) {
      onNodeClick(node);
    }
  }, [onNodeClick]);

  const toggleLoop = useCallback((loop: FeedbackLoop) => {
    setActiveLoops((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(loop.loop_id)) {
        newSet.delete(loop.loop_id);
      } else {
        newSet.add(loop.loop_id);
      }
      return newSet;
    });
    setSelectedLoop(loop);
  }, []);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const g = svg
      .append('g')
      .attr('class', 'main-group');

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Prepare nodes and links for D3
    const nodes: D3Node[] = data.nodes.map((node) => ({
      ...node,
      x: width / 2 + (Math.random() - 0.5) * 100,
      y: height / 2 + (Math.random() - 0.5) * 100,
    }));

    const links: D3Link[] = data.links.map((link) => ({
      source: link.from_metric,
      target: link.to_metric,
      data: link,
    }));

    // Create force simulation
    const simulation = d3
      .forceSimulation<D3Node>(nodes)
      .force('link', d3.forceLink<D3Node, D3Link>(links)
        .id((d) => d.metric)
        .distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    simulationRef.current = simulation;

    // Draw links
    const link = g
      .append('g')
      .attr('class', 'links')
      .selectAll('g')
      .data(links)
      .join('g')
      .attr('class', 'link-group');

    link
      .append('line')
      .attr('class', 'link')
      .attr('stroke', (d) => d.data.relationship_type === 'positive' ? '#10b981' : '#ef4444')
      .attr('stroke-width', (d) => 1 + (d.data.time_delay_days / 30))
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', 'url(#arrowhead)');

    // Draw nodes
    const node = g
      .append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('class', 'node-group')
      .call(d3.drag<SVGGElement, D3Node>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any);

    node
      .append('circle')
      .attr('r', 20)
      .attr('fill', (d) => getCategoryColor(d.category))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .on('mouseenter', (event, d) => handleNodeHover(d))
      .on('mouseleave', () => handleNodeHover(null))
      .on('click', (event, d) => handleNodeClick(d));

    node
      .append('text')
      .attr('dy', 35)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('fill', '#374151')
      .text((d) => d.metric.length > 15 ? d.metric.substring(0, 15) + '...' : d.metric);

    // Trend indicators
    node
      .append('text')
      .attr('dy', -25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '16px')
      .text((d) => d.trend === 'up' ? '↑' : d.trend === 'down' ? '↓' : '→');

    // Arrow markers
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-10 -10 20 20')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 8)
      .attr('markerHeight', 8)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M-8,-4 L0,0 L-8,4')
      .attr('fill', '#6b7280');

    // Simulation tick
    simulation.on('tick', () => {
      link.select('line')
        .attr('x1', (d) => (d.source as D3Node).x!)
        .attr('y1', (d) => (d.source as D3Node).y!)
        .attr('x2', (d) => (d.target as D3Node).x!)
        .attr('y2', (d) => (d.target as D3Node).y!);

      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event: any, d: D3Node) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: D3Node) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: D3Node) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return () => {
      simulation.stop();
    };
  }, [data, width, height, handleNodeHover, handleNodeClick]);

  // Highlight active loops
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('.loop-highlight').remove();

    activeLoops.forEach((loopId) => {
      const loop = data.feedback_loops.find((l) => l.loop_id === loopId);
      if (!loop) return;

      const g = svg.select('.main-group');

      // Draw loop path
      loop.links.forEach((link) => {
        g.append('line')
          .attr('class', 'loop-highlight')
          .attr('stroke', getLoopColor(loop.loop_type))
          .attr('stroke-width', 3)
          .attr('stroke-opacity', 0.4)
          .attr('x1', data.nodes.find((n) => n.metric === link.from_metric)?.x || 0)
          .attr('y1', data.nodes.find((n) => n.metric === link.from_metric)?.y || 0)
          .attr('x2', data.nodes.find((n) => n.metric === link.to_metric)?.x || 0)
          .attr('y2', data.nodes.find((n) => n.metric === link.to_metric)?.y || 0);
      });
    });
  }, [activeLoops, data]);

  return (
    <div className="w-full h-full bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-900">System Dynamics Map</h2>

        <div className="flex gap-2">
          <button
            onClick={() => setShowLeveragePoints(!showLeveragePoints)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              showLeveragePoints
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Leverage Points
          </button>

          {simulationEnabled && (
            <button
              onClick={() => {
                if (simulationRef.current) {
                  simulationRef.current.alpha(0.3).restart();
                }
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Reset Simulation
            </button>
          )}
        </div>
      </div>

      <div className="flex gap-4">
        {/* Main visualization */}
        <div className="flex-1">
          <svg
            ref={svgRef}
            width={width}
            height={height}
            className="border border-gray-200 rounded-lg"
          />
        </div>

        {/* Side panel */}
        <div className="w-80 space-y-4">
          {/* Legend */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Legend</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-blue-500" />
                <span>Market</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-green-500" />
                <span>Financial</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-purple-500" />
                <span>Strategic</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-amber-500" />
                <span>Operational</span>
              </div>
              <div className="border-t pt-2 mt-2">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-8 h-0.5 bg-green-500" />
                  <span>Positive (+)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-0.5 bg-red-500" />
                  <span>Negative (−)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Feedback Loops */}
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            <h3 className="font-semibold text-gray-900 mb-3">Feedback Loops</h3>
            <div className="space-y-2">
              {data.feedback_loops.map((loop) => (
                <button
                  key={loop.loop_id}
                  onClick={() => toggleLoop(loop)}
                  className={`w-full text-left p-2 rounded-lg text-sm transition-colors ${
                    activeLoops.has(loop.loop_id)
                      ? loop.loop_type === 'Reinforcing'
                        ? 'bg-red-100 border-2 border-red-400'
                        : 'bg-blue-100 border-2 border-blue-400'
                      : 'bg-white border border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">
                      {loop.loop_type === 'Reinforcing' ? '🔴' : '🔵'} {loop.loop_id}
                    </span>
                    <span className="text-xs text-gray-500">
                      {loop.cycle_time_days}d
                    </span>
                  </div>
                  {loop.description && (
                    <p className="text-xs text-gray-600 mt-1">{loop.description}</p>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Leverage Points */}
          {showLeveragePoints && (
            <div className="bg-purple-50 rounded-lg p-4 max-h-64 overflow-y-auto">
              <h3 className="font-semibold text-gray-900 mb-3">Leverage Points</h3>
              <div className="space-y-2">
                {data.leverage_points
                  .sort((a, b) => b.impact_score - a.impact_score)
                  .map((point, idx) => (
                    <button
                      key={idx}
                      onClick={() => onLeveragePointClick?.(point)}
                      className="w-full text-left p-3 bg-white rounded-lg border border-purple-200 hover:border-purple-400 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-sm">{point.intervention}</span>
                        <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                          Impact: {point.impact_score}/10
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">{point.expected_outcome}</p>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>ROI: {point.roi.toFixed(1)}x</span>
                        <span>${(point.cost_estimate / 1000).toFixed(0)}K</span>
                      </div>
                    </button>
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Node detail modal */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setSelectedNode(null)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold text-gray-900 mb-4">{selectedNode.metric}</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Category</span>
                  <span className="font-medium capitalize">{selectedNode.category}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Current Value</span>
                  <span className="font-medium">{selectedNode.value.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Trend</span>
                  <span className="font-medium">
                    {selectedNode.trend === 'up' ? '↑ Increasing' :
                     selectedNode.trend === 'down' ? '↓ Decreasing' :
                     '→ Stable'}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="mt-6 w-full bg-gray-900 text-white py-2 rounded-lg hover:bg-gray-800 transition-colors"
              >
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SystemDynamicsMap;
