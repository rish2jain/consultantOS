"""
Financial Agent - Analyzes company financials using SEC and yfinance
"""
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import FinancialSnapshot
from consultantos.tools import yfinance_tool, sec_edgar_tool


class FinancialAgent(BaseAgent):
    """Financial analyst agent"""
    
    def __init__(self):
        super().__init__(
            name="financial_analyst",
            model="gemini-2.0-flash-exp"
        )
        self.instruction = """
        You are a financial analyst with expertise in:
        - Financial statement analysis
        - Valuation metrics interpretation
        - Risk assessment

        Analyze company financial performance using SEC filings and stock data.
        Focus on: revenue growth, profitability, cash flow, valuation metrics.
        """
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> FinancialSnapshot:
        """
        Execute financial analysis using SEC filings and stock market data.

        Gathers and analyzes financial performance metrics using yfinance for
        market data and SEC EDGAR API for official filings.

        Args:
            input_data: Dictionary containing:
                - company: Company name
                - ticker: Stock ticker symbol (required)

        Returns:
            FinancialSnapshot object containing:
                - revenue: Revenue figures and growth rates
                - profitability: Profit margins and net income
                - cash_flow: Operating cash flow metrics
                - debt_equity_ratio: Leverage ratio
                - valuation_metrics: P/E ratio, market cap, etc.
                - growth_indicators: YoY growth rates
                - risk_factors: Financial risk assessment

        Raises:
            ValueError: If ticker is not provided
            Exception: If financial data fetch or analysis fails
        """
        company = input_data.get("company", "")
        ticker = input_data.get("ticker")
        
        # Require ticker or raise validation error
        if not ticker:
            raise ValueError(f"Ticker symbol is required for company '{company}'. Please provide a ticker parameter.")
        
        # Get financial data
        yfinance_data = yfinance_tool(ticker)
        sec_data = sec_edgar_tool(ticker) or {}  # Ensure sec_data is never None
        
        # Check for errors
        has_error = yfinance_data.get("error") or sec_data.get("error")
        
        # Format financial context
        financial_context = self._format_financial_data(yfinance_data, sec_data)
        
        prompt = f"""
        {self.instruction}
        
        Analyze financials for: {company} (Ticker: {ticker})
        
        Financial Data:
        {financial_context}
        
        Extract and structure:
        1. Ticker symbol
        2. Market cap
        3. Revenue (latest annual)
        4. Revenue growth (YoY %)
        5. Profit margin
        6. P/E ratio
        7. Key metrics (dict)
        8. Risk assessment (Low/Medium/High with rationale)
        """
        
        try:
            result = self.structured_client.create(
                response_model=FinancialSnapshot,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return result
        except Exception as e:
            # Fallback
            info = yfinance_data.get("company_info", {})
            risk_note = "Unable to assess due to data limitations"
            if has_error:
                risk_note = "Partial data available - some sources unavailable"
            
            return FinancialSnapshot(
                ticker=ticker,
                market_cap=info.get("marketCap"),
                revenue=info.get("totalRevenue"),
                revenue_growth=None,
                profit_margin=info.get("profitMargins"),
                pe_ratio=info.get("trailingPE"),
                key_metrics=info,
                risk_assessment=f"Medium - {risk_note}"
            )
    
    def _format_financial_data(self, yfinance_data: Dict[str, Any], sec_data: Dict[str, Any]) -> str:
        """Format financial data for LLM"""
        info = yfinance_data.get("company_info", {})
        market_cap = info.get('marketCap', 'N/A')
        revenue = info.get('totalRevenue', 'N/A')
        
        # Format market cap
        if isinstance(market_cap, (int, float)):
            market_cap_str = f"${market_cap:,.0f}"
        else:
            market_cap_str = str(market_cap)
        
        # Format revenue
        if isinstance(revenue, (int, float)):
            revenue_str = f"${revenue:,.0f}"
        else:
            revenue_str = str(revenue)
        
        formatted = f"""
        Market Cap: {market_cap_str}
        Revenue: {revenue_str}
        Profit Margin: {info.get('profitMargins', 'N/A')}
        P/E Ratio: {info.get('trailingPE', 'N/A')}
        """
        if sec_data:
            formatted += f"\nSEC Filing Date: {sec_data.get('filing_date', 'N/A')}"
        return formatted

