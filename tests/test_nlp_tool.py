"""
Tests for NLP Tool - Entity extraction, sentiment analysis, and keyword extraction
"""
import pytest
from consultantos.tools.nlp_tool import NLPProcessor, get_nlp_processor, analyze_text


# Sample texts for testing
SAMPLE_ARTICLE_TITLE = "Tesla Partners with Samsung on Battery Technology"
SAMPLE_ARTICLE_CONTENT = """
Tesla Inc. announced a groundbreaking partnership with Samsung Electronics today.
The collaboration will focus on developing next-generation battery technology for electric vehicles.
CEO Elon Musk stated that this partnership represents a significant milestone for sustainable transportation.
The agreement, signed in Seoul, South Korea, is expected to accelerate innovation in the EV industry.
Industry analysts view this partnership positively, with stock prices rising 5% following the announcement.
"""

POSITIVE_TEXT = "This is an excellent product with amazing features and outstanding performance!"
NEGATIVE_TEXT = "This terrible product failed completely and caused major problems."
NEUTRAL_TEXT = "The product has specifications listed in the manual."

MULTI_ENTITY_TEXT = """
Apple CEO Tim Cook met with Microsoft CEO Satya Nadella in San Francisco on January 15, 2024.
They discussed potential collaboration on AI technology worth $10 billion.
Google and Amazon were also mentioned as potential partners in the deal.
"""


class TestNLPProcessor:
    """Test suite for NLPProcessor class"""

    @pytest.fixture
    def nlp_processor(self):
        """Fixture to create NLP processor instance"""
        try:
            return NLPProcessor(model_name="en_core_web_sm")
        except OSError:
            pytest.skip("spaCy model not installed. Run: python -m spacy download en_core_web_sm")

    def test_nlp_processor_initialization(self, nlp_processor):
        """Test NLP processor initializes correctly"""
        assert nlp_processor is not None
        assert nlp_processor.model_name == "en_core_web_sm"
        assert nlp_processor.cache_enabled is True

    def test_lazy_loading(self, nlp_processor):
        """Test that spaCy model is lazily loaded"""
        # Model should be None before first use
        assert nlp_processor._nlp is None

        # Access nlp property to trigger loading
        _ = nlp_processor.nlp

        # Model should now be loaded
        assert nlp_processor._nlp is not None

    def test_entity_extraction_basic(self, nlp_processor):
        """Test basic entity extraction"""
        entities = nlp_processor.entity_extraction(SAMPLE_ARTICLE_CONTENT)

        # Should extract entities
        assert len(entities) > 0

        # Check entity structure
        for entity in entities:
            assert "text" in entity
            assert "label" in entity
            assert "start" in entity
            assert "end" in entity

        # Should find specific entities
        entity_texts = [e["text"] for e in entities]
        assert any("Tesla" in text for text in entity_texts)
        assert any("Samsung" in text for text in entity_texts)
        assert any("Elon Musk" in text for text in entity_texts)

    def test_entity_extraction_filtered(self, nlp_processor):
        """Test entity extraction with type filtering"""
        # Extract only organization entities
        entities = nlp_processor.entity_extraction(
            SAMPLE_ARTICLE_CONTENT,
            entity_types=['ORG']
        )

        # Should only return ORG entities
        for entity in entities:
            assert entity["label"] == "ORG"

        # Should find organizations
        entity_texts = [e["text"] for e in entities]
        assert any("Tesla" in text for text in entity_texts)
        assert any("Samsung" in text for text in entity_texts)

    def test_entity_extraction_empty_text(self, nlp_processor):
        """Test entity extraction with empty text"""
        entities = nlp_processor.entity_extraction("")
        assert entities == []

        entities = nlp_processor.entity_extraction("   ")
        assert entities == []

    def test_sentiment_analysis_positive(self, nlp_processor):
        """Test sentiment analysis on positive text"""
        sentiment = nlp_processor.sentiment_analysis(POSITIVE_TEXT)

        assert "polarity" in sentiment
        assert "subjectivity" in sentiment
        assert "classification" in sentiment

        assert sentiment["polarity"] > 0.1  # Should be positive
        assert sentiment["classification"] == "positive"

    def test_sentiment_analysis_negative(self, nlp_processor):
        """Test sentiment analysis on negative text"""
        sentiment = nlp_processor.sentiment_analysis(NEGATIVE_TEXT)

        assert sentiment["polarity"] < -0.1  # Should be negative
        assert sentiment["classification"] == "negative"

    def test_sentiment_analysis_neutral(self, nlp_processor):
        """Test sentiment analysis on neutral text"""
        sentiment = nlp_processor.sentiment_analysis(NEUTRAL_TEXT)

        assert -0.1 <= sentiment["polarity"] <= 0.1  # Should be near neutral
        assert sentiment["classification"] == "neutral"

    def test_sentiment_analysis_empty(self, nlp_processor):
        """Test sentiment analysis with empty text"""
        sentiment = nlp_processor.sentiment_analysis("")

        assert sentiment["polarity"] == 0.0
        assert sentiment["subjectivity"] == 0.0
        assert sentiment["classification"] == "neutral"

    def test_relationship_extraction(self, nlp_processor):
        """Test relationship extraction between entities"""
        relationships = nlp_processor.relationship_extraction(MULTI_ENTITY_TEXT)

        # Should find relationships between entities
        assert len(relationships) > 0

        # Check relationship structure
        for rel in relationships:
            assert "entity1" in rel
            assert "entity2" in rel
            assert "distance" in rel
            assert "context" in rel

            assert "text" in rel["entity1"]
            assert "label" in rel["entity1"]

    def test_relationship_extraction_distance_filter(self, nlp_processor):
        """Test relationship extraction with distance filtering"""
        # Very short distance - should find fewer relationships
        relationships_short = nlp_processor.relationship_extraction(
            MULTI_ENTITY_TEXT,
            max_distance=20
        )

        # Longer distance - should find more relationships
        relationships_long = nlp_processor.relationship_extraction(
            MULTI_ENTITY_TEXT,
            max_distance=100
        )

        # Longer distance should find at least as many relationships
        assert len(relationships_long) >= len(relationships_short)

    def test_keyword_extraction(self, nlp_processor):
        """Test keyword extraction"""
        keywords = nlp_processor.keyword_extraction(SAMPLE_ARTICLE_CONTENT, top_n=10)

        # Should extract keywords
        assert len(keywords) > 0
        assert len(keywords) <= 10  # Should respect top_n limit

        # Check keyword structure
        for keyword in keywords:
            assert "text" in keyword
            assert "pos" in keyword
            assert "frequency" in keyword

        # Should find relevant keywords
        keyword_texts = [kw["text"] for kw in keywords]
        assert any("partnership" in text.lower() for text in keyword_texts)
        assert any("battery" in text.lower() or "technology" in text.lower() for text in keyword_texts)

    def test_keyword_extraction_pos_filter(self, nlp_processor):
        """Test keyword extraction with POS tag filtering"""
        # Extract only proper nouns
        keywords = nlp_processor.keyword_extraction(
            SAMPLE_ARTICLE_CONTENT,
            pos_tags=['PROPN']
        )

        # Should only return proper nouns
        for keyword in keywords:
            assert keyword["pos"] == "PROPN"

    def test_process_article(self, nlp_processor):
        """Test full article processing pipeline"""
        results = nlp_processor.process_article(
            SAMPLE_ARTICLE_TITLE,
            SAMPLE_ARTICLE_CONTENT,
            extract_relationships=True
        )

        # Should contain all NLP results
        assert "entities" in results
        assert "sentiment" in results
        assert "keywords" in results
        assert "relationships" in results

        # All should have content
        assert len(results["entities"]) > 0
        assert results["sentiment"]["classification"] in ["positive", "negative", "neutral"]
        assert len(results["keywords"]) > 0

    def test_process_article_no_relationships(self, nlp_processor):
        """Test article processing without relationship extraction"""
        results = nlp_processor.process_article(
            SAMPLE_ARTICLE_TITLE,
            SAMPLE_ARTICLE_CONTENT,
            extract_relationships=False
        )

        # Should not include relationships
        assert "relationships" not in results

    def test_is_english_detection(self, nlp_processor):
        """Test English language detection"""
        # English text
        assert nlp_processor._is_english("This is English text") is True

        # Non-English text (Chinese)
        assert nlp_processor._is_english("这是中文文本") is False

        # Mixed text (mostly English)
        assert nlp_processor._is_english("This is mostly English with some 中文") is True

        # Empty text
        assert nlp_processor._is_english("") is False

    def test_non_english_graceful_handling(self, nlp_processor):
        """Test graceful handling of non-English text"""
        # Non-English text should return empty results
        entities = nlp_processor.entity_extraction("这是中文文本")
        assert entities == []


class TestConvenienceFunctions:
    """Test suite for convenience functions"""

    def test_get_nlp_processor_singleton(self):
        """Test that get_nlp_processor returns singleton instance"""
        try:
            processor1 = get_nlp_processor()
            processor2 = get_nlp_processor()

            # Should be same instance (cached)
            assert processor1 is processor2
        except OSError:
            pytest.skip("spaCy model not installed")

    def test_analyze_text_basic(self):
        """Test quick text analysis function"""
        try:
            results = analyze_text(SAMPLE_ARTICLE_CONTENT, include_relationships=False)

            assert "entities" in results
            assert "sentiment" in results
            assert "keywords" in results
            assert "relationships" not in results
        except OSError:
            pytest.skip("spaCy model not installed")

    def test_analyze_text_with_relationships(self):
        """Test text analysis with relationships"""
        try:
            results = analyze_text(MULTI_ENTITY_TEXT, include_relationships=True)

            assert "entities" in results
            assert "sentiment" in results
            assert "keywords" in results
            assert "relationships" in results
        except OSError:
            pytest.skip("spaCy model not installed")


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def nlp_processor(self):
        """Fixture to create NLP processor instance"""
        try:
            return NLPProcessor(model_name="en_core_web_sm")
        except OSError:
            pytest.skip("spaCy model not installed")

    def test_very_long_text(self, nlp_processor):
        """Test processing very long text"""
        # Generate long text
        long_text = SAMPLE_ARTICLE_CONTENT * 100

        # Should handle without crashing
        entities = nlp_processor.entity_extraction(long_text)
        assert len(entities) > 0

    def test_special_characters(self, nlp_processor):
        """Test text with special characters"""
        special_text = "Tesla's Q3 results showed $10B revenue @15% growth! #EVs 🚗"

        # Should handle special characters gracefully
        entities = nlp_processor.entity_extraction(special_text)
        sentiment = nlp_processor.sentiment_analysis(special_text)

        assert isinstance(entities, list)
        assert "classification" in sentiment

    def test_only_numbers(self, nlp_processor):
        """Test text with only numbers"""
        number_text = "123 456 789"

        entities = nlp_processor.entity_extraction(number_text)
        keywords = nlp_processor.keyword_extraction(number_text)

        # Should return empty or minimal results
        assert isinstance(entities, list)
        assert isinstance(keywords, list)

    def test_single_word(self, nlp_processor):
        """Test single word input"""
        sentiment = nlp_processor.sentiment_analysis("excellent")

        assert sentiment["polarity"] > 0  # Positive word
        assert sentiment["classification"] == "positive"


class TestIntegration:
    """Integration tests with realistic scenarios"""

    @pytest.fixture
    def nlp_processor(self):
        """Fixture to create NLP processor instance"""
        try:
            return NLPProcessor(model_name="en_core_web_sm")
        except OSError:
            pytest.skip("spaCy model not installed")

    def test_competitor_mention_detection(self, nlp_processor):
        """Test detection of competitor mentions in news"""
        competitor_text = """
        Tesla faces increased competition from BYD, which has overtaken it in global EV sales.
        Traditional automakers like Ford and GM are also ramping up electric vehicle production.
        Chinese manufacturers including NIO and XPeng are expanding into European markets.
        """

        entities = nlp_processor.entity_extraction(competitor_text, entity_types=['ORG'])

        # Should extract competitor organizations
        org_names = [e["text"] for e in entities]

        assert any("Tesla" in name for name in org_names)
        assert any("BYD" in name for name in org_names)
        assert any("Ford" in name or "GM" in name for name in org_names)

    def test_partnership_detection(self, nlp_processor):
        """Test detection of partnership relationships"""
        partnership_text = """
        Apple announced a strategic partnership with OpenAI to integrate AI features.
        Microsoft is collaborating with Meta on open-source AI development.
        """

        relationships = nlp_processor.relationship_extraction(partnership_text)

        # Should find relationships between companies
        assert len(relationships) > 0

        # Check for company pairs
        pairs = [(rel["entity1"]["text"], rel["entity2"]["text"]) for rel in relationships]
        assert len(pairs) > 0

    def test_sentiment_trends(self, nlp_processor):
        """Test sentiment analysis for market sentiment tracking"""
        positive_news = "Company exceeds earnings expectations with record revenue growth"
        negative_news = "Company faces regulatory challenges and declining market share"

        pos_sentiment = nlp_processor.sentiment_analysis(positive_news)
        neg_sentiment = nlp_processor.sentiment_analysis(negative_news)

        # Positive news should have higher polarity
        assert pos_sentiment["polarity"] > neg_sentiment["polarity"]
        assert pos_sentiment["classification"] == "positive"
        assert neg_sentiment["classification"] == "negative"


# Fixtures for VCR cassettes (if needed for future web scraping tests)
@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration for recording HTTP interactions"""
    return {
        "filter_headers": ["authorization", "api-key"],
        "record_mode": "once",
    }


if __name__ == "__main__":
    # Run tests with: pytest tests/test_nlp_tool.py -v
    pytest.main([__file__, "-v"])
