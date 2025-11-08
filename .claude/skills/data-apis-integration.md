---
name: data-apis-integration
description: Expert integration of SEC Edgar, yfinance, Google Trends (pytrends), and financial data APIs for business intelligence systems with caching, error handling, and rate limit management
category: skill
---

# Data APIs Integration Expert

Comprehensive guide for integrating financial and market data APIs into business intelligence systems.

## Overview

Critical data sources for automated business analysis:

1. **SEC Edgar**: US public company filings (10-K, 10-Q, 8-K)
2. **yfinance**: Stock prices, financial metrics, company info
3. **pytrends**: Google Trends search interest data
4. **Alpha Vantage**: Real-time and historical financial data (backup)

## 1. SEC Edgar API

### Installation

```bash
pip install edgartools
```

### Basic Usage

```python
from edgar import Company, set_identity

# Set identity (required by SEC)
set_identity("Your Name your.email@example.com")

# Get company
company = Company("TSLA")  # Ticker symbol

# Basic info
print(company.name)  # Tesla Inc
print(company.cik)   # Central Index Key
print(company.sic)   # Standard Industrial Classification

# Get filings
filings = company.get_filings(form="10-K")  # Annual reports
print(f"Found {len(filings)} 10-K filings")

# Latest filing
latest = filings[0]
print(latest.filing_date)
print(latest.accession_number)
```

### Extract Financial Data

```python
from edgar import Company

async def get_company_financials(ticker: str) -> dict:
    """Extract financial metrics from SEC filings"""

    company = Company(ticker)

    # Get latest 10-K (annual report)
    annual_filings = company.get_filings(form="10-K")
    latest_10k = annual_filings[0] if annual_filings else None

    # Get latest 10-Q (quarterly report)
    quarterly_filings = company.get_filings(form="10-Q")
    latest_10q = quarterly_filings[0] if quarterly_filings else None

    financials = {
        "company_name": company.name,
        "ticker": ticker,
        "cik": company.cik,
        "industry": company.sic_description,
        "latest_annual_filing": None,
        "latest_quarterly_filing": None
    }

    # Extract from 10-K
    if latest_10k:
        financials["latest_annual_filing"] = {
            "filing_date": latest_10k.filing_date,
            "fiscal_year": latest_10k.fiscal_year,
            "accession_number": latest_10k.accession_number,
            "url": latest_10k.document.url
        }

        # Extract financial statements (if available)
        try:
            statements = latest_10k.financials
            if statements:
                financials["annual_financials"] = {
                    "balance_sheet": statements.balance_sheet.to_dict(),
                    "income_statement": statements.income_statement.to_dict(),
                    "cash_flow": statements.cash_flow.to_dict()
                }
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to extract annual financials: {e}")
            # Skip assigning annual_financials on expected errors

    # Extract from 10-Q
    if latest_10q:
        financials["latest_quarterly_filing"] = {
            "filing_date": latest_10q.filing_date,
            "fiscal_quarter": latest_10q.fiscal_period,
            "accession_number": latest_10q.accession_number
        }

    return financials
```

### Search Filings

```python
from edgar import find

# Search for specific filings
results = find(
    "cybersecurity",  # Search term
    form="10-K",      # Filing type
    start_date="2023-01-01",
    end_date="2023-12-31"
)

for filing in results:
    print(f"{filing.company_name}: {filing.filing_date}")
```

### Error Handling & Rate Limiting

```python
import asyncio
from functools import wraps
from typing import Callable

def rate_limit_edgar(calls_per_second: int = 10):
    """SEC Edgar requires max 10 requests/second"""

    min_interval = 1.0 / calls_per_second
    last_call = 0

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_call
            current = asyncio.get_event_loop().time()
            elapsed = current - last_call

            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

            last_call = asyncio.get_event_loop().time()
            return await func(*args, **kwargs)

        return wrapper
    return decorator


@rate_limit_edgar(calls_per_second=10)
async def fetch_company_data(ticker: str):
    try:
        company = Company(ticker)
        return await get_company_financials(ticker)
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None
```

## 2. yfinance (Yahoo Finance)

### Installation

```bash
pip install yfinance
```

### Basic Usage

```python
import yfinance as yf

# Get ticker object
ticker = yf.Ticker("TSLA")

# Company info
info = ticker.info
print(info['longName'])           # Tesla, Inc.
print(info['sector'])              # Consumer Cyclical
print(info['industry'])            # Auto Manufacturers
print(info['marketCap'])           # Market capitalization
print(info['trailingPE'])          # P/E ratio
print(info['profitMargins'])       # Profit margin

# Financial statements
balance_sheet = ticker.balance_sheet
income_stmt = ticker.income_stmt
cash_flow = ticker.cashflow

# Historical data
hist = ticker.history(period="1y")  # 1 year
print(hist.head())

# Dividends and splits
dividends = ticker.dividends
splits = ticker.splits
```

### Extract Key Metrics

```python
import yfinance as yf
import pandas as pd

async def get_stock_metrics(ticker: str) -> dict:
    """Extract comprehensive stock and financial metrics"""

    stock = yf.Ticker(ticker)
    info = stock.info

    metrics = {
        # Company Info
        "company_name": info.get('longName', 'N/A'),
        "ticker": ticker,
        "sector": info.get('sector', 'N/A'),
        "industry": info.get('industry', 'N/A'),

        # Valuation Metrics
        "market_cap": info.get('marketCap'),
        "enterprise_value": info.get('enterpriseValue'),
        "price_to_earnings": info.get('trailingPE'),
        "price_to_sales": info.get('priceToSalesTrailing12Months'),
        "price_to_book": info.get('priceToBook'),
        "peg_ratio": info.get('pegRatio'),

        # Profitability Metrics
        "profit_margin": info.get('profitMargins'),
        "operating_margin": info.get('operatingMargins'),
        "return_on_equity": info.get('returnOnEquity'),
        "return_on_assets": info.get('returnOnAssets'),

        # Growth Metrics
        "revenue_growth": info.get('revenueGrowth'),
        "earnings_growth": info.get('earningsGrowth'),

        # Financial Health
        "total_cash": info.get('totalCash'),
        "total_debt": info.get('totalDebt'),
        "current_ratio": info.get('currentRatio'),
        "debt_to_equity": info.get('debtToEquity'),

        # Stock Performance
        "52_week_high": info.get('fiftyTwoWeekHigh'),
        "52_week_low": info.get('fiftyTwoWeekLow'),
        "50_day_average": info.get('fiftyDayAverage'),
        "200_day_average": info.get('twoHundredDayAverage'),

        # Analyst Recommendations
        "target_high_price": info.get('targetHighPrice'),
        "target_low_price": info.get('targetLowPrice'),
        "target_mean_price": info.get('targetMeanPrice'),
        "recommendation": info.get('recommendationKey')
    }

    # Historical performance
    hist = stock.history(period="1y")
    if not hist.empty:
        metrics["1_year_return"] = (
            (hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] * 100
        )
        metrics["volatility"] = hist['Close'].pct_change().std() * 100

    return metrics
```

### Compare Multiple Stocks

```python
import yfinance as yf
import pandas as pd

def compare_stocks(tickers: list[str]) -> pd.DataFrame:
    """Compare key metrics across multiple stocks"""

    data = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info

        data.append({
            'Ticker': ticker,
            'Company': info.get('longName', 'N/A'),
            'Market Cap': info.get('marketCap', 0),
            'P/E Ratio': info.get('trailingPE', 0),
            'Profit Margin': info.get('profitMargins', 0) * 100,
            'Revenue Growth': info.get('revenueGrowth', 0) * 100,
            '1Y Return': get_1y_return(ticker)
        })

    df = pd.DataFrame(data)
    return df.sort_values('Market Cap', ascending=False)


def get_1y_return(ticker: str) -> float:
    """Calculate 1-year stock return"""
    import logging
    import requests
    logger = logging.getLogger(__name__)
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if not hist.empty:
            return (hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] * 100
    except (KeyError, IndexError, ValueError, requests.exceptions.RequestException) as e:
        logger.warning(f"Failed to calculate 1y return for {ticker}: {e}")
        return 0.0
    except Exception as e:
        logger.error(f"Unexpected error calculating 1y return for {ticker}: {e}")
        return 0.0
```

### Error Handling

```python
from functools import wraps
import time

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Retry decorator for yfinance (web scraping can be unreliable)"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"Failed after {max_retries} attempts: {e}")
                        return None
                    await asyncio.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator


@retry_on_failure(max_retries=3)
async def safe_get_stock_data(ticker: str):
    return await get_stock_metrics(ticker)
```

## 3. Google Trends (pytrends)

### Installation

```bash
pip install pytrends
```

### Basic Usage

```python
from pytrends.request import TrendReq

# Initialize
pytrend = TrendReq(hl='en-US', tz=360)

# Build payload
keywords = ["Tesla", "Ford", "GM"]
pytrend.build_payload(
    keywords,
    timeframe='today 12-m',  # Last 12 months
    geo='US'                 # United States
)

# Interest over time
interest_over_time = pytrend.interest_over_time()
print(interest_over_time.head())

# Interest by region
interest_by_region = pytrend.interest_by_region()
print(interest_by_region.head())

# Related queries
related = pytrend.related_queries()
print(related['Tesla']['top'])     # Top related queries
print(related['Tesla']['rising'])  # Rising related queries
```

### Extract Market Trends

```python
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta

async def analyze_market_trends(
    keywords: list[str],
    timeframe: str = 'today 12-m',
    geo: str = ''
) -> dict:
    """Comprehensive Google Trends analysis"""

    pytrend = TrendReq(hl='en-US', tz=360)

    # Build payload
    pytrend.build_payload(
        keywords,
        timeframe=timeframe,
        geo=geo
    )

    # Interest over time
    interest_df = pytrend.interest_over_time()

    trends = {
        "keywords": keywords,
        "timeframe": timeframe,
        "geography": geo if geo else "Worldwide",
        "data_points": []
    }

    if not interest_df.empty:
        # Remove 'isPartial' column if present
        if 'isPartial' in interest_df.columns:
            interest_df = interest_df.drop('isPartial', axis=1)

        # Overall trend direction
        for keyword in keywords:
            if keyword in interest_df.columns:
                values = interest_df[keyword]

                # Calculate trend
                recent_avg = values[-30:].mean()  # Last 30 days
                earlier_avg = values[:30].mean()  # First 30 days

                trend_direction = "Growing" if recent_avg > earlier_avg * 1.1 else \
                                 "Declining" if recent_avg < earlier_avg * 0.9 else \
                                 "Stable"

                # Peak and low
                peak_date = values.idxmax()
                low_date = values.idxmin()

                trends["data_points"].append({
                    "keyword": keyword,
                    "trend_direction": trend_direction,
                    "current_interest": int(values[-1]),
                    "average_interest": int(values.mean()),
                    "peak_interest": int(values.max()),
                    "peak_date": peak_date.strftime("%Y-%m-%d"),
                    "low_interest": int(values.min()),
                    "low_date": low_date.strftime("%Y-%m-%d"),
                    "volatility": float(values.std())
                })

    # Interest by region (top 10)
    import logging
    import requests
    logger = logging.getLogger(__name__)
    try:
        region_df = pytrend.interest_by_region()
        if not region_df.empty:
            top_regions = {}
            for keyword in keywords:
                if keyword in region_df.columns:
                    top_10 = region_df[keyword].nlargest(10).to_dict()
                    top_regions[keyword] = top_10
            trends["top_regions"] = top_regions
    except (KeyError, AttributeError, ValueError, requests.exceptions.RequestException) as e:
        logger.error(f"Failed to fetch top regions: {e}")
        trends["top_regions"] = {}
    except Exception as e:
        logger.error(f"Unexpected error fetching top regions: {e}")
        trends["top_regions"] = {}

    # Related queries
    try:
        related = pytrend.related_queries()
        trends["related_queries"] = {}
        for keyword in keywords:
            if keyword in related:
                trends["related_queries"][keyword] = {
                    "top": related[keyword]['top'].head(5).to_dict() if related[keyword]['top'] is not None else {},
                    "rising": related[keyword]['rising'].head(5).to_dict() if related[keyword]['rising'] is not None else {}
                }
    except (KeyError, AttributeError, ValueError, requests.exceptions.RequestException) as e:
        logger.error(f"Failed to fetch related queries: {e}")
        trends["related_queries"] = {}
    except Exception as e:
        logger.error(f"Unexpected error fetching related queries: {e}")
        trends["related_queries"] = {}

    return trends
```

### Compare Competitors

```python
async def compare_brand_interest(brands: list[str]) -> dict:
    """Compare search interest across competing brands"""

    pytrend = TrendReq(hl='en-US', tz=360)

    # Google Trends allows max 5 keywords
    if len(brands) > 5:
        brands = brands[:5]

    pytrend.build_payload(brands, timeframe='today 12-m')

    interest_df = pytrend.interest_over_time()

    if interest_df.empty:
        return {"error": "No data available"}

    # Remove 'isPartial' column
    if 'isPartial' in interest_df.columns:
        interest_df = interest_df.drop('isPartial', axis=1)

    comparison = {
        "brands": brands,
        "market_leader": None,
        "fastest_growing": None,
        "brand_scores": []
    }

    # Calculate metrics for each brand
    for brand in brands:
        if brand in interest_df.columns:
            values = interest_df[brand]

            # Growth calculation
            recent = values[-90:].mean()  # Last 3 months
            earlier = values[:90].mean()  # First 3 months
            growth = ((recent - earlier) / earlier * 100) if earlier > 0 else 0

            score = {
                "brand": brand,
                "average_interest": float(values.mean()),
                "current_interest": float(values[-1]),
                "peak_interest": float(values.max()),
                "growth_rate": float(growth),
                "consistency": float(100 - values.std())  # Lower std = more consistent
            }

            comparison["brand_scores"].append(score)

    # Determine market leader (highest average)
    comparison["brand_scores"].sort(key=lambda x: x["average_interest"], reverse=True)
    comparison["market_leader"] = comparison["brand_scores"][0]["brand"]

    # Determine fastest growing
    fastest = max(comparison["brand_scores"], key=lambda x: x["growth_rate"])
    comparison["fastest_growing"] = fastest["brand"]

    return comparison
```

### Rate Limiting for pytrends

```python
import asyncio
from functools import wraps

def rate_limit_trends(requests_per_minute: int = 60):
    """Rate limit Google Trends requests"""

    min_interval = 60.0 / requests_per_minute
    last_call = 0

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_call
            current = asyncio.get_event_loop().time()
            elapsed = current - last_call

            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

            last_call = asyncio.get_event_loop().time()
            return await func(*args, **kwargs)

        return wrapper
    return decorator


@rate_limit_trends(requests_per_minute=60)
async def fetch_trends_data(keywords: list[str]):
    return await analyze_market_trends(keywords)
```

## Caching Strategy

```python
from diskcache import Cache
from functools import wraps
import hashlib
import json

# Initialize cache
cache = Cache('/tmp/bi_data_cache', size_limit=int(1e9))  # 1GB

def cache_data(expire_seconds: int = 3600):
    """Cache decorator for data API calls"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Check cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            # Fetch fresh data
            result = await func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, expire=expire_seconds)

            return result

        return wrapper
    return decorator


# Usage
@cache_data(expire_seconds=86400)  # Cache for 24 hours
async def get_cached_stock_data(ticker: str):
    return await get_stock_metrics(ticker)


@cache_data(expire_seconds=3600)  # Cache for 1 hour
async def get_cached_trends(keywords: list[str]):
    return await analyze_market_trends(keywords)


@cache_data(expire_seconds=86400)  # Cache for 24 hours
async def get_cached_sec_filings(ticker: str):
    return await get_company_financials(ticker)
```

## Integrated Data Pipeline

```python
from typing import Dict, Any
import asyncio

class DataIntegrationPipeline:
    """Integrate all data sources with caching and error handling"""

    def __init__(self):
        self.cache = Cache('/tmp/bi_cache', size_limit=int(1e9))

    async def gather_company_data(
        self,
        company_name: str,
        ticker: str,
        industry: str
    ) -> Dict[str, Any]:
        """Gather data from all sources in parallel"""

        # Run all data fetches in parallel
        tasks = [
            self._fetch_sec_data(ticker),
            self._fetch_stock_data(ticker),
            self._fetch_trends_data([company_name, industry])
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "company_name": company_name,
            "ticker": ticker,
            "industry": industry,
            "sec_data": results[0] if not isinstance(results[0], Exception) else None,
            "stock_data": results[1] if not isinstance(results[1], Exception) else None,
            "trends_data": results[2] if not isinstance(results[2], Exception) else None,
            "errors": [str(r) for r in results if isinstance(r, Exception)]
        }

    @cache_data(expire_seconds=86400)
    async def _fetch_sec_data(self, ticker: str):
        return await get_company_financials(ticker)

    @cache_data(expire_seconds=3600)
    async def _fetch_stock_data(self, ticker: str):
        return await get_stock_metrics(ticker)

    @cache_data(expire_seconds=3600)
    async def _fetch_trends_data(self, keywords: list[str]):
        return await analyze_market_trends(keywords)


# Usage
async def main():
    pipeline = DataIntegrationPipeline()

    data = await pipeline.gather_company_data(
        company_name="Tesla",
        ticker="TSLA",
        industry="Electric Vehicles"
    )

    print(f"SEC Data: {data['sec_data'] is not None}")
    print(f"Stock Data: {data['stock_data'] is not None}")
    print(f"Trends Data: {data['trends_data'] is not None}")
    print(f"Errors: {data['errors']}")
```

## Best Practices

1. **Always set SEC identity**: Required by Edgar API
2. **Respect rate limits**: Edgar (10/sec), yfinance (unreliable), pytrends (60/min)
3. **Implement caching**: Financial data doesn't change frequently
4. **Error handling**: All APIs can fail, have fallbacks
5. **Parallel execution**: Fetch from multiple sources simultaneously
6. **Validation**: Check data quality and completeness

## Cloud Run Integration

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()
pipeline = DataIntegrationPipeline()

@app.post("/data/company/{ticker}")
async def fetch_company_data(
    ticker: str,
    background_tasks: BackgroundTasks
):
    try:
        data = await pipeline.gather_company_data(
            company_name=ticker,  # Could lookup name
            ticker=ticker,
            industry="Unknown"
        )

        return {
            "status": "success",
            "ticker": ticker,
            "data_sources": {
                "sec": data['sec_data'] is not None,
                "stock": data['stock_data'] is not None,
                "trends": data['trends_data'] is not None
            },
            "errors": data['errors']
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

This skill provides production-ready integration of critical financial and market data APIs.
