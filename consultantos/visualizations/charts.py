"""
Chart generation using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
from consultantos.models import PortersFiveForces, SWOTAnalysis


def create_porter_radar_figure(forces: PortersFiveForces) -> go.Figure:
    """Generate radar chart for Porter's 5 Forces"""
    fig = go.Figure(data=go.Scatterpolar(
        r=[
            forces.supplier_power,
            forces.buyer_power,
            forces.competitive_rivalry,
            forces.threat_of_substitutes,
            forces.threat_of_new_entrants
        ],
        theta=[
            'Supplier<br>Power',
            'Buyer<br>Power',
            'Competitive<br>Rivalry',
            'Threat of<br>Substitutes',
            'New Entrant<br>Threat'
        ],
        fill='toself',
        fillcolor='rgba(0, 123, 255, 0.3)',
        line=dict(color='rgba(0, 123, 255, 1)', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['Weak', '', 'Moderate', '', 'Strong']
            )
        ),
        title=dict(
            text="Porter's Five Forces Analysis",
            font=dict(size=18, family='Arial')
        ),
        showlegend=False,
        width=600,
        height=500
    )
    
    return fig


def create_swot_matrix_figure(swot: SWOTAnalysis) -> go.Figure:
    """Generate 2x2 SWOT matrix"""
    fig = go.Figure()
    
    # Create quadrants with text
    strengths_text = '<br>• '.join(swot.strengths[:3])
    weaknesses_text = '<br>• '.join(swot.weaknesses[:3])
    opportunities_text = '<br>• '.join(swot.opportunities[:3])
    threats_text = '<br>• '.join(swot.threats[:3])
    
    fig.add_trace(go.Scatter(
        x=[0.25, 0.75, 0.25, 0.75],
        y=[0.75, 0.75, 0.25, 0.25],
        text=[
            f'<b>STRENGTHS</b><br>{strengths_text}',
            f'<b>WEAKNESSES</b><br>{weaknesses_text}',
            f'<b>OPPORTUNITIES</b><br>{opportunities_text}',
            f'<b>THREATS</b><br>{threats_text}'
        ],
        mode='text',
        textposition='middle center',
        textfont=dict(size=11, family='Arial')
    ))
    
    # Add quadrant backgrounds
    fig.add_shape(type="rect", x0=0, x1=0.5, y0=0.5, y1=1,
                  fillcolor="rgba(144, 238, 144, 0.2)", line_width=0)
    fig.add_shape(type="rect", x0=0.5, x1=1, y0=0.5, y1=1,
                  fillcolor="rgba(255, 182, 193, 0.2)", line_width=0)
    fig.add_shape(type="rect", x0=0, x1=0.5, y0=0, y1=0.5,
                  fillcolor="rgba(173, 216, 230, 0.2)", line_width=0)
    fig.add_shape(type="rect", x0=0.5, x1=1, y0=0, y1=0.5,
                  fillcolor="rgba(255, 218, 185, 0.2)", line_width=0)
    
    # Add dividing lines
    fig.add_shape(type="line", x0=0.5, x1=0.5, y0=0, y1=1,
                  line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=0, x1=1, y0=0.5, y1=0.5,
                  line=dict(color="black", width=2))
    
    fig.update_layout(
        title="SWOT Analysis Matrix",
        xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
        width=700,
        height=600,
        showlegend=False
    )
    
    return fig


def create_trend_chart_figure(trend_data: Dict[str, Any]) -> go.Figure:
    """Generate market interest trend chart from trend_data"""
    fig = go.Figure()
    
    # Extract data from trend_data parameter
    x_data = []
    y_data = []
    
    # Try to extract time series data from trend_data
    if isinstance(trend_data, dict):
        # Check for common keys that might contain time series
        if "interest_data" in trend_data and isinstance(trend_data["interest_data"], dict):
            # Extract time/index and values
            for key, value in trend_data["interest_data"].items():
                try:
                    x_data.append(key)
                    if isinstance(value, (int, float)):
                        y_data.append(value)
                    else:
                        y_data.append(0)
                except Exception:
                    pass
        
        # Fallback: check for data_points list
        if not x_data and "data_points" in trend_data and isinstance(trend_data["data_points"], list):
            for point in trend_data["data_points"]:
                if isinstance(point, dict):
                    if "peak_date" in point:
                        x_data.append(point["peak_date"])
                    if "current_interest" in point:
                        y_data.append(point["current_interest"])
    
    # Validate and use extracted data, or fallback to empty
    if not x_data or not y_data or len(x_data) != len(y_data):
        # Fallback: empty chart with warning
        x_data = []
        y_data = []
    
    fig.add_trace(go.Scatter(
        x=x_data if x_data else [],
        y=y_data if y_data else [],
        mode='lines+markers',
        name='Search Interest'
    ))
    
    fig.update_layout(
        title='Market Interest Over Time (Google Trends)',
        xaxis_title='Time Period',
        yaxis_title='Search Interest (0-100)',
        width=800,
        height=400
    )
    
    return fig


def create_risk_heatmap_figure(risks: list, risk_heatmap: Dict[str, Any]) -> go.Figure:
    """Generate risk heatmap (likelihood vs impact)"""
    # Prepare data for heatmap
    categories = ['High Impact', 'Medium Impact', 'Low Impact']
    likelihood_levels = ['High Likelihood', 'Medium Likelihood', 'Low Likelihood']
    
    # Initialize matrix
    z_data = [[0 for _ in range(3)] for _ in range(3)]
    
    # Map risk heatmap data to matrix
    for i, likelihood in enumerate(['high', 'medium', 'low']):
        for j, impact in enumerate(['high', 'medium', 'low']):
            key = f"{likelihood}_likelihood_{impact}_impact"
            if key in risk_heatmap:
                items = risk_heatmap[key]
                if isinstance(items, list):
                    z_data[i][j] = len(items)
                elif isinstance(items, (int, float)):
                    z_data[i][j] = items
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=categories,
        y=likelihood_levels,
        colorscale='Reds',
        showscale=True,
        text=[[f"{z_data[i][j]} risks" for j in range(3)] for i in range(3)],
        texttemplate='%{text}',
        textfont={"size": 12}
    ))
    
    fig.update_layout(
        title="Risk Heatmap (Likelihood vs Impact)",
        xaxis_title="Impact",
        yaxis_title="Likelihood",
        width=600,
        height=400
    )
    
    return fig


def create_opportunity_prioritization_figure(opportunities: list) -> go.Figure:
    """Generate opportunity prioritization chart (Impact vs Feasibility)"""
    # Extract data
    impact_values = [opp.impact_potential for opp in opportunities[:10]]  # Top 10
    feasibility_values = [opp.feasibility for opp in opportunities[:10]]
    titles = [opp.title[:30] for opp in opportunities[:10]]  # Truncate titles
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=feasibility_values,
        y=impact_values,
        mode='markers+text',
        text=titles,
        textposition="top center",
        marker=dict(
            size=[opp.priority_score * 2 for opp in opportunities[:10]],
            color=[opp.priority_score for opp in opportunities[:10]],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Priority Score")
        ),
        name='Opportunities'
    ))
    
    fig.update_layout(
        title="Opportunity Prioritization (Impact vs Feasibility)",
        xaxis_title="Feasibility (1-10)",
        yaxis_title="Impact Potential (1-10)",
        width=800,
        height=600
    )
    
    return fig


def create_recommendations_timeline_figure(recommendations: Any) -> go.Figure:
    """Generate timeline visualization for recommendations"""
    timelines = ['Immediate', 'Short-term', 'Medium-term', 'Long-term']
    counts = [
        len(recommendations.immediate_actions),
        len(recommendations.short_term_actions),
        len(recommendations.medium_term_actions),
        len(recommendations.long_term_actions)
    ]
    
    fig = go.Figure(data=go.Bar(
        x=timelines,
        y=counts,
        marker_color=['#ff4444', '#ffaa00', '#00aa00', '#0066cc']
    ))
    
    fig.update_layout(
        title="Recommendations by Timeline",
        xaxis_title="Timeline",
        yaxis_title="Number of Actions",
        width=600,
        height=400
    )
    
    return fig

