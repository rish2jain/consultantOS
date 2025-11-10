"""
NLP Tool - Entity extraction, sentiment analysis, and relationship extraction
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
from textblob import TextBlob
import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)


class NLPProcessor:
    """
    NLP processor for extracting structured information from text.

    Provides:
    - Entity extraction (companies, people, locations, dates, etc.)
    - Sentiment analysis (polarity, subjectivity, classification)
    - Keyword extraction (key terms and phrases)
    - Relationship extraction (entity co-occurrences)
    """

    def __init__(self, model_name: str = "en_core_web_sm", cache_enabled: bool = True):
        """
        Initialize NLP processor with spaCy model.

        Args:
            model_name: spaCy model to load (default: en_core_web_sm)
            cache_enabled: Enable caching of NLP results

        Note:
            If model is not installed, download with:
            python -m spacy download en_core_web_sm
        """
        self.model_name = model_name
        self.cache_enabled = cache_enabled
        self._nlp: Optional[Language] = None

    @property
    def nlp(self) -> Language:
        """Lazy load spaCy model on first use"""
        if self._nlp is None:
            try:
                self._nlp = spacy.load(self.model_name)
                logger.info(f"Loaded spaCy model: {self.model_name}")
            except OSError:
                logger.error(
                    f"spaCy model '{self.model_name}' not found. "
                    f"Download it with: python -m spacy download {self.model_name}"
                )
                raise
        return self._nlp

    def entity_extraction(self, text: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Extract named entities from text.

        Args:
            text: Input text to analyze
            entity_types: Filter to specific entity types (ORG, PERSON, GPE, DATE, etc.)
                         If None, returns all entities

        Returns:
            List of entity dictionaries with:
                - text: Entity text
                - label: Entity type (ORG, PERSON, GPE, DATE, etc.)
                - start: Start character index
                - end: End character index
                - confidence: Entity confidence (if available)

        Example:
            >>> nlp = NLPProcessor()
            >>> entities = nlp.entity_extraction("Apple Inc. CEO Tim Cook announced...")
            >>> [{'text': 'Apple Inc.', 'label': 'ORG', 'start': 0, 'end': 10}, ...]
        """
        if not text or not text.strip():
            return []

        # Detect language - skip non-English text
        if not self._is_english(text):
            logger.warning("Non-English text detected, skipping NLP processing")
            return []

        doc = self.nlp(text)

        entities = []
        for ent in doc.ents:
            # Filter by entity type if specified
            if entity_types and ent.label_ not in entity_types:
                continue

            entity = {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            entities.append(entity)

        return entities

    def sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using TextBlob.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with:
                - polarity: Sentiment polarity (-1.0 to 1.0)
                - subjectivity: Subjectivity score (0.0 to 1.0)
                - classification: Sentiment classification (positive/negative/neutral)

        Example:
            >>> nlp = NLPProcessor()
            >>> sentiment = nlp.sentiment_analysis("This is an excellent product!")
            >>> {'polarity': 0.8, 'subjectivity': 0.9, 'classification': 'positive'}
        """
        if not text or not text.strip():
            return {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "classification": "neutral"
            }

        # Use TextBlob for sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Classify sentiment based on polarity
        if polarity > 0.1:
            classification = "positive"
        elif polarity < -0.1:
            classification = "negative"
        else:
            classification = "neutral"

        return {
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3),
            "classification": classification
        }

    def relationship_extraction(self, text: str, min_distance: int = 0, max_distance: int = 50) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities based on proximity.

        Identifies entity co-occurrences within a specified distance,
        which can indicate potential relationships (partnerships, acquisitions, etc.)

        Args:
            text: Input text to analyze
            min_distance: Minimum character distance between entities
            max_distance: Maximum character distance between entities

        Returns:
            List of relationship dictionaries with:
                - entity1: First entity
                - entity2: Second entity
                - distance: Character distance between entities
                - context: Surrounding text context

        Example:
            >>> nlp = NLPProcessor()
            >>> rels = nlp.relationship_extraction("Tesla partnered with Samsung on batteries")
            >>> [{'entity1': {'text': 'Tesla', 'label': 'ORG'},
            ...   'entity2': {'text': 'Samsung', 'label': 'ORG'},
            ...   'distance': 15, 'context': 'partnered with'}]
        """
        if not text or not text.strip():
            return []

        doc = self.nlp(text)
        entities = list(doc.ents)

        relationships = []

        # Find entity pairs within distance threshold
        for i, ent1 in enumerate(entities):
            for ent2 in entities[i+1:]:
                # Calculate character distance
                distance = abs(ent1.start_char - ent2.start_char)

                if min_distance <= distance <= max_distance:
                    # Extract context between entities
                    start = min(ent1.end_char, ent2.end_char)
                    end = max(ent1.start_char, ent2.start_char)
                    context = text[start:end].strip()

                    relationships.append({
                        "entity1": {
                            "text": ent1.text,
                            "label": ent1.label_
                        },
                        "entity2": {
                            "text": ent2.text,
                            "label": ent2.label_
                        },
                        "distance": distance,
                        "context": context
                    })

        return relationships

    def keyword_extraction(self, text: str, top_n: int = 10, pos_tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Extract key terms and phrases from text.

        Uses part-of-speech tagging and frequency analysis to identify
        important terms (nouns, noun phrases, etc.)

        Args:
            text: Input text to analyze
            top_n: Number of top keywords to return
            pos_tags: POS tags to filter (NOUN, PROPN, VERB, ADJ, etc.)
                     Default: ['NOUN', 'PROPN'] (nouns and proper nouns)

        Returns:
            List of keyword dictionaries with:
                - text: Keyword text
                - pos: Part-of-speech tag
                - frequency: Occurrence count

        Example:
            >>> nlp = NLPProcessor()
            >>> keywords = nlp.keyword_extraction("Tesla develops electric vehicles...")
            >>> [{'text': 'Tesla', 'pos': 'PROPN', 'frequency': 3}, ...]
        """
        if not text or not text.strip():
            return []

        if pos_tags is None:
            pos_tags = ['NOUN', 'PROPN']  # Default to nouns and proper nouns

        doc = self.nlp(text)

        # Count token frequencies by POS tag
        token_freq: Dict[str, int] = {}
        token_pos: Dict[str, str] = {}

        for token in doc:
            # Filter by POS tag
            if token.pos_ not in pos_tags:
                continue

            # Skip stopwords and punctuation
            if token.is_stop or token.is_punct:
                continue

            # Normalize to lowercase
            text_lower = token.text.lower()

            # Count frequency
            token_freq[text_lower] = token_freq.get(text_lower, 0) + 1
            token_pos[text_lower] = token.pos_

        # Sort by frequency and return top N
        sorted_keywords = sorted(token_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]

        keywords = [
            {
                "text": text,
                "pos": token_pos[text],
                "frequency": freq
            }
            for text, freq in sorted_keywords
        ]

        return keywords

    def process_article(self, title: str, content: str, extract_relationships: bool = True) -> Dict[str, Any]:
        """
        Process an article with full NLP pipeline.

        Convenience method that runs all NLP analyses on an article.

        Args:
            title: Article title
            content: Article content/text
            extract_relationships: Whether to extract entity relationships (slower)

        Returns:
            Dictionary with all NLP results:
                - entities: List of extracted entities
                - sentiment: Sentiment analysis results
                - keywords: Key terms and phrases
                - relationships: Entity relationships (if enabled)

        Example:
            >>> nlp = NLPProcessor()
            >>> results = nlp.process_article("Tesla News", "Tesla announced...")
            >>> results['entities']  # List of entities
            >>> results['sentiment']  # Sentiment scores
        """
        # Combine title and content for analysis
        full_text = f"{title}\n\n{content}"

        results = {
            "entities": self.entity_extraction(full_text),
            "sentiment": self.sentiment_analysis(full_text),
            "keywords": self.keyword_extraction(full_text),
        }

        if extract_relationships:
            results["relationships"] = self.relationship_extraction(full_text)

        return results

    def _is_english(self, text: str) -> bool:
        """
        Detect if text is primarily English.

        Simple heuristic: check if majority of characters are ASCII.
        More sophisticated language detection could use langdetect library.

        Args:
            text: Text to check

        Returns:
            True if text appears to be English, False otherwise
        """
        if not text:
            return False

        # Count ASCII vs non-ASCII characters
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        total_chars = len(text)

        # Consider English if >80% ASCII
        return (ascii_chars / total_chars) > 0.8


@lru_cache(maxsize=1)
def get_nlp_processor(model_name: str = "en_core_web_sm") -> NLPProcessor:
    """
    Get singleton NLP processor instance (cached).

    This ensures we only load the spaCy model once per process,
    improving performance.

    Args:
        model_name: spaCy model to load

    Returns:
        Cached NLPProcessor instance
    """
    return NLPProcessor(model_name=model_name)


# Convenience function for quick NLP processing
def analyze_text(text: str, include_relationships: bool = False) -> Dict[str, Any]:
    """
    Quick NLP analysis of text with default settings.

    Args:
        text: Text to analyze
        include_relationships: Whether to extract entity relationships

    Returns:
        Dictionary with NLP results (entities, sentiment, keywords, relationships)
    """
    processor = get_nlp_processor()

    results = {
        "entities": processor.entity_extraction(text),
        "sentiment": processor.sentiment_analysis(text),
        "keywords": processor.keyword_extraction(text),
    }

    if include_relationships:
        results["relationships"] = processor.relationship_extraction(text)

    return results
