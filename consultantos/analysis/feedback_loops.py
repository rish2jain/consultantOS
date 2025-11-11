"""
Feedback loop detection and system dynamics analysis.

Implements sophisticated algorithms for detecting causal relationships,
feedback loops, and leverage points in business systems.
"""
import logging
from typing import List, Dict, Tuple, Optional, Set
import numpy as np
from scipy import stats
from scipy.sparse import csgraph

from consultantos.models.systems import (
    CausalLink,
    FeedbackLoop,
    LeveragePoint,
    SystemDynamicsAnalysis,
    LoopType,
)

logger = logging.getLogger(__name__)


class FeedbackLoopDetector:
    """
    Detects feedback loops and analyzes system dynamics.

    Uses correlation analysis, graph algorithms, and Meadows' leverage point
    framework to identify system structure and intervention opportunities.
    """

    def __init__(self, min_correlation: float = 0.5, min_confidence: float = 0.6):
        """
        Initialize detector.

        Args:
            min_correlation: Minimum correlation coefficient for causal links (0-1)
            min_confidence: Minimum confidence threshold for loop detection (0-1)
        """
        self.min_correlation = min_correlation
        self.min_confidence = min_confidence

    def detect_causal_links(
        self,
        time_series_data: Dict[str, List[float]],
        metric_names: List[str]
    ) -> List[CausalLink]:
        """
        Detect causal relationships between metrics using correlation and time-lag analysis.

        Args:
            time_series_data: Dict mapping metric names to time series values
            metric_names: List of metric names to analyze

        Returns:
            List of detected causal links with strength and polarity

        Raises:
            ValueError: If data is insufficient or invalid
        """
        if not time_series_data or not metric_names:
            raise ValueError("Time series data and metric names are required")

        causal_links = []

        # Analyze all pairs of metrics
        for i, from_metric in enumerate(metric_names):
            for to_metric in metric_names[i + 1:]:
                if from_metric == to_metric:
                    continue

                # Get data series
                from_series = time_series_data.get(from_metric, [])
                to_series = time_series_data.get(to_metric, [])

                if len(from_series) < 3 or len(to_series) < 3:
                    logger.debug(f"Insufficient data for {from_metric} → {to_metric}")
                    continue

                # Ensure equal length
                min_len = min(len(from_series), len(to_series))
                from_series = from_series[:min_len]
                to_series = to_series[:min_len]

                # Calculate correlation
                try:
                    correlation, p_value = stats.pearsonr(from_series, to_series)
                except Exception as e:
                    logger.warning(f"Correlation calculation failed: {e}")
                    continue

                # Check if correlation is significant
                if abs(correlation) >= self.min_correlation and p_value < 0.05:
                    # Determine polarity and delay
                    polarity = "+" if correlation > 0 else "-"
                    strength = abs(correlation) * 100

                    # Estimate time delay (simplified - could use cross-correlation)
                    delay = self._estimate_delay(from_series, to_series)

                    # Create causal link
                    link = CausalLink(
                        from_element=from_metric,
                        to_element=to_metric,
                        polarity=polarity,
                        strength=strength,
                        delay=delay,
                        description=f"{from_metric} {'increases' if polarity == '+' else 'decreases'} {to_metric} (r={correlation:.2f})"
                    )
                    causal_links.append(link)

        logger.info(f"Detected {len(causal_links)} causal links")
        return causal_links

    def _estimate_delay(self, from_series: List[float], to_series: List[float]) -> str:
        """
        Estimate time delay between two series.

        Args:
            from_series: Source metric time series
            to_series: Target metric time series

        Returns:
            Delay category: none/short/medium/long
        """
        try:
            # Simple approach: check if correlation improves with lag
            correlations = []
            for lag in range(min(5, len(from_series) // 2)):
                if lag == 0:
                    corr, _ = stats.pearsonr(from_series, to_series)
                else:
                    corr, _ = stats.pearsonr(from_series[:-lag], to_series[lag:])
                correlations.append(abs(corr))

            # Find optimal lag
            optimal_lag = np.argmax(correlations)

            if optimal_lag == 0:
                return "none"
            elif optimal_lag == 1:
                return "short"
            elif optimal_lag <= 3:
                return "medium"
            else:
                return "long"
        except Exception as e:
            logger.debug(f"Delay estimation failed: {e}")
            return "unknown"

    def detect_feedback_loops(
        self,
        causal_links: List[CausalLink],
        metric_names: List[str]
    ) -> Tuple[List[FeedbackLoop], List[FeedbackLoop]]:
        """
        Detect feedback loops (both reinforcing and balancing) using graph cycle detection.

        Args:
            causal_links: List of causal relationships
            metric_names: List of all metrics

        Returns:
            Tuple of (reinforcing_loops, balancing_loops)
        """
        if not causal_links:
            return [], []

        # Build adjacency matrix for graph analysis
        n = len(metric_names)
        metric_index = {name: i for i, name in enumerate(metric_names)}
        adj_matrix = np.zeros((n, n))
        polarity_matrix = np.zeros((n, n))  # 1 for +, -1 for -

        for link in causal_links:
            if link.from_element in metric_index and link.to_element in metric_index:
                i = metric_index[link.from_element]
                j = metric_index[link.to_element]
                adj_matrix[i][j] = link.strength
                polarity_matrix[i][j] = 1 if link.polarity == "+" else -1

        # Find cycles using DFS
        cycles = self._find_cycles(adj_matrix, metric_names)

        reinforcing_loops = []
        balancing_loops = []

        for idx, cycle in enumerate(cycles):
            if len(cycle) < 2:
                continue

            # Calculate loop polarity (product of all link polarities)
            loop_polarity = 1
            loop_strength = 1.0
            cycle_links = []

            for i in range(len(cycle)):
                from_elem = cycle[i]
                to_elem = cycle[(i + 1) % len(cycle)]

                from_idx = metric_index[from_elem]
                to_idx = metric_index[to_elem]

                if adj_matrix[from_idx][to_idx] > 0:
                    loop_polarity *= polarity_matrix[from_idx][to_idx]
                    loop_strength *= (adj_matrix[from_idx][to_idx] / 100)

                    # Find the actual link
                    for link in causal_links:
                        if link.from_element == from_elem and link.to_element == to_elem:
                            cycle_links.append(link)
                            break

            # Normalize loop strength
            loop_strength = (loop_strength ** (1 / len(cycle))) * 100

            # Determine loop type
            loop_type = LoopType.REINFORCING if loop_polarity > 0 else LoopType.BALANCING

            # Create feedback loop
            loop = FeedbackLoop(
                loop_id=f"{'R' if loop_type == LoopType.REINFORCING else 'B'}{idx + 1}",
                loop_name=f"{'Reinforcing' if loop_type == LoopType.REINFORCING else 'Balancing'} loop {idx + 1}",
                loop_type=loop_type,
                elements=cycle,
                causal_links=cycle_links,
                strength=loop_strength,
                dominant=False,  # Will be determined later
                time_constant=self._estimate_loop_time_constant(cycle_links),
                current_state="stable",  # Would need historical data to determine
                impact=f"{'Amplifies' if loop_type == LoopType.REINFORCING else 'Stabilizes'} system behavior",
                intervention_points=self._identify_intervention_points(cycle, cycle_links)
            )

            if loop_type == LoopType.REINFORCING:
                reinforcing_loops.append(loop)
            else:
                balancing_loops.append(loop)

        # Identify dominant loop
        all_loops = reinforcing_loops + balancing_loops
        if all_loops:
            dominant = max(all_loops, key=lambda x: x.strength)
            dominant.dominant = True

        logger.info(f"Detected {len(reinforcing_loops)} reinforcing loops, {len(balancing_loops)} balancing loops")

        return reinforcing_loops, balancing_loops

    def _find_cycles(self, adj_matrix: np.ndarray, metric_names: List[str]) -> List[List[str]]:
        """
        Find all cycles in directed graph using DFS.

        Args:
            adj_matrix: Adjacency matrix
            metric_names: Names of nodes

        Returns:
            List of cycles (each cycle is a list of metric names)
        """
        n = len(metric_names)
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: int, path: List[int]):
            """Depth-first search to find cycles"""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            # Check all neighbors
            for neighbor in range(n):
                if adj_matrix[node][neighbor] > 0:
                    if neighbor not in visited:
                        dfs(neighbor, path[:])
                    elif neighbor in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(neighbor)
                        cycle_indices = path[cycle_start:]
                        cycle_names = [metric_names[i] for i in cycle_indices]
                        if len(cycle_names) >= 2 and cycle_names not in cycles:
                            cycles.append(cycle_names)

            rec_stack.remove(node)

        # Run DFS from each node
        for i in range(n):
            if i not in visited:
                dfs(i, [])

        # Limit to reasonable number of cycles
        return cycles[:20]

    def _estimate_loop_time_constant(self, links: List[CausalLink]) -> str:
        """
        Estimate how fast a loop operates based on link delays.

        Args:
            links: Causal links in the loop

        Returns:
            Time constant description
        """
        if not links:
            return "unknown"

        delay_scores = {"none": 0, "short": 1, "medium": 2, "long": 3, "unknown": 2}
        avg_delay = np.mean([delay_scores.get(link.delay, 2) for link in links])

        if avg_delay < 0.5:
            return "days to weeks"
        elif avg_delay < 1.5:
            return "weeks to months"
        elif avg_delay < 2.5:
            return "months to quarters"
        else:
            return "quarters to years"

    def _identify_intervention_points(
        self,
        cycle: List[str],
        links: List[CausalLink]
    ) -> List[str]:
        """
        Identify best intervention points in a loop.

        Args:
            cycle: Metrics in the loop
            links: Causal links

        Returns:
            List of intervention suggestions
        """
        interventions = []

        # Find weakest link (easiest to modify)
        if links:
            weakest = min(links, key=lambda x: x.strength)
            interventions.append(f"Strengthen/weaken link: {weakest.from_element} → {weakest.to_element}")

        # Find strongest element (highest leverage)
        if len(links) >= 2:
            # Element with most connections
            element_counts = {}
            for link in links:
                element_counts[link.from_element] = element_counts.get(link.from_element, 0) + 1
                element_counts[link.to_element] = element_counts.get(link.to_element, 0) + 1

            if element_counts:
                hub = max(element_counts, key=element_counts.get)
                interventions.append(f"Intervene at hub: {hub}")

        return interventions or ["Analyze individual elements for leverage points"]

    def identify_leverage_points(
        self,
        loops: List[FeedbackLoop],
        company: str,
        industry: str
    ) -> List[LeveragePoint]:
        """
        Identify leverage points using Meadows' hierarchy.

        Args:
            loops: Detected feedback loops
            company: Company name
            industry: Industry context

        Returns:
            List of leverage points ranked by potential impact
        """
        leverage_points = []
        lp_id = 1

        # Level 9: Constants, parameters (easy to change, low leverage)
        for loop in loops:
            if loop.loop_type == LoopType.BALANCING and loop.dominant:
                leverage_points.append(
                    LeveragePoint(
                        leverage_id=f"lp_{lp_id:03d}",
                        leverage_name=f"Adjust parameters in {loop.loop_name}",
                        leverage_level=9,
                        description=f"Fine-tune variables in balancing loop: {', '.join(loop.elements[:3])}",
                        current_state="Standard parameter settings",
                        proposed_intervention="Optimize parameter values for efficiency",
                        impact_potential=40.0,
                        implementation_difficulty=20.0,
                        time_to_impact="1-3 months",
                        strategic_priority="medium",
                        dependencies=[]
                    )
                )
                lp_id += 1

        # Level 6: Information flows (medium leverage)
        for loop in loops:
            leverage_points.append(
                LeveragePoint(
                    leverage_id=f"lp_{lp_id:03d}",
                    leverage_name=f"Improve information flow in {loop.loop_name}",
                    leverage_level=6,
                    description=f"Enhance feedback mechanisms in loop involving: {', '.join(loop.elements[:3])}",
                    current_state="Information delays present",
                    proposed_intervention="Reduce information delays, improve transparency",
                    impact_potential=65.0,
                    implementation_difficulty=45.0,
                    time_to_impact="3-6 months",
                    strategic_priority="high",
                    dependencies=[]
                )
            )
            lp_id += 1
            if lp_id > 10:  # Limit number of leverage points
                break

        # Level 3: Goal of the system (high leverage)
        if loops:
            dominant_loop = next((l for l in loops if l.dominant), loops[0])
            leverage_points.append(
                LeveragePoint(
                    leverage_id=f"lp_{lp_id:03d}",
                    leverage_name="Redefine system goals and incentives",
                    leverage_level=3,
                    description=f"Align goals with long-term value creation in {industry}",
                    current_state="Current goals may drive suboptimal behavior",
                    proposed_intervention="Redesign incentive structures and KPIs",
                    impact_potential=85.0,
                    implementation_difficulty=70.0,
                    time_to_impact="6-12 months",
                    strategic_priority="critical",
                    dependencies=[]
                )
            )
            lp_id += 1

        # Level 2: Paradigm (very high leverage)
        leverage_points.append(
            LeveragePoint(
                leverage_id=f"lp_{lp_id:03d}",
                leverage_name="Shift organizational paradigm",
                leverage_level=2,
                description=f"Transform {company}'s fundamental worldview and assumptions",
                current_state="Operating under current industry paradigm",
                proposed_intervention="Challenge assumptions, reframe problems, shift mental models",
                impact_potential=95.0,
                implementation_difficulty=85.0,
                time_to_impact="12-24 months",
                strategic_priority="critical",
                dependencies=[]
            )
        )

        # Sort by impact potential / difficulty (ROI)
        leverage_points.sort(
            key=lambda x: x.impact_potential / max(x.implementation_difficulty, 1),
            reverse=True
        )

        return leverage_points

    def analyze_system(
        self,
        time_series_data: Dict[str, List[float]],
        metric_names: List[str],
        company: str,
        industry: str
    ) -> SystemDynamicsAnalysis:
        """
        Perform complete system dynamics analysis.

        Args:
            time_series_data: Historical metric data
            metric_names: List of metric names
            company: Company name
            industry: Industry

        Returns:
            Complete system dynamics analysis

        Raises:
            ValueError: If inputs are invalid
        """
        logger.info(f"Starting system dynamics analysis for {company}")

        try:
            # Step 1: Detect causal links
            causal_links = self.detect_causal_links(time_series_data, metric_names)

            # Step 2: Detect feedback loops
            reinforcing_loops, balancing_loops = self.detect_feedback_loops(
                causal_links,
                metric_names
            )

            # Step 3: Identify leverage points
            all_loops = reinforcing_loops + balancing_loops
            leverage_points = self.identify_leverage_points(all_loops, company, industry)

            # Step 4: Determine dominant loop and system archetype
            dominant_loop_id = None
            system_archetype = None

            if all_loops:
                dominant = next((l for l in all_loops if l.dominant), all_loops[0])
                dominant_loop_id = dominant.loop_id

                # Classify system archetype
                if len(reinforcing_loops) > len(balancing_loops):
                    if any(l.dominant for l in reinforcing_loops):
                        system_archetype = "success to the successful"
                    else:
                        system_archetype = "escalation"
                elif balancing_loops:
                    system_archetype = "limits to growth"
                else:
                    system_archetype = "unknown"

            # Step 5: Generate strategic insights
            structural_issues = self._identify_structural_issues(all_loops)
            quick_fixes = self._identify_quick_fixes_to_avoid(all_loops)
            fundamental_solutions = self._identify_fundamental_solutions(
                leverage_points,
                all_loops
            )

            # Step 6: Calculate confidence
            confidence = self._calculate_confidence(
                causal_links,
                all_loops,
                time_series_data
            )

            return SystemDynamicsAnalysis(
                company=company,
                industry=industry,
                key_variables=metric_names,
                causal_links=causal_links,
                reinforcing_loops=reinforcing_loops,
                balancing_loops=balancing_loops,
                dominant_loop=dominant_loop_id,
                leverage_points=leverage_points,
                high_leverage_interventions=[lp.leverage_name for lp in leverage_points[:3]],
                system_archetype=system_archetype,
                current_behavior=self._describe_current_behavior(all_loops),
                unintended_consequences=self._predict_unintended_consequences(all_loops),
                structural_issues=structural_issues,
                quick_fixes_to_avoid=quick_fixes,
                fundamental_solutions=fundamental_solutions,
                confidence_score=confidence,
                data_sources=["time_series_analysis", "correlation_analysis", "graph_theory"]
            )

        except Exception as e:
            logger.error(f"System dynamics analysis failed: {e}")
            raise

    def _identify_structural_issues(self, loops: List[FeedbackLoop]) -> List[str]:
        """Identify structural problems in the system"""
        issues = []

        vicious_cycles = [l for l in loops if l.loop_type == LoopType.REINFORCING and "declining" in l.current_state]
        if vicious_cycles:
            issues.append(f"Vicious cycles detected in {len(vicious_cycles)} loops")

        strong_balancing = [l for l in loops if l.loop_type == LoopType.BALANCING and l.strength > 70]
        if strong_balancing:
            issues.append("Strong balancing forces may limit growth")

        return issues or ["No major structural issues detected"]

    def _identify_quick_fixes_to_avoid(self, loops: List[FeedbackLoop]) -> List[str]:
        """Identify tempting but ineffective interventions"""
        return [
            "Treating symptoms without addressing root causes",
            "Short-term optimizations that weaken long-term loops",
            "Focusing on parameters instead of system structure"
        ]

    def _identify_fundamental_solutions(
        self,
        leverage_points: List[LeveragePoint],
        loops: List[FeedbackLoop]
    ) -> List[str]:
        """Identify fundamental solutions from leverage points"""
        return [lp.proposed_intervention for lp in leverage_points[:3]]

    def _describe_current_behavior(self, loops: List[FeedbackLoop]) -> str:
        """Describe overall system behavior"""
        if not loops:
            return "Insufficient data for behavior analysis"

        reinforcing = sum(1 for l in loops if l.loop_type == LoopType.REINFORCING)
        balancing = len(loops) - reinforcing

        if reinforcing > balancing * 1.5:
            return "System dominated by reinforcing dynamics - potential for rapid change"
        elif balancing > reinforcing * 1.5:
            return "System dominated by balancing forces - resistance to change"
        else:
            return "Mixed dynamics - system behavior depends on which loops dominate"

    def _predict_unintended_consequences(self, loops: List[FeedbackLoop]) -> List[str]:
        """Predict potential unintended consequences"""
        consequences = []

        for loop in loops:
            if loop.loop_type == LoopType.REINFORCING and loop.strength > 70:
                consequences.append(
                    f"Strong reinforcing loop ({loop.loop_name}) may cause overshooting or instability"
                )

        return consequences or ["Monitor for delayed feedback effects"]

    def _calculate_confidence(
        self,
        causal_links: List[CausalLink],
        loops: List[FeedbackLoop],
        time_series_data: Dict[str, List[float]]
    ) -> float:
        """Calculate overall confidence in analysis"""
        # Base confidence on data quality and quantity
        avg_data_points = np.mean([len(v) for v in time_series_data.values()])

        data_quality_score = min(avg_data_points / 50, 1.0) * 40  # 40 points max

        # Confidence from number of detected structures
        structure_score = min(len(causal_links) / 20, 1.0) * 30  # 30 points max
        loop_score = min(len(loops) / 5, 1.0) * 30  # 30 points max

        return min(data_quality_score + structure_score + loop_score, 100.0)
