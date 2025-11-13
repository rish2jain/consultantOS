"""Utilities to convert raw social media telemetry into strategic signals."""

from __future__ import annotations

from statistics import mean
from typing import Dict, List, Optional

from consultantos.models.social_media import (
    CrisisAlert,
    Influencer,
    InfluencerSignal,
    NarrativeSignal,
    RedditInsight,
    RedditPost,
    SocialMediaInsight,
    SocialSignalSummary,
    TrendingTopic,
)


class SocialSignalSynthesizer:
    """Aggregate Reddit + Twitter telemetry into concise strategic signals."""

    def __init__(self, share_floor: float = 5.0) -> None:
        self.share_floor = share_floor

    def summarize(
        self,
        company: str,
        twitter_insight: Optional[SocialMediaInsight],
        reddit_insight: Optional[RedditInsight],
    ) -> Optional[SocialSignalSummary]:
        """Build a SocialSignalSummary from platform-specific insights."""

        if not twitter_insight and not reddit_insight:
            return None

        sentiment_samples: List[float] = []
        twitter_volume = 0
        reddit_volume = 0

        if twitter_insight:
            # Safely append sentiment score
            if hasattr(twitter_insight, 'overall_sentiment') and twitter_insight.overall_sentiment is not None:
                sentiment_samples.append(twitter_insight.overall_sentiment)
            
            # Safely access metrics with defensive checks
            metrics = getattr(twitter_insight, 'metrics', None)
            if metrics is not None and isinstance(metrics, dict):
                total_tweets = metrics.get("total_tweets", 0)
                try:
                    twitter_volume = int(total_tweets) if total_tweets is not None else 0
                except (ValueError, TypeError):
                    twitter_volume = 0
            else:
                twitter_volume = 0

        if reddit_insight:
            # Safely append sentiment score
            if hasattr(reddit_insight, 'overall_sentiment') and reddit_insight.overall_sentiment is not None:
                sentiment_samples.append(reddit_insight.overall_sentiment)
            
            # Safely get total_posts and total_comments with numeric fallbacks
            total_posts = getattr(reddit_insight, 'total_posts', None)
            total_comments = getattr(reddit_insight, 'total_comments', None)
            
            try:
                posts_val = int(total_posts) if total_posts is not None and isinstance(total_posts, (int, float, str)) else 0
            except (ValueError, TypeError):
                posts_val = 0
            
            try:
                comments_val = int(total_comments) if total_comments is not None and isinstance(total_comments, (int, float, str)) else 0
            except (ValueError, TypeError):
                comments_val = 0
            
            reddit_volume = posts_val + comments_val

        # Filter out None values and ensure all are numeric before calculating mean
        valid_samples = [s for s in sentiment_samples if s is not None and isinstance(s, (int, float))]
        if valid_samples:
            blended_sentiment = mean(valid_samples)
        else:
            blended_sentiment = 0.0
        sentiment_label = self._label_from_score(blended_sentiment)

        narratives = self._build_narratives(
            twitter_insight=twitter_insight,
            reddit_insight=reddit_insight,
            twitter_volume=twitter_volume,
            reddit_volume=reddit_volume,
        )

        influencer_watchlist = self._build_influencer_watchlist(
            twitter_insight=twitter_insight,
            reddit_insight=reddit_insight,
        )

        risk_alerts = self._build_risk_alerts(twitter_insight, reddit_insight)
        opportunity_alerts = [
            narrative.strategic_implication
            for narrative in narratives
            if narrative.sentiment_score >= 0.2
        ]
        supporting_posts = self._collect_supporting_posts(reddit_insight)

        summary = SocialSignalSummary(
            sentiment_score=round(blended_sentiment, 3),
            sentiment_label=sentiment_label,
            momentum=self._derive_momentum(blended_sentiment, risk_alerts, opportunity_alerts),
            reddit_volume=reddit_volume,
            twitter_volume=twitter_volume,
            narratives=narratives,
            influencer_watchlist=influencer_watchlist,
            risk_alerts=risk_alerts,
            opportunity_alerts=opportunity_alerts,
            supporting_posts=supporting_posts,
        )

        return summary

    # ------------------------------------------------------------------
    # Narrative synthesis helpers
    # ------------------------------------------------------------------

    def _build_narratives(
        self,
        twitter_insight: Optional[SocialMediaInsight],
        reddit_insight: Optional[RedditInsight],
        twitter_volume: int,
        reddit_volume: int,
    ) -> List[NarrativeSignal]:
        topic_map: Dict[str, NarrativeSignal] = {}

        if twitter_insight and twitter_insight.trending_topics:
            total_mentions = sum(t.mention_count for t in twitter_insight.trending_topics) or 1
            for topic in twitter_insight.trending_topics[:5]:
                share = max(self.share_floor, (topic.mention_count / total_mentions) * 100)
                self._merge_topic(
                    topic_map,
                    topic=topic.topic,
                    sentiment=topic.sentiment_score,
                    share_of_voice=share,
                    platform="twitter",
                    implication=self._infer_implication(topic.topic, topic.sentiment_score),
                )

        if reddit_insight and reddit_insight.trending_topics:
            share = max(self.share_floor, 100 / max(len(reddit_insight.trending_topics), 1))
            for topic in reddit_insight.trending_topics[:5]:
                self._merge_topic(
                    topic_map,
                    topic=topic,
                    sentiment=reddit_insight.overall_sentiment,
                    share_of_voice=share,
                    platform="reddit",
                    implication=self._infer_implication(topic, reddit_insight.overall_sentiment),
                    supporting_posts=self._find_supporting_posts(topic, reddit_insight.top_discussions),
                )

        return sorted(topic_map.values(), key=lambda n: n.share_of_voice, reverse=True)[:5]

    def _merge_topic(
        self,
        topic_map: Dict[str, NarrativeSignal],
        *,
        topic: str,
        sentiment: float,
        share_of_voice: float,
        platform: str,
        implication: str,
        supporting_posts: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        key = topic.lower().strip()
        if key in topic_map:
            existing = topic_map[key]
            existing.share_of_voice = round(min(100.0, existing.share_of_voice + share_of_voice), 2)
            existing.sentiment_score = round((existing.sentiment_score + sentiment) / 2, 3)
            if platform not in existing.platforms:
                existing.platforms.append(platform)
            if supporting_posts:
                existing.supporting_evidence.extend(supporting_posts)
            existing.strategic_implication = implication or existing.strategic_implication
            return

        narrative = NarrativeSignal(
            topic=topic,
            stance="supportive" if sentiment >= 0.2 else "opposed" if sentiment <= -0.2 else "neutral",
            sentiment_score=round(sentiment, 3),
            share_of_voice=round(min(100.0, share_of_voice), 2),
            momentum="accelerating" if abs(sentiment) >= 0.2 else "stable",
            platforms=[platform],
            supporting_evidence=supporting_posts or [],
            strategic_implication=implication,
            confidence=min(1.0, share_of_voice / 100),
        )
        topic_map[key] = narrative

    def _infer_implication(self, topic: str, sentiment: float) -> str:
        if sentiment >= 0.2:
            return f"Double down on {topic} narrative; community momentum is positive."
        if sentiment <= -0.2:
            return f"Mitigate backlash around {topic} before it shapes perception."
        return f"Monitor {topic} closely; sentiment is mixed and could swing rapidly."

    def _find_supporting_posts(
        self, topic: str, posts: Optional[List[RedditPost]]
    ) -> List[Dict[str, str]]:
        if not posts:
            return []
        matches: List[Dict[str, str]] = []
        topic_lower = topic.lower()
        for post in posts:
            if topic_lower in post.title.lower() or topic_lower in (post.content or "").lower():
                matches.append(
                    {
                        "platform": "reddit",
                        "title": post.title[:120],
                        "url": post.url,
                        "sentiment": f"{post.sentiment_score:.2f}",
                    }
                )
            if len(matches) >= 2:
                break
        return matches

    # ------------------------------------------------------------------
    # Influencer & alert derivation
    # ------------------------------------------------------------------

    def _build_influencer_watchlist(
        self,
        twitter_insight: Optional[SocialMediaInsight],
        reddit_insight: Optional[RedditInsight],
    ) -> List[InfluencerSignal]:
        watchlist: List[InfluencerSignal] = []

        if twitter_insight and twitter_insight.top_influencers:
            for influencer in twitter_insight.top_influencers[:5]:
                watchlist.append(
                    InfluencerSignal(
                        handle=f"@{influencer.username}",
                        platform="twitter",
                        reach=influencer.followers_count,
                        influence_score=influencer.influence_score,
                        stance=self._derive_influencer_stance(twitter_insight.overall_sentiment),
                        message=self._summarize_influencer_topics(influencer),
                        link=None,
                    )
                )

        if reddit_insight and reddit_insight.key_influencers:
            approx_reach = max(1, reddit_insight.total_posts)
            for redditor in reddit_insight.key_influencers[:3]:
                watchlist.append(
                    InfluencerSignal(
                        handle=f"u/{redditor}",
                        platform="reddit",
                        reach=approx_reach,
                        influence_score=approx_reach / 10,
                        stance=self._derive_influencer_stance(reddit_insight.overall_sentiment),
                        message="Driving high-engagement Reddit threads",
                        link=None,
                    )
                )

        return watchlist

    def _derive_influencer_stance(self, sentiment: float) -> str:
        if sentiment >= 0.2:
            return "supportive"
        if sentiment <= -0.2:
            return "critical"
        return "mixed"

    def _summarize_influencer_topics(self, influencer: Influencer) -> str:
        if influencer.topics:
            topics = ", ".join(influencer.topics[:2])
            return f"Shaping conversation on {topics}"
        return "Driving conversation on core roadmap themes"

    def _build_risk_alerts(
        self,
        twitter_insight: Optional[SocialMediaInsight],
        reddit_insight: Optional[RedditInsight],
    ) -> List[str]:
        alerts: List[str] = []

        if twitter_insight:
            crisis_alerts = [
                alert for alert in twitter_insight.crisis_alerts if isinstance(alert, CrisisAlert)
            ]
            for alert in crisis_alerts:
                if alert.requires_action:
                    topics = ", ".join(alert.affected_topics) if alert.affected_topics else "community"
                    alerts.append(f"{alert.description} across {topics}")

        if reddit_insight and reddit_insight.overall_sentiment <= -0.2:
            alerts.append(
                f"Reddit sentiment turned negative ({reddit_insight.overall_sentiment:.2f}); watchdog subreddits escalating narrative."
            )

        return alerts

    # ------------------------------------------------------------------
    # Momentum helpers & supporting posts
    # ------------------------------------------------------------------

    def _collect_supporting_posts(
        self, reddit_insight: Optional[RedditInsight]
    ) -> List[Dict[str, str]]:
        if not reddit_insight or not reddit_insight.top_discussions:
            return []
        posts = []
        for post in reddit_insight.top_discussions[:5]:
            posts.append(
                {
                    "platform": "reddit",
                    "title": post.title[:140],
                    "url": post.url,
                    "subreddit": post.subreddit,
                    "sentiment": f"{post.sentiment_score:.2f}",
                }
            )
        return posts

    def _derive_momentum(
        self, blended_sentiment: float, risk_alerts: List[str], opportunity_alerts: List[str]
    ) -> str:
        if blended_sentiment >= 0.2 and opportunity_alerts:
            return "Tailwind"
        if blended_sentiment <= -0.2 or risk_alerts:
            return "Headwind"
        return "Mixed"

    def _label_from_score(self, score: float) -> str:
        if score >= 0.2:
            return "positive"
        if score <= -0.2:
            return "negative"
        return "neutral"

