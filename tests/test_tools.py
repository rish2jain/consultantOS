"""
Tests for tool implementations
"""
import pytest
from unittest.mock import Mock, patch
from consultantos.tools import (
    tavily_search_tool,
    google_trends_tool,
    yfinance_tool,
    sec_edgar_tool,
    resolve_ticker,
    guess_ticker
)


class TestTavilyTool:
    """Tests for Tavily search tool"""
    
    def test_tavily_search_success(self):
        """Test successful Tavily search"""
        with patch('consultantos.tools.tavily_tool._get_tavily_client') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.search.return_value = {
                "results": [
                    {
                        "title": "Test Result",
                        "url": "https://example.com",
                        "content": "Test content"
                    }
                ]
            }
            mock_client.return_value = mock_client_instance
            
            result = tavily_search_tool("test query")
            
            assert "results" in result
            assert len(result["results"]) > 0
            assert result["query"] == "test query"
    
    def test_tavily_search_error_handling(self):
        """Test Tavily search error handling"""
        with patch('consultantos.tools.tavily_tool._get_tavily_client') as mock_client:
            mock_client.side_effect = Exception("API Error")
            
            result = tavily_search_tool("test query")
            
            assert "error" in result
            assert result["total_results"] == 0


class TestFinancialTools:
    """Tests for financial data tools"""
    
    def test_yfinance_tool_success(self):
        """Test successful yfinance fetch"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {
                "marketCap": 1000000,
                "totalRevenue": 500000,
                "profitMargins": 0.1,
                "trailingPE": 50.0
            }
            mock_stock.history.return_value = Mock(empty=False, to_dict=lambda: {})
            mock_stock.financials = Mock(empty=False, to_dict=lambda: {})
            mock_ticker.return_value = mock_stock
            
            result = yfinance_tool("TSLA")
            
            assert "company_info" in result
            assert result["ticker"] == "TSLA"
    
    def test_yfinance_tool_error_handling(self):
        """Test yfinance error handling"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.side_effect = Exception("API Error")
            
            result = yfinance_tool("INVALID")
            
            assert "error" in result
            assert result["ticker"] == "INVALID"


class TestTickerResolver:
    """Tests for ticker resolution"""
    
    def test_resolve_ticker_success(self):
        """Test successful ticker resolution"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {
                "symbol": "TSLA",
                "longName": "Tesla, Inc."
            }
            mock_ticker.return_value = mock_stock
            
            result = resolve_ticker("Tesla")
            
            assert result == "TSLA"
    
    def test_resolve_ticker_not_found(self):
        """Test ticker resolution when not found"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {}
            mock_ticker.return_value = mock_stock
            
            result = resolve_ticker("NonexistentCompany")
            
            assert result is None
    
    def test_guess_ticker(self):
        """Test ticker guessing"""
        result = guess_ticker("Tesla Inc")
        assert len(result) == 4
        assert result.isupper()
        
        result2 = guess_ticker("Apple Corporation")
        assert len(result2) == 4

