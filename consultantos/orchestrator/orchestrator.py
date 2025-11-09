"""
Multi-agent orchestrator for ConsultantOS
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from consultantos_core import models as core_models
from consultantos.agents import (
    ResearchAgent,
    MarketAgent,
    FinancialAgent,
    FrameworkAgent,
    SynthesisAgent
)
from consultantos.cache import cache_key, semantic_cache_lookup, semantic_cache_store
from consultantos.monitoring import track_operation, log_cache_hit, log_cache_miss

logger = logging.getLogger(__name__)

AnalysisRequest = core_models.AnalysisRequest
StrategicReport = core_models.StrategicReport
ExecutiveSummary = core_models.ExecutiveSummary


class AnalysisOrchestrator:
    """Orchestrates multi-agent analysis workflow"""
    
    def __init__(self) -> None:
        """Initialize orchestrator with all agent instances."""
        self.research_agent = ResearchAgent()
        self.market_agent = MarketAgent()
        self.financial_agent = FinancialAgent()
        self.framework_agent = FrameworkAgent()
        self.synthesis_agent = SynthesisAgent()
    
    async def execute(self, request: AnalysisRequest) -> StrategicReport:
        """
        Execute complete analysis workflow
        
        Phase 1: Parallel data gathering (Research, Market, Financial)
        Phase 2: Sequential analysis (Framework → Synthesis)
        
        Args:
            request: Analysis request containing company info and framework selection
            
        Returns:
            Complete strategic report with all analysis phases
            
        Raises:
            Exception: If all Phase 1 agents fail or orchestration fails
        """
        # Check semantic cache first
        cache_key_str = cache_key(
            request.company,
            request.frameworks,
            request.industry
        )
        
        # Try semantic cache lookup
        cached_result = await semantic_cache_lookup(
            request.company,
            request.frameworks
        )
        
        if cached_result:
            log_cache_hit(cache_key_str, "semantic")
            return cached_result
        
        log_cache_miss(cache_key_str)
        
        with track_operation(
            "orchestration",
            company=request.company,
            frameworks=request.frameworks
        ):
            try:
                # Phase 1: Parallel data gathering
                phase1_results = await self._execute_parallel_phase(request)
                
                # Phase 2: Sequential framework analysis
                framework_results = await self._execute_framework_phase(
                    request, phase1_results
                )
                
                # Phase 3: Synthesis
                synthesis_results = await self._execute_synthesis_phase(
                    request, phase1_results, framework_results
                )
                
                # Assemble final report
                report = self._assemble_report(
                    request, phase1_results, framework_results, synthesis_results
                )
                
                # Store in semantic cache
                await semantic_cache_store(
                    request.company,
                    request.frameworks,
                    cache_key_str,
                    report
                )
                
                return report
            
            except Exception as e:
                raise Exception(f"Orchestration failed: {str(e)}")
    
    async def _safe_execute_agent(self, agent: Any, input_data: Dict[str, Any], agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Execute agent with error handling and logging
        
        Args:
            agent: Agent instance to execute
            input_data: Input data for the agent
            agent_name: Name of the agent for logging
        
        Returns:
            Agent result or None if execution failed
        """
        try:
            result = await agent.execute(input_data)
            logger.info(f"{agent_name} completed successfully")
            return result
        except asyncio.TimeoutError as e:
            logger.error(f"{agent_name} timed out: {e}")
            return None
        except Exception as e:
            logger.error(f"{agent_name} failed: {e}", exc_info=True)
            return None
    
    async def _execute_parallel_phase(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Execute Phase 1: Parallel data gathering with graceful degradation
        
        Args:
            request: Analysis request with company and industry information
        
        Returns:
            Dictionary with results and error tracking containing:
            - research: Research agent results or None
            - market: Market agent results or None
            - financial: Financial agent results or None
            - errors: Dict of error messages for failed agents
            
        Raises:
            Exception: If all three agents fail to produce results
        """
        input_data = {
            "company": request.company,
            "industry": request.industry,
            "ticker": self._guess_ticker(request.company)
        }
        
        # Run agents in parallel with individual error handling
        research_task = self._safe_execute_agent(
            self.research_agent, input_data, "research_agent"
        )
        market_task = self._safe_execute_agent(
            self.market_agent, input_data, "market_agent"
        )
        financial_task = self._safe_execute_agent(
            self.financial_agent, input_data, "financial_agent"
        )
        
        research, market, financial = await asyncio.gather(
            research_task,
            market_task,
            financial_task,
            return_exceptions=False  # Errors already handled in _safe_execute_agent
        )
        
        # Track which agents succeeded/failed
        errors = {}
        if research is None:
            errors["research"] = "Research agent failed or timed out"
        if market is None:
            errors["market"] = "Market agent failed or timed out"
        if financial is None:
            errors["financial"] = "Financial agent failed or timed out"
        
        # Log warnings if any agents failed
        if errors:
            logger.warning(
                f"Phase 1 completed with errors: {errors}. "
                f"Continuing with partial results."
            )
        
        # Ensure at least one agent succeeded
        if research is None and market is None and financial is None:
            raise Exception(
                "All Phase 1 agents failed. Cannot proceed with analysis. "
                "Please check API keys and network connectivity."
            )
        
        return {
            "research": research,
            "market": market,
            "financial": financial,
            "errors": errors
        }
    
    async def _execute_framework_phase(self, request: AnalysisRequest, phase1_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Phase 2: Framework analysis
        
        Continues even if some Phase 1 data is missing
        
        Args:
            request: Analysis request with framework selection
            phase1_results: Results from Phase 1 data gathering
            
        Returns:
            Dictionary containing framework analysis results
        """
        input_data = {
            "company": request.company,
            "industry": request.industry,
            "frameworks": request.frameworks,
            "research": phase1_results.get("research"),
            "market": phase1_results.get("market"),
            "financial": phase1_results.get("financial")
        }
        
        # Note missing data in prompt if needed
        missing_data = []
        if input_data.get("research") is None:
            missing_data.append("research")
        if input_data.get("market") is None:
            missing_data.append("market")
        if input_data.get("financial") is None:
            missing_data.append("financial")
        
        if missing_data:
            logger.info(f"Framework analysis proceeding with missing data: {missing_data}")
        
        try:
            framework_results = await self.framework_agent.execute(input_data)
            return {
                "frameworks": framework_results
            }
        except Exception as e:
            logger.error(f"Framework analysis failed: {e}", exc_info=True)
            # Return empty framework analysis rather than failing completely
            from consultantos.models import FrameworkAnalysis
            return {
                "frameworks": FrameworkAnalysis(),
                "errors": {"framework": str(e)}
            }
    
    async def _execute_synthesis_phase(self, request: AnalysisRequest, 
                                       phase1_results: Dict[str, Any],
                                       phase2_results: Dict[str, Any]) -> ExecutiveSummary:
        """
        Execute Phase 3: Synthesis
        
        Args:
            request: Original analysis request
            phase1_results: Results from parallel data gathering phase
            phase2_results: Results from framework analysis phase
            
        Returns:
            Executive summary synthesizing all analysis results
        """
        input_data = {
            "company": request.company,
            "industry": request.industry,
            "research": phase1_results.get("research"),
            "market": phase1_results.get("market"),
            "financial": phase1_results.get("financial"),
            "frameworks": phase2_results.get("frameworks")
        }
        
        synthesis = await self.synthesis_agent.execute(input_data)
        return synthesis
    
    def _assemble_report(self, request: AnalysisRequest, phase1_results: Dict[str, Any],
                        phase2_results: Dict[str, Any], synthesis: ExecutiveSummary) -> StrategicReport:
        """
        Assemble final strategic report
        
        Includes metadata about partial results if any agents failed
        
        Args:
            request: Original analysis request
            phase1_results: Results from Phase 1
            phase2_results: Results from Phase 2
            synthesis: Executive summary from Phase 3
            
        Returns:
            Complete strategic report with all components and metadata
        """
        # Get framework analysis
        framework_analysis = phase2_results.get("frameworks")
        
        # Generate recommendations from synthesis
        recommendations = synthesis.next_steps[:3] if synthesis.next_steps else []
        
        # Collect error information
        phase1_errors = phase1_results.get("errors", {})
        phase2_errors = phase2_results.get("errors", {})
        all_errors = {**phase1_errors, **phase2_errors}
        
        # Adjust confidence score if there were errors
        confidence_score = synthesis.confidence_score
        if all_errors:
            # Reduce confidence by 10% per failed agent (minimum 0.3)
            error_penalty = len(all_errors) * 0.1
            confidence_score = max(0.3, confidence_score - error_penalty)
            logger.warning(
                f"Report generated with errors. "
                f"Confidence adjusted from {synthesis.confidence_score:.2f} to {confidence_score:.2f}"
            )
        
        # Update synthesis confidence if adjusted
        synthesis.confidence_score = confidence_score
        
        # Create report metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "frameworks_requested": request.frameworks,
            "depth": request.depth,
            "partial_results": len(all_errors) > 0,
            "errors": all_errors if all_errors else None
        }
        
        # Create report
        report = StrategicReport(
            executive_summary=synthesis,
            company_research=phase1_results.get("research"),
            market_trends=phase1_results.get("market"),
            financial_snapshot=phase1_results.get("financial"),
            framework_analysis=framework_analysis,
            recommendations=recommendations,
            metadata=metadata
        )
        
        return report
    
    def _guess_ticker(self, company: str) -> str:
        """
        Resolve ticker symbol for company
        
        Uses enhanced ticker resolution, falls back to simple guess
        
        Args:
            company: Company name to resolve ticker for
            
        Returns:
            Ticker symbol string (may be a guess if resolution fails)
        """
        from consultantos.tools.ticker_resolver import resolve_ticker, guess_ticker
        
        # Try to resolve ticker properly
        ticker = resolve_ticker(company)
        if ticker:
            return ticker
        
        # Fallback to guess
        return guess_ticker(company)