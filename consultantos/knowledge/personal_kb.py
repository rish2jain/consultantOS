"""
Personal Knowledge Base - aggregate insights across all user analyses
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

from consultantos.models import (
    KnowledgeItem,
    Timeline,
    KnowledgeGraph,
    ConnectionNode,
    ConnectionEdge,
    SearchKBRequest,
    StrategicReport,
)
from consultantos.database import get_db_service
import logging

logger = logging.getLogger(__name__)


class PersonalKnowledgeBase:
    """
    Aggregate insights across all user analyses

    Creates switching costs by making user's historical data increasingly valuable
    """

    def __init__(self, db_service=None):
        self.db = db_service

    async def add_analysis(self, user_id: str, analysis: StrategicReport) -> KnowledgeItem:
        """
        Index new analysis into knowledge base

        Args:
            user_id: User ID
            analysis: Strategic report to index

        Returns:
            Created knowledge item
        """
        try:
            # Extract key insights from analysis
            key_insights = self._extract_key_insights(analysis)

            # Create knowledge item
            item = KnowledgeItem(
                id=f"kb_{user_id}_{analysis.company}_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                analysis_id=analysis.report_id if hasattr(analysis, 'report_id') else "",
                company=analysis.company,
                industry=analysis.industry,
                frameworks_used=self._extract_frameworks(analysis),
                key_insights=key_insights,
                created_at=datetime.utcnow(),
                relevance_score=1.0,  # Fresh analyses start at max relevance
            )

            # Store in database
            await self.db.add_knowledge_item(item)

            logger.info(
                "knowledge_item_added",
                user_id=user_id,
                company=analysis.company,
                insights_count=len(key_insights)
            )

            return item

        except Exception as e:
            logger.error("add_analysis_failed", user_id=user_id, error=str(e))
            raise

    async def search_kb(
        self,
        user_id: str,
        request: SearchKBRequest
    ) -> List[KnowledgeItem]:
        """
        Search across all user's analyses using semantic similarity

        Args:
            user_id: User ID
            request: Search request with query and filters

        Returns:
            Ranked list of knowledge items
        """
        try:
            # Get all user's knowledge items
            all_items = await self.db.list_knowledge_items(user_id)

            # Apply filters
            filtered_items = self._apply_filters(all_items, request.filters)

            # Rank by relevance to query
            ranked_items = self._rank_by_relevance(filtered_items, request.query)

            # Apply limit
            results = ranked_items[:request.limit]

            logger.info(
                "kb_searched",
                user_id=user_id,
                query=request.query,
                results_count=len(results)
            )

            return results

        except Exception as e:
            logger.error("search_kb_failed", user_id=user_id, error=str(e))
            raise

    async def get_timeline(
        self,
        company: str,
        user_id: str
    ) -> Timeline:
        """
        Show how analysis of company changed over time

        Args:
            company: Company name
            user_id: User ID

        Returns:
            Timeline of analyses
        """
        try:
            # Get all analyses for this company
            analyses = await self.db.list_company_analyses(user_id, company)

            # Sort by date
            analyses.sort(key=lambda x: x.created_at)

            # Extract key changes over time
            key_changes = self._identify_changes(analyses)

            # Generate trend summary
            trend_summary = self._generate_trend_summary(analyses)

            timeline = Timeline(
                company=company,
                analyses=[self._analysis_to_dict(a) for a in analyses],
                trend_summary=trend_summary,
                key_changes=key_changes,
            )

            logger.info("timeline_generated", user_id=user_id, company=company)

            return timeline

        except Exception as e:
            logger.error("get_timeline_failed", company=company, error=str(e))
            raise

    async def get_connections(
        self,
        company: str,
        user_id: str
    ) -> KnowledgeGraph:
        """
        Show connections between companies/industries user analyzed

        Args:
            company: Starting company
            user_id: User ID

        Returns:
            Knowledge graph showing connections
        """
        try:
            # Get all user's knowledge items
            all_items = await self.db.list_knowledge_items(user_id)

            # Build graph nodes and edges
            nodes = self._build_nodes(all_items)
            edges = self._build_edges(all_items, company)

            graph = KnowledgeGraph(
                nodes=nodes,
                edges=edges,
            )

            logger.info(
                "connections_built",
                user_id=user_id,
                company=company,
                nodes=len(nodes),
                edges=len(edges)
            )

            return graph

        except Exception as e:
            logger.error("get_connections_failed", company=company, error=str(e))
            raise

    # ===== Helper Methods =====

    def _extract_key_insights(self, analysis: StrategicReport) -> List[str]:
        """Extract key insights from strategic report"""
        insights = []

        # From executive summary
        if hasattr(analysis, 'executive_summary'):
            if hasattr(analysis.executive_summary, 'key_findings'):
                insights.extend(analysis.executive_summary.key_findings)

        # From frameworks
        if hasattr(analysis, 'framework_analysis'):
            # Porter's Five Forces insights
            if hasattr(analysis.framework_analysis, 'porter') and analysis.framework_analysis.porter:
                porter = analysis.framework_analysis.porter
                insights.append(f"Competitive rivalry: {porter.competitive_rivalry[:100]}")
                insights.append(f"Supplier power: {porter.supplier_power[:100]}")

            # SWOT insights
            if hasattr(analysis.framework_analysis, 'swot') and analysis.framework_analysis.swot:
                swot = analysis.framework_analysis.swot
                if swot.strengths:
                    insights.append(f"Key strength: {swot.strengths[0][:100]}")
                if swot.opportunities:
                    insights.append(f"Top opportunity: {swot.opportunities[0][:100]}")

        return insights[:10]  # Limit to top 10 insights

    def _extract_frameworks(self, analysis: StrategicReport) -> List[str]:
        """Extract frameworks used in analysis"""
        frameworks = []

        if hasattr(analysis, 'framework_analysis'):
            if hasattr(analysis.framework_analysis, 'porter') and analysis.framework_analysis.porter:
                frameworks.append("porter")
            if hasattr(analysis.framework_analysis, 'swot') and analysis.framework_analysis.swot:
                frameworks.append("swot")
            if hasattr(analysis.framework_analysis, 'pestel') and analysis.framework_analysis.pestel:
                frameworks.append("pestel")
            if hasattr(analysis.framework_analysis, 'blue_ocean') and analysis.framework_analysis.blue_ocean:
                frameworks.append("blue_ocean")

        return frameworks

    def _apply_filters(
        self,
        items: List[KnowledgeItem],
        filters: Optional[Dict[str, Any]]
    ) -> List[KnowledgeItem]:
        """Apply filters to knowledge items"""
        if not filters:
            return items

        filtered = items

        # Company filter
        if 'company' in filters:
            company = filters['company'].lower()
            filtered = [i for i in filtered if company in i.company.lower()]

        # Industry filter
        if 'industry' in filters:
            industry = filters['industry'].lower()
            filtered = [i for i in filtered if industry in i.industry.lower()]

        # Framework filter
        if 'frameworks' in filters:
            target_frameworks = set(filters['frameworks'])
            filtered = [
                i for i in filtered
                if any(f in target_frameworks for f in i.frameworks_used)
            ]

        # Date range filter
        if 'from_date' in filters:
            from_date = datetime.fromisoformat(filters['from_date'])
            filtered = [i for i in filtered if i.created_at >= from_date]

        if 'to_date' in filters:
            to_date = datetime.fromisoformat(filters['to_date'])
            filtered = [i for i in filtered if i.created_at <= to_date]

        return filtered

    def _rank_by_relevance(
        self,
        items: List[KnowledgeItem],
        query: str
    ) -> List[KnowledgeItem]:
        """Rank items by relevance to query"""
        # Simple keyword matching (could be enhanced with embeddings)
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for item in items:
            # Score based on keyword matches in insights
            matches = 0
            for insight in item.key_insights:
                insight_words = set(insight.lower().split())
                matches += len(query_words & insight_words)

            # Boost recent items
            age_days = (datetime.utcnow() - item.created_at).days
            recency_boost = max(0, 1.0 - (age_days / 365.0))

            item.relevance_score = matches + recency_boost

        # Sort by relevance
        items.sort(key=lambda x: x.relevance_score, reverse=True)

        return items

    def _identify_changes(self, analyses: List[Any]) -> List[str]:
        """Identify key changes between analyses"""
        changes = []

        if len(analyses) < 2:
            return changes

        # Compare most recent with previous
        recent = analyses[-1]
        previous = analyses[-2]

        # Framework differences
        recent_frameworks = set(self._extract_frameworks(recent))
        previous_frameworks = set(self._extract_frameworks(previous))

        new_frameworks = recent_frameworks - previous_frameworks
        if new_frameworks:
            changes.append(f"Added frameworks: {', '.join(new_frameworks)}")

        removed_frameworks = previous_frameworks - recent_frameworks
        if removed_frameworks:
            changes.append(f"Removed frameworks: {', '.join(removed_frameworks)}")

        # Time since last analysis
        time_diff = recent.created_at - previous.created_at
        changes.append(f"Time since last analysis: {time_diff.days} days")

        return changes

    def _generate_trend_summary(self, analyses: List[Any]) -> str:
        """Generate trend summary from analyses"""
        if not analyses:
            return "No analyses available"

        if len(analyses) == 1:
            return f"Single analysis of {analyses[0].company} on {analyses[0].created_at.strftime('%Y-%m-%d')}"

        first = analyses[0]
        last = analyses[-1]
        time_span = (last.created_at - first.created_at).days

        return (
            f"Analyzed {first.company} {len(analyses)} times over {time_span} days. "
            f"Most recent: {last.created_at.strftime('%Y-%m-%d')}"
        )

    def _analysis_to_dict(self, analysis: Any) -> Dict[str, Any]:
        """Convert analysis to dictionary"""
        return {
            "company": analysis.company,
            "industry": analysis.industry,
            "created_at": analysis.created_at.isoformat(),
            "frameworks": self._extract_frameworks(analysis),
        }

    def _build_nodes(self, items: List[KnowledgeItem]) -> List[ConnectionNode]:
        """Build nodes for knowledge graph"""
        # Track entities
        companies = defaultdict(int)
        industries = defaultdict(int)
        frameworks = defaultdict(int)

        for item in items:
            companies[item.company] += 1
            industries[item.industry] += 1
            for framework in item.frameworks_used:
                frameworks[framework] += 1

        nodes = []

        # Company nodes
        for company, count in companies.items():
            nodes.append(ConnectionNode(
                id=f"company:{company}",
                type="company",
                name=company,
                analysis_count=count,
            ))

        # Industry nodes
        for industry, count in industries.items():
            nodes.append(ConnectionNode(
                id=f"industry:{industry}",
                type="industry",
                name=industry,
                analysis_count=count,
            ))

        # Framework nodes
        for framework, count in frameworks.items():
            nodes.append(ConnectionNode(
                id=f"framework:{framework}",
                type="framework",
                name=framework,
                analysis_count=count,
            ))

        return nodes

    def _build_edges(
        self,
        items: List[KnowledgeItem],
        company: str
    ) -> List[ConnectionEdge]:
        """Build edges for knowledge graph"""
        edges = []

        # Company -> Industry connections
        company_industries = defaultdict(int)
        for item in items:
            if item.company == company:
                key = (f"company:{item.company}", f"industry:{item.industry}")
                company_industries[key] += 1

        for (source, target), weight in company_industries.items():
            edges.append(ConnectionEdge(
                source=source,
                target=target,
                weight=weight,
                relationship="in_industry",
            ))

        # Company -> Framework connections
        company_frameworks = defaultdict(int)
        for item in items:
            if item.company == company:
                for framework in item.frameworks_used:
                    key = (f"company:{item.company}", f"framework:{framework}")
                    company_frameworks[key] += 1

        for (source, target), weight in company_frameworks.items():
            edges.append(ConnectionEdge(
                source=source,
                target=target,
                weight=weight,
                relationship="analyzed_with",
            ))

        return edges
