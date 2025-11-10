"""
Grok API Connector via laozhang.ai for social media sentiment analysis
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai not installed - Grok connector will be unavailable")


class GrokConnector:
    """Grok API connector via laozhang.ai for sentiment analysis on X/Twitter"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.laozhang.ai/v1",
        model: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize Grok connector

        Args:
            api_key: Laozhang.ai API key
            base_url: API base URL (default: laozhang.ai)
            model: Grok model name (default: grok-4-all)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        # Default to grok-4-fast-reasoning-latest if not specified (fastest with reasoning)
        # Can override to: grok-4-fast-non-reasoning-latest (fastest, 1.80s), grok-4-fast (4.18s), grok-4-all (comprehensive, 112s)
        self.model = model or "grok-4-fast-reasoning-latest"
        self.timeout = timeout

        self.client = None

        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(
                    base_url=base_url,
                    api_key=api_key,
                    timeout=timeout
                )
                logger.info(f"Grok API client initialized with model: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Grok client: {e}")
        else:
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI package not available - Grok connector disabled")
            if not api_key:
                logger.warning("Grok API key not provided - Grok connector disabled")

    async def analyze_sentiment(
        self,
        company: str,
        keywords: List[str],
        days_back: int = 7,
        competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment for a company using Grok's real-time X data access

        Args:
            company: Company name to analyze
            keywords: List of keywords to track
            days_back: Days of history to analyze
            competitors: Optional list of competitor names

        Returns:
            Dictionary with sentiment analysis results
        """
        if not self.client:
            raise ValueError("Grok client not initialized. Check API key and dependencies.")

        # Build comprehensive prompt
        competitor_text = ""
        if competitors:
            competitor_text = f"\n- Competitors to track: {', '.join(competitors)}"

        prompt = f"""
        Analyze sentiment on X (Twitter) for "{company}" over the last {days_back} days.
        Keywords to track: {', '.join(keywords)}
        {competitor_text}

        Provide a comprehensive JSON response with:
        {{
            "overall_sentiment": float between -1 and 1,
            "sentiment_label": "positive" or "negative" or "neutral",
            "sentiment_breakdown": {{
                "positive_percentage": float,
                "neutral_percentage": float,
                "negative_percentage": float
            }},
            "key_themes": ["theme1", "theme2", "theme3"],
            "trending_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
            "key_influencers": ["@account1", "@account2", "@account3", "@account4", "@account5"],
            "crisis_alerts": "description of any negative sentiment spikes or concerns",
            "competitor_mentions": "description of competitor mentions if relevant",
            "summary": "brief summary of overall sentiment and key findings"
        }}
        """

        try:
            # Run in thread pool to avoid blocking
            response = await asyncio.to_thread(
                self._make_request,
                prompt
            )

            # Parse response
            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        content = content[json_start:json_end].strip()
                        data = json.loads(content)
                elif "```" in content:
                    # Try regular code block
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        content = content[json_start:json_end].strip()
                        data = json.loads(content)
                else:
                    # Fallback: return raw content with basic structure
                    logger.warning("Could not parse Grok response as JSON, using fallback")
                    data = {
                        "overall_sentiment": 0.0,
                        "sentiment_label": "neutral",
                        "summary": content,
                        "raw_response": content
                    }

            # Normalize the response to match expected format
            result = {
                "overall_sentiment": float(data.get("overall_sentiment", 0.0)),
                "sentiment_label": data.get("sentiment_label", "neutral").lower(),
                "sentiment_breakdown": data.get("sentiment_breakdown", {
                    "positive_percentage": 0.0,
                    "neutral_percentage": 0.0,
                    "negative_percentage": 0.0
                }),
                "trending_topics": data.get("trending_topics", []),
                "key_influencers": data.get("key_influencers", []),
                "key_themes": data.get("key_themes", []),
                "crisis_alerts": data.get("crisis_alerts", ""),
                "competitor_mentions": data.get("competitor_mentions", ""),
                "summary": data.get("summary", ""),
                "raw_data": data
            }

            logger.info(f"Grok sentiment analysis completed for {company}")
            return result

        except Exception as e:
            logger.error(f"Grok sentiment analysis failed: {e}", exc_info=True)
            raise

    def _make_request(self, prompt: str):
        """Make synchronous API request (called from async context)"""
        try:
            # Try with JSON format first
            try:
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=2000
                )
            except:
                # Fallback: request JSON in prompt
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt + "\n\nPlease format your response as valid JSON."}],
                    max_tokens=2000
                )
        except Exception as e:
            logger.error(f"Grok API request failed: {e}")
            raise

    async def get_influencers(
        self,
        topic: str,
        min_followers: int = 10000,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find top influencers discussing a topic using Grok

        Args:
            topic: Topic to search for
            min_followers: Minimum follower count (informational, Grok may not filter)
            max_results: Maximum number of influencers to return

        Returns:
            List of influencer data dictionaries
        """
        if not self.client:
            raise ValueError("Grok client not initialized")

        prompt = f"""
        Identify top influencers on X (Twitter) discussing "{topic}".
        Provide a JSON array of influencers with:
        {{
            "influencers": [
                {{
                    "username": "@username",
                    "name": "Display Name",
                    "description": "brief description",
                    "topics": ["topic1", "topic2"]
                }}
            ]
        }}
        Return up to {max_results} influencers.
        """

        try:
            response = await asyncio.to_thread(
                self._make_request,
                prompt
            )

            content = response.choices[0].message.content

            # Parse JSON
            try:
                data = json.loads(content)
                influencers = data.get("influencers", [])
            except json.JSONDecodeError:
                # Fallback
                logger.warning("Could not parse influencer response as JSON")
                influencers = []

            logger.info(f"Found {len(influencers)} influencers for topic: {topic}")
            return influencers[:max_results]

        except Exception as e:
            logger.error(f"Failed to get influencers: {e}")
            return []

