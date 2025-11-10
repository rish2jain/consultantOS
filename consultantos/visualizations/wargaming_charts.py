"""
Wargaming visualization charts.

Provides charts for:
- Probability distribution histograms
- Tornado diagrams (sensitivity analysis)
- Decision trees
- Risk heatmaps
- Cumulative distribution functions
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Optional, Any
import logging

from consultantos.models.wargaming import (
    SimulationResult,
    SensitivityAnalysis,
    DecisionTree,
    DecisionNode,
)

logger = logging.getLogger(__name__)


def create_distribution_chart(
    simulation: SimulationResult,
    title: str = "Monte Carlo Simulation Results",
    show_stats: bool = True,
) -> go.Figure:
    """
    Create probability distribution histogram.

    Args:
        simulation: Simulation results
        title: Chart title
        show_stats: Show statistics annotations

    Returns:
        Plotly figure
    """
    if not simulation.distribution:
        logger.warning("No distribution data available for chart")
        return go.Figure()

    fig = go.Figure()

    # Histogram
    fig.add_trace(
        go.Histogram(
            x=simulation.distribution,
            nbinsx=50,
            name="Distribution",
            marker_color="rgba(0, 123, 255, 0.6)",
            marker_line_width=1,
            marker_line_color="rgba(0, 123, 255, 1.0)",
        )
    )

    # Add vertical lines for key statistics
    if show_stats:
        # Mean
        fig.add_vline(
            x=simulation.mean,
            line_dash="solid",
            line_color="green",
            annotation_text=f"Mean: ${simulation.mean:,.0f}",
            annotation_position="top",
        )

        # Median
        fig.add_vline(
            x=simulation.median,
            line_dash="dash",
            line_color="blue",
            annotation_text=f"Median: ${simulation.median:,.0f}",
            annotation_position="top",
        )

        # 10th and 90th percentiles
        fig.add_vline(
            x=simulation.percentiles["p10"],
            line_dash="dot",
            line_color="red",
            annotation_text=f"P10: ${simulation.percentiles['p10']:,.0f}",
            annotation_position="bottom left",
        )

        fig.add_vline(
            x=simulation.percentiles["p90"],
            line_dash="dot",
            line_color="red",
            annotation_text=f"P90: ${simulation.percentiles['p90']:,.0f}",
            annotation_position="bottom right",
        )

    fig.update_layout(
        title=title,
        xaxis_title="Outcome Value ($)",
        yaxis_title="Frequency",
        showlegend=False,
        hovermode="x unified",
        template="plotly_white",
    )

    return fig


def create_tornado_diagram(
    sensitivity: SensitivityAnalysis,
    title: str = "Sensitivity Analysis - Key Drivers",
    top_n: int = 10,
) -> go.Figure:
    """
    Create tornado diagram for sensitivity analysis.

    Args:
        sensitivity: Sensitivity analysis results
        title: Chart title
        top_n: Number of top variables to show

    Returns:
        Plotly figure
    """
    # Get top N variables by impact
    variables = sensitivity.rank_order[:top_n]
    impacts = [
        sensitivity.variable_impacts[var]["impact_score"] for var in variables
    ]

    # Create horizontal bar chart
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=variables,
            x=impacts,
            orientation="h",
            marker_color=px.colors.sequential.Blues_r,
            text=[f"{impact:.1f}%" for impact in impacts],
            textposition="outside",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Impact on Outcome Variance (%)",
        yaxis_title="Variable",
        yaxis=dict(autorange="reversed"),  # Highest impact at top
        showlegend=False,
        template="plotly_white",
        height=max(400, len(variables) * 40),  # Scale height with number of vars
    )

    return fig


def create_cdf_chart(
    simulation: SimulationResult,
    title: str = "Cumulative Distribution Function",
    show_percentiles: bool = True,
) -> go.Figure:
    """
    Create cumulative distribution function chart.

    Args:
        simulation: Simulation results
        title: Chart title
        show_percentiles: Show key percentile markers

    Returns:
        Plotly figure
    """
    if not simulation.distribution:
        logger.warning("No distribution data available for CDF")
        return go.Figure()

    # Sort values for CDF
    sorted_values = np.sort(simulation.distribution)
    cdf = np.arange(1, len(sorted_values) + 1) / len(sorted_values)

    fig = go.Figure()

    # CDF line
    fig.add_trace(
        go.Scatter(
            x=sorted_values,
            y=cdf,
            mode="lines",
            name="CDF",
            line=dict(color="blue", width=2),
        )
    )

    # Add percentile markers
    if show_percentiles:
        percentile_levels = [10, 25, 50, 75, 90]
        for p in percentile_levels:
            value = simulation.percentiles[f"p{p}"]
            fig.add_scatter(
                x=[value],
                y=[p / 100],
                mode="markers",
                marker=dict(size=8, color="red"),
                name=f"P{p}",
                showlegend=False,
            )
            fig.add_annotation(
                x=value,
                y=p / 100,
                text=f"P{p}: ${value:,.0f}",
                showarrow=True,
                arrowhead=2,
                ax=40,
                ay=-20 if p < 50 else 20,
            )

    fig.update_layout(
        title=title,
        xaxis_title="Outcome Value ($)",
        yaxis_title="Cumulative Probability",
        yaxis=dict(tickformat=".0%"),
        template="plotly_white",
        hovermode="x unified",
    )

    return fig


def create_decision_tree_chart(
    decision_tree: DecisionTree,
    title: str = "Strategic Decision Tree",
) -> go.Figure:
    """
    Create decision tree visualization.

    Args:
        decision_tree: Decision tree structure
        title: Chart title

    Returns:
        Plotly figure
    """
    # Build tree layout
    positions = _calculate_tree_positions(decision_tree)

    # Create edges
    edge_x = []
    edge_y = []

    for node_id, node in decision_tree.nodes.items():
        if not node.children:
            continue

        parent_pos = positions[node_id]
        for child_id in node.children:
            child_pos = positions[child_id]

            # Add edge
            edge_x.extend([parent_pos[0], child_pos[0], None])
            edge_y.extend([parent_pos[1], child_pos[1], None])

    # Create nodes
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []

    for node_id, node in decision_tree.nodes.items():
        pos = positions[node_id]
        node_x.append(pos[0])
        node_y.append(pos[1])

        # Node label
        if node.type == "decision":
            label = "Decision"
            color = "blue"
            size = 20
        elif node.type == "chance":
            label = "Chance"
            color = "orange"
            size = 15
        else:  # outcome
            label = f"${node.value:,.0f}" if node.value else "Outcome"
            color = "green" if (node.value or 0) > 0 else "red"
            size = 12

        if node.expected_value is not None:
            label += f"<br>EV: ${node.expected_value:,.0f}"

        node_text.append(label)
        node_colors.append(color)
        node_sizes.append(size)

    fig = go.Figure()

    # Add edges
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(color="gray", width=1),
            showlegend=False,
            hoverinfo="none",
        )
    )

    # Add nodes
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker=dict(size=node_sizes, color=node_colors, line_width=2),
            text=node_text,
            textposition="top center",
            showlegend=False,
            hoverinfo="text",
        )
    )

    fig.update_layout(
        title=title,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        template="plotly_white",
        height=600,
    )

    return fig


def _calculate_tree_positions(
    tree: DecisionTree,
) -> Dict[str, tuple[float, float]]:
    """
    Calculate positions for tree nodes using layered layout.

    Args:
        tree: Decision tree

    Returns:
        Dictionary mapping node IDs to (x, y) positions
    """
    positions = {}

    # Calculate depth of each node
    depths = {}
    _calculate_depths(tree.nodes, tree.root_id, depths, 0)

    # Group nodes by depth
    layers = {}
    for node_id, depth in depths.items():
        if depth not in layers:
            layers[depth] = []
        layers[depth].append(node_id)

    # Assign positions
    max_depth = max(layers.keys())

    for depth, nodes in layers.items():
        y = max_depth - depth  # Top to bottom
        num_nodes = len(nodes)

        for i, node_id in enumerate(nodes):
            # Spread nodes horizontally within layer
            x = (i + 1) / (num_nodes + 1)
            positions[node_id] = (x, y)

    return positions


def _calculate_depths(
    nodes: Dict[str, DecisionNode],
    node_id: str,
    depths: Dict[str, int],
    current_depth: int,
) -> None:
    """Recursively calculate depth of each node."""
    depths[node_id] = current_depth

    node = nodes[node_id]
    for child_id in node.children:
        _calculate_depths(nodes, child_id, depths, current_depth + 1)


def create_risk_heatmap(
    scenarios: Dict[str, Dict[str, float]],
    title: str = "Risk-Return Analysis",
) -> go.Figure:
    """
    Create risk-return heatmap for scenario comparison.

    Args:
        scenarios: Dictionary of scenario metrics
            Format: {scenario_name: {"expected_return": float, "volatility": float}}
        title: Chart title

    Returns:
        Plotly figure
    """
    scenario_names = list(scenarios.keys())
    returns = [scenarios[s]["expected_return"] for s in scenario_names]
    volatilities = [scenarios[s]["volatility"] for s in scenario_names]

    fig = go.Figure()

    # Scatter plot with bubble size for Sharpe ratio
    sharpe_ratios = [
        r / v if v > 0 else 0 for r, v in zip(returns, volatilities)
    ]

    fig.add_trace(
        go.Scatter(
            x=volatilities,
            y=returns,
            mode="markers+text",
            marker=dict(
                size=[max(10, s * 20) for s in sharpe_ratios],
                color=sharpe_ratios,
                colorscale="RdYlGn",
                showscale=True,
                colorbar=dict(title="Sharpe<br>Ratio"),
            ),
            text=scenario_names,
            textposition="top center",
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Return: $%{y:,.0f}<br>"
                "Risk: $%{x:,.0f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Risk (Volatility)",
        yaxis_title="Expected Return ($)",
        template="plotly_white",
        hovermode="closest",
    )

    return fig


def create_comparison_chart(
    scenarios: Dict[str, Any],
    metric: str = "expected_value",
    title: Optional[str] = None,
) -> go.Figure:
    """
    Create bar chart comparing scenarios on a specific metric.

    Args:
        scenarios: Dictionary of scenario results
        metric: Metric to compare (e.g., "expected_value", "win_probability")
        title: Chart title (auto-generated if None)

    Returns:
        Plotly figure
    """
    scenario_names = list(scenarios.keys())
    values = [scenarios[s].get(metric, 0) for s in scenario_names]

    # Sort by value
    sorted_pairs = sorted(zip(scenario_names, values), key=lambda x: x[1], reverse=True)
    scenario_names, values = zip(*sorted_pairs) if sorted_pairs else ([], [])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=list(scenario_names),
            y=list(values),
            marker_color=px.colors.sequential.Blues_r,
            text=[f"{v:,.0f}" if v > 1000 else f"{v:.2%}" for v in values],
            textposition="outside",
        )
    )

    if title is None:
        title = f"Scenario Comparison - {metric.replace('_', ' ').title()}"

    fig.update_layout(
        title=title,
        xaxis_title="Scenario",
        yaxis_title=metric.replace("_", " ").title(),
        showlegend=False,
        template="plotly_white",
    )

    return fig
