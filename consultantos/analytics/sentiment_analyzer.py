"""
Sentiment analysis using BERT-based models
"""
import logging
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import statistics
import importlib

from consultantos.config import settings

logger = logging.getLogger(__name__)

# NOTE: Importing transformers/torch eagerly makes application startup hang on systems
# without optimized wheels. We defer those imports until sentiment analysis is actually
# requested so the rest of the API can continue to load quickly.
pipeline = None
AutoTokenizer = None
AutoModelForSequenceClassification = None
torch = None
TRANSFORMERS_AVAILABLE = False
_transformers_checked = False
_transformers_lock = threading.Lock()


def _ensure_transformers_loaded() -> bool:
    """Lazy-load heavy transformers/torch dependencies exactly once."""
    global pipeline, AutoTokenizer, AutoModelForSequenceClassification
    global torch, TRANSFORMERS_AVAILABLE, _transformers_checked

    if not getattr(settings, "enable_advanced_sentiment", False):
        logger.info("Advanced sentiment disabled in settings; skipping transformers import")
        _transformers_checked = True
        return False

    if TRANSFORMERS_AVAILABLE:
        return True
    
    with _transformers_lock:
        # Re-check inside lock
        if TRANSFORMERS_AVAILABLE:
            return True
        if _transformers_checked:
            return False

        _transformers_checked = True
        try:
            transformers_module = importlib.import_module("transformers")
            torch_module = importlib.import_module("torch")
            pipeline = transformers_module.pipeline
            AutoTokenizer = transformers_module.AutoTokenizer
            AutoModelForSequenceClassification = transformers_module.AutoModelForSequenceClassification
            torch = torch_module
            TRANSFORMERS_AVAILABLE = True
            logger.info("transformers library loaded lazily for sentiment analysis")
            return True
        except ImportError:
            logger.warning(
                "transformers not installed - sentiment analysis will use rule-based fallback"
            )
            TRANSFORMERS_AVAILABLE = False
            return False


try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logger.warning("textblob not installed - using basic sentiment fallback")


class SentimentAnalyzer:
    """
    Sentiment analyzer using BERT-based models with fallback to simpler methods
    """

    def __init__(
        self,
        model_name: str = "distilbert-base-uncased-finetuned-sst-2-english",
        use_gpu: bool = False
    ):
        """
        Initialize sentiment analyzer

        Args:
            model_name: HuggingFace model name for sentiment analysis
            use_gpu: Whether to use GPU for inference (requires CUDA)
        """
        self.model_name = model_name
        self.pipeline = None
        self.use_gpu = False
        self._prefer_gpu = bool(use_gpu)
        self._pipeline_failed = False
        self._pipeline_lock = threading.Lock()

        # NOTE: We intentionally avoid loading transformers/torch here because creating
        # the huggingface pipeline pulls in TensorFlow on macOS, which can hang startup
        # (see issue documented in tests/e2e/MUTEX_DEADLOCK_FIX.md). The heavy imports
        # now happen only when a sentiment call is actually executed.

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single text

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment_score (-1 to 1), label, and confidence
        """
        if not text or not text.strip():
            return {
                "sentiment_score": 0.0,
                "label": "neutral",
                "confidence": 0.0
            }

        # Try BERT-based analysis
        if self.pipeline is None and not self._pipeline_failed:
            self._ensure_pipeline_ready()

        if self.pipeline:
            try:
                result = await asyncio.to_thread(
                    self._analyze_with_bert,
                    text
                )
                return result
            except Exception as e:
                logger.warning(f"BERT analysis failed: {e}, using fallback")

        # Fallback to TextBlob
        if TEXTBLOB_AVAILABLE:
            return self._analyze_with_textblob(text)

        # Basic keyword-based fallback
        return self._analyze_with_keywords(text)

    def _analyze_with_bert(self, text: str) -> Dict[str, Any]:
        """Analyze with BERT model"""
        # Truncate text if too long
        if len(text) > 512:
            text = text[:512]

        result = self.pipeline(text)[0]

        # Convert to -1 to 1 scale
        if result['label'].upper() == 'POSITIVE':
            score = result['score']
        elif result['label'].upper() == 'NEGATIVE':
            score = -result['score']
        else:
            score = 0.0

        return {
            "sentiment_score": round(score, 3),
            "label": self._score_to_label(score),
            "confidence": round(result['score'], 3)
        }

    def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze with TextBlob (simpler but fast)"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1

        return {
            "sentiment_score": round(polarity, 3),
            "label": self._score_to_label(polarity),
            "confidence": round(abs(polarity), 3)
        }

    def _analyze_with_keywords(self, text: str) -> Dict[str, Any]:
        """Basic keyword-based sentiment analysis"""
        text_lower = text.lower()

        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'best',
            'fantastic', 'wonderful', 'perfect', 'outstanding', 'superb'
        ]
        negative_words = [
            'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'poor',
            'disappointing', 'useless', 'failure', 'pathetic', 'disgusting'
        ]

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        total = pos_count + neg_count
        if total == 0:
            score = 0.0
        else:
            score = (pos_count - neg_count) / total

        return {
            "sentiment_score": round(score, 3),
            "label": self._score_to_label(score),
            "confidence": round(min(total / 5, 1.0), 3)  # Rough confidence estimate
        }

    def _ensure_pipeline_ready(self) -> None:
        """Load the transformers pipeline on first use without blocking import time."""
        if self.pipeline is not None or self._pipeline_failed:
            return

        with self._pipeline_lock:
            if self.pipeline is not None or self._pipeline_failed:
                return

            if not _ensure_transformers_loaded():
                self._pipeline_failed = True
                return

            self.use_gpu = bool(self._prefer_gpu and torch and torch.cuda.is_available())
            try:
                device = 0 if self.use_gpu else -1
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    device=device,
                    truncation=True,
                    max_length=512
                )
                logger.info(
                    "Loaded sentiment model %s (GPU=%s) after deferred import",
                    self.model_name,
                    self.use_gpu,
                )
            except Exception as e:
                logger.warning(f"Failed to load BERT model, using fallback: {e}")
                self.pipeline = None
                self._pipeline_failed = True

    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.2:
            return "positive"
        elif score < -0.2:
            return "negative"
        else:
            return "neutral"

    async def analyze_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for a batch of texts

        Args:
            texts: List of texts to analyze
            batch_size: Number of texts to process at once

        Returns:
            List of sentiment analysis results
        """
        if not texts:
            return []

        results = []

        # Process in batches for efficiency
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Analyze each text in batch
            batch_results = await asyncio.gather(*[
                self.analyze_text(text) for text in batch
            ])

            results.extend(batch_results)

        return results

    async def analyze_tweets(
        self,
        tweets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for a list of tweets

        Args:
            tweets: List of tweet dictionaries with 'content' field

        Returns:
            List of tweets with added sentiment data
        """
        if not tweets:
            return []

        # Extract tweet contents
        contents = [tweet.get('content', '') for tweet in tweets]

        # Analyze sentiments
        sentiments = await self.analyze_batch(contents)

        # Merge sentiment data into tweets
        enriched_tweets = []
        for tweet, sentiment in zip(tweets, sentiments):
            enriched_tweet = tweet.copy()
            enriched_tweet['sentiment'] = sentiment
            enriched_tweet['sentiment_score'] = sentiment['sentiment_score']
            enriched_tweets.append(enriched_tweet)

        return enriched_tweets

    def aggregate_sentiment(
        self,
        sentiments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate sentiment scores over multiple texts

        Args:
            sentiments: List of sentiment analysis results

        Returns:
            Aggregated sentiment statistics
        """
        if not sentiments:
            return {
                "mean_score": 0.0,
                "median_score": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "total_count": 0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "neutral_percentage": 0.0,
                "overall_label": "neutral"
            }

        scores = [s['sentiment_score'] for s in sentiments]
        labels = [s['label'] for s in sentiments]

        positive_count = labels.count('positive')
        negative_count = labels.count('negative')
        neutral_count = labels.count('neutral')
        total = len(sentiments)

        mean_score = statistics.mean(scores)
        median_score = statistics.median(scores)

        return {
            "mean_score": round(mean_score, 3),
            "median_score": round(median_score, 3),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "total_count": total,
            "positive_percentage": round(positive_count / total * 100, 1),
            "negative_percentage": round(negative_count / total * 100, 1),
            "neutral_percentage": round(neutral_count / total * 100, 1),
            "overall_label": self._score_to_label(mean_score)
        }

    def detect_sentiment_shift(
        self,
        current_sentiment: Dict[str, Any],
        previous_sentiment: Dict[str, Any],
        threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Detect significant sentiment shifts (for crisis detection)

        Args:
            current_sentiment: Current aggregated sentiment
            previous_sentiment: Previous aggregated sentiment
            threshold: Minimum score change to consider significant

        Returns:
            Dict with shift detection results
        """
        current_score = current_sentiment.get('mean_score', 0.0)
        previous_score = previous_sentiment.get('mean_score', 0.0)

        shift = current_score - previous_score
        is_significant = abs(shift) >= threshold

        # Detect crisis (sudden negative shift)
        is_crisis = is_significant and shift < -threshold

        return {
            "shift_detected": is_significant,
            "is_crisis": is_crisis,
            "shift_magnitude": round(shift, 3),
            "current_score": current_score,
            "previous_score": previous_score,
            "shift_percentage": round((shift / max(abs(previous_score), 0.1)) * 100, 1),
            "direction": "positive" if shift > 0 else "negative" if shift < 0 else "stable"
        }

    async def get_sentiment_over_time(
        self,
        tweets_by_period: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze sentiment trends over time periods

        Args:
            tweets_by_period: Dict mapping time period to list of tweets

        Returns:
            Dict mapping time period to aggregated sentiment
        """
        sentiment_timeline = {}

        for period, tweets in tweets_by_period.items():
            # Analyze tweets for this period
            enriched_tweets = await self.analyze_tweets(tweets)

            # Aggregate sentiment
            sentiments = [t['sentiment'] for t in enriched_tweets]
            aggregated = self.aggregate_sentiment(sentiments)

            sentiment_timeline[period] = aggregated

        return sentiment_timeline
