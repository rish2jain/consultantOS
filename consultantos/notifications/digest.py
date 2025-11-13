"""
Email digest and alerts system for user notifications
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from consultantos.models import (
    DigestPreferences,
    DigestContent,
    DigestFrequency,
    Alert,
)
from consultantos.database import get_db_service
from consultantos.services.email_service import get_email_service
import logging

logger = logging.getLogger(__name__)


class DigestGenerator:
    """
    Generate and send email digests to users
    """

    def __init__(self, db_service=None):
        self.db = db_service or get_db_service()

    async def generate_weekly_digest(self, user_id: str) -> DigestContent:
        """
        Create weekly digest of all monitored companies

        Args:
            user_id: User ID

        Returns:
            Digest content
        """
        try:
            # Calculate period
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=7)

            # Get user preferences
            prefs = await self.db.get_digest_preferences(user_id)
            if not prefs:
                prefs = DigestPreferences(
                    user_id=user_id,
                    frequency=DigestFrequency.WEEKLY
                )

            # Initialize digest
            digest = DigestContent(
                user_id=user_id,
                period_start=period_start,
                period_end=period_end,
                monitored_companies=[],
                team_activity=[],
                kb_insights=[],
                alerts=[],
            )

            # Monitored companies (from auto-run saved searches)
            if prefs.include_monitored:
                digest.monitored_companies = await self._get_monitored_companies_summary(
                    user_id,
                    period_start,
                    period_end
                )

            # Team activity
            if prefs.include_team_activity:
                digest.team_activity = await self._get_team_activity_summary(
                    user_id,
                    period_start,
                    period_end
                )

            # Knowledge base insights
            if prefs.include_kb_insights:
                digest.kb_insights = await self._get_kb_insights(
                    user_id,
                    period_start,
                    period_end
                )

            # Alerts
            digest.alerts = await self._get_alerts_summary(
                user_id,
                period_start,
                period_end
            )

            logger.info(
                "digest_generated",
                extra={
                    "user_id": user_id,
                    "companies": len(digest.monitored_companies),
                    "team_items": len(digest.team_activity),
                    "alerts": len(digest.alerts)
                }
            )

            return digest

        except Exception as e:
            logger.error(f"generate_digest_failed: user_id={user_id}, error={str(e)}")
            raise

    async def send_digest(self, user_id: str):
        """
        Send digest via email

        Args:
            user_id: User ID
        """
        try:
            # Get user
            user = await self.db.get_user(user_id)
            if not user:
                logger.warning(f"user_not_found: user_id={user_id}")
                return

            # Get preferences
            prefs = await self.db.get_digest_preferences(user_id)
            if not prefs or not prefs.enabled:
                logger.info(f"digest_disabled: user_id={user_id}")
                return

            # Generate digest
            digest = await self.generate_weekly_digest(user_id)

            # Check if there's content to send
            if not self._has_content(digest):
                logger.info(f"digest_empty: user_id={user_id}")
                return

            # Format email
            email_html = self._format_digest_email(digest, user)

            # Send email
            email_service = get_email_service()
            # Create simple text version from HTML
            text_body = f"Weekly Intelligence Digest\n\n"
            text_body += f"Companies analyzed: {len(digest.companies)}\n"
            text_body += f"Alerts: {len(digest.alerts)}\n"
            text_body += f"Insights: {len(digest.kb_insights)}\n"
            email_service.send_email(
                to=user.email,
                subject=self._get_subject_line(digest),
                body=text_body,
                html_body=email_html
            )

            logger.info(f"digest_sent: user_id={user_id}, email={user.email}")

        except Exception as e:
            logger.error(f"send_digest_failed: user_id={user_id}, error={str(e)}")
            raise

    async def send_all_digests(self, frequency: DigestFrequency):
        """
        Send digests to all users with specified frequency

        Args:
            frequency: Digest frequency (daily, weekly, monthly)
        """
        try:
            # Get all users with this frequency enabled
            users = await self.db.list_users_with_digest_frequency(frequency)

            logger.info(f"sending_digests", frequency=frequency.value, count=len(users))

            sent_count = 0
            error_count = 0

            for user in users:
                try:
                    await self.send_digest(user.id)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"digest_send_failed: user_id={user.id}, error={str(e)}")
                    error_count += 1

            logger.info(
                f"digests_batch_complete: frequency={frequency.value}, sent={sent_count}, errors={error_count}"
            )

        except Exception as e:
            logger.error(f"send_all_digests_failed: frequency={frequency.value}, error={str(e)}")
            raise

    # ===== Helper Methods =====

    async def _get_monitored_companies_summary(
        self,
        user_id: str,
        start: datetime,
        end: datetime
    ) -> List[Dict[str, Any]]:
        """Get summary of monitored companies (auto-run saved searches)"""
        companies = []

        # Get auto-run saved searches
        searches = await self.db.list_saved_searches(user_id, auto_run_only=True)

        for search in searches:
            # Get recent runs
            runs = await self.db.get_saved_search_history(
                search.id,
                limit=5,
                from_date=start,
                to_date=end
            )

            if runs:
                companies.append({
                    "company": search.company,
                    "industry": search.industry,
                    "runs_this_period": len(runs),
                    "last_run": search.last_run,
                    "confidence": runs[0].get('confidence', 0) if runs else 0,
                    "key_changes": self._identify_changes_in_runs(runs),
                })

        return companies

    async def _get_team_activity_summary(
        self,
        user_id: str,
        start: datetime,
        end: datetime
    ) -> List[Dict[str, Any]]:
        """Get team activity summary"""
        activity = []

        # Get user's teams
        teams = await self.db.list_user_teams(user_id)

        for team in teams:
            # Get recent analyses
            analyses = await self.db.list_team_analyses(
                team.id,
                limit=10,
                from_date=start,
                to_date=end
            )

            # Get recent comments
            comments = await self.db.list_team_comments(
                team.id,
                from_date=start,
                to_date=end
            )

            if analyses or comments:
                activity.append({
                    "team_name": team.name,
                    "team_id": team.id,
                    "new_analyses": len(analyses),
                    "new_comments": len(comments),
                    "top_companies": self._extract_top_companies(analyses),
                })

        return activity

    async def _get_kb_insights(
        self,
        user_id: str,
        start: datetime,
        end: datetime
    ) -> List[str]:
        """Get new patterns/insights from knowledge base"""
        insights = []

        # Get recent knowledge items
        items = await self.db.list_knowledge_items(
            user_id,
            from_date=start,
            to_date=end
        )

        if not items:
            return insights

        # Identify patterns
        companies = defaultdict(int)
        industries = defaultdict(int)
        frameworks = defaultdict(int)

        for item in items:
            companies[item.company] += 1
            industries[item.industry] += 1
            for framework in item.frameworks_used:
                frameworks[framework] += 1

        # Generate insights
        if companies:
            top_company = max(companies.items(), key=lambda x: x[1])
            if top_company[1] >= 2:
                insights.append(
                    f"You analyzed {top_company[0]} {top_company[1]} times this week"
                )

        if industries:
            top_industry = max(industries.items(), key=lambda x: x[1])
            if top_industry[1] >= 3:
                insights.append(
                    f"Focus on {top_industry[0]} industry ({top_industry[1]} analyses)"
                )

        if frameworks:
            top_framework = max(frameworks.items(), key=lambda x: x[1])
            insights.append(
                f"Most used framework: {top_framework[0].upper()} ({top_framework[1]} times)"
            )

        # Cross-company connections
        if len(companies) >= 3:
            insights.append(
                f"Growing knowledge base: analyzed {len(companies)} different companies"
            )

        return insights

    async def _get_alerts_summary(
        self,
        user_id: str,
        start: datetime,
        end: datetime
    ) -> List[Dict[str, Any]]:
        """Get alerts summary"""
        alerts = await self.db.list_alerts(
            user_id,
            from_date=start,
            to_date=end,
            unread_only=True
        )

        # Sort by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        alerts.sort(key=lambda x: severity_order.get(x.severity, 3))

        return [
            {
                "company": alert.company,
                "type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "created_at": alert.created_at,
            }
            for alert in alerts[:10]  # Top 10 alerts
        ]

    def _has_content(self, digest: DigestContent) -> bool:
        """Check if digest has any content"""
        return bool(
            digest.monitored_companies or
            digest.team_activity or
            digest.kb_insights or
            digest.alerts
        )

    def _get_subject_line(self, digest: DigestContent) -> str:
        """Generate email subject line"""
        alert_count = len(digest.alerts)
        company_count = len(digest.monitored_companies)

        if alert_count > 0:
            return f"📊 ConsultantOS Weekly Digest - {alert_count} alerts"
        elif company_count > 0:
            return f"📊 ConsultantOS Weekly Digest - {company_count} companies updated"
        else:
            return "📊 ConsultantOS Weekly Digest"

    def _format_digest_email(self, digest: DigestContent, user: Any) -> str:
        """Format digest as HTML email"""
        html_parts = [
            f"<html><body>",
            f"<h1>Weekly Digest</h1>",
            f"<p>Hi {user.email},</p>",
            f"<p>Here's your weekly summary from {digest.period_start.strftime('%b %d')} to {digest.period_end.strftime('%b %d, %Y')}:</p>",
        ]

        # Alerts
        if digest.alerts:
            html_parts.append("<h2>🚨 Alerts</h2><ul>")
            for alert in digest.alerts:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(alert['severity'], "⚪")
                html_parts.append(
                    f"<li>{severity_icon} <strong>{alert['company']}</strong>: {alert['message']}</li>"
                )
            html_parts.append("</ul>")

        # Monitored companies
        if digest.monitored_companies:
            html_parts.append("<h2>📈 Monitored Companies</h2><ul>")
            for company in digest.monitored_companies:
                html_parts.append(
                    f"<li><strong>{company['company']}</strong> ({company['industry']}): "
                    f"{company['runs_this_period']} updates, confidence {company['confidence']:.2f}</li>"
                )
            html_parts.append("</ul>")

        # Team activity
        if digest.team_activity:
            html_parts.append("<h2>👥 Team Activity</h2><ul>")
            for team in digest.team_activity:
                html_parts.append(
                    f"<li><strong>{team['team_name']}</strong>: "
                    f"{team['new_analyses']} new analyses, {team['new_comments']} comments</li>"
                )
            html_parts.append("</ul>")

        # KB insights
        if digest.kb_insights:
            html_parts.append("<h2>💡 Knowledge Base Insights</h2><ul>")
            for insight in digest.kb_insights:
                html_parts.append(f"<li>{insight}</li>")
            html_parts.append("</ul>")

        html_parts.append(
            "<p><a href='https://consultantos.app'>View Dashboard</a></p>"
            "<p>-- ConsultantOS Team</p>"
            "</body></html>"
        )

        return "\n".join(html_parts)

    def _identify_changes_in_runs(self, runs: List[Dict[str, Any]]) -> List[str]:
        """Identify key changes between runs"""
        if len(runs) < 2:
            return []

        changes = []
        recent = runs[0]
        previous = runs[1]

        # Confidence change
        if 'confidence' in recent and 'confidence' in previous:
            conf_change = recent['confidence'] - previous['confidence']
            if abs(conf_change) > 0.1:
                direction = "improved" if conf_change > 0 else "decreased"
                changes.append(f"Confidence {direction} by {abs(conf_change):.2f}")

        return changes

    def _extract_top_companies(self, analyses: List[Dict[str, Any]]) -> List[str]:
        """Extract top companies from analyses"""
        company_counts = defaultdict(int)
        for analysis in analyses:
            company_counts[analysis.get('company', 'Unknown')] += 1

        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)
        return [company for company, _ in top_companies[:3]]
