"""
Progress tracking for analysis orchestration
"""
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProgressUpdate:
    """Progress update message"""
    phase: str
    phase_name: str
    phase_num: int
    total_phases: int
    progress: int  # 0-100
    current_agents: List[str] = field(default_factory=list)
    completed_agents: List[str] = field(default_factory=list)
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    estimated_seconds_remaining: Optional[int] = None


class ProgressCallback:
    """Callback interface for progress updates"""
    
    async def on_phase_start(
        self, 
        phase: str, 
        phase_name: str,
        phase_num: int, 
        total_phases: int
    ):
        """Called when a phase starts"""
        pass
    
    async def on_agent_start(self, agent_name: str, phase: str):
        """Called when an agent starts"""
        pass
    
    async def on_agent_complete(self, agent_name: str, phase: str):
        """Called when an agent completes"""
        pass
    
    async def on_phase_complete(self, phase: str, phase_num: int):
        """Called when a phase completes"""
        pass


class ProgressTracker:
    """Tracks and calculates analysis progress"""
    
    # Phase progress allocation (percentage of total)
    PHASE_PROGRESS = {
        "phase_1": {"start": 0, "end": 40, "name": "Data Gathering"},
        "phase_2": {"start": 40, "end": 70, "name": "Framework Analysis"},
        "phase_3": {"start": 70, "end": 100, "name": "Synthesis"},
    }
    
    # Estimated time per phase (seconds)
    PHASE_ESTIMATED_TIME = {
        "phase_1": 60,  # Parallel agents, max 60s
        "phase_2": 60,  # Framework analysis
        "phase_3": 90,  # Synthesis (increased from 60s)
    }
    
    def __init__(self, report_id: str, callback: Optional[ProgressCallback] = None):
        self.report_id = report_id
        self.callback = callback
        self.current_phase: Optional[str] = None
        self.current_phase_num: int = 0
        self.total_phases: int = 3
        self.active_agents: List[str] = []
        self.completed_agents: List[str] = []
        self.phase_start_time: Optional[datetime] = None
        self.analysis_start_time = datetime.utcnow()
        
    def calculate_progress(self) -> int:
        """Calculate overall progress percentage"""
        if not self.current_phase:
            return 0
        
        phase_info = self.PHASE_PROGRESS.get(self.current_phase)
        if not phase_info:
            return 0
        
        base_progress = phase_info["start"]
        phase_range = phase_info["end"] - phase_info["start"]
        
        # For phase 1 (parallel), calculate based on completed agents
        if self.current_phase == "phase_1":
            total_agents = 3  # Research, Market, Financial
            completed = len(self.completed_agents)
            agent_progress = (completed / total_agents) * phase_range
        else:
            # For sequential phases, assume 50% complete if in progress
            # This is a rough estimate - could be improved with actual timing
            agent_progress = phase_range * 0.5 if self.active_agents else phase_range
        
        return int(base_progress + agent_progress)
    
    def get_estimated_remaining(self) -> Optional[int]:
        """Get estimated seconds remaining for current phase"""
        if not self.current_phase or not self.phase_start_time:
            return None
        
        estimated = self.PHASE_ESTIMATED_TIME.get(self.current_phase, 60)
        elapsed = (datetime.utcnow() - self.phase_start_time).total_seconds()
        remaining = max(0, estimated - elapsed)
        return int(remaining)
    
    async def start_phase(
        self, 
        phase: str, 
        phase_num: int, 
        total_phases: int = 3
    ):
        """Mark a phase as started"""
        self.current_phase = phase
        self.current_phase_num = phase_num
        self.total_phases = total_phases
        self.phase_start_time = datetime.utcnow()
        self.active_agents = []
        self.completed_agents = []
        
        phase_name = self.PHASE_PROGRESS.get(phase, {}).get("name", phase)
        
        if self.callback:
            await self.callback.on_phase_start(phase, phase_name, phase_num, total_phases)
        
        logger.info(f"Progress: Started {phase_name} (Phase {phase_num}/{total_phases})")
    
    async def start_agent(self, agent_name: str):
        """Mark an agent as started"""
        if agent_name not in self.active_agents:
            self.active_agents.append(agent_name)
        
        if self.callback:
            await self.callback.on_agent_start(agent_name, self.current_phase or "")
        
        logger.debug(f"Progress: Started agent {agent_name} in {self.current_phase}")
    
    async def complete_agent(self, agent_name: str):
        """Mark an agent as completed"""
        if agent_name in self.active_agents:
            self.active_agents.remove(agent_name)
        if agent_name not in self.completed_agents:
            self.completed_agents.append(agent_name)
        
        if self.callback:
            await self.callback.on_agent_complete(agent_name, self.current_phase or "")
        
        logger.debug(f"Progress: Completed agent {agent_name} in {self.current_phase}")
    
    async def complete_phase(self, phase: str):
        """Mark a phase as completed"""
        # Move all active agents to completed
        self.completed_agents.extend(self.active_agents)
        self.active_agents = []
        
        if self.callback:
            await self.callback.on_phase_complete(phase, self.current_phase_num)
        
        phase_name = self.PHASE_PROGRESS.get(phase, {}).get("name", phase)
        logger.info(f"Progress: Completed {phase_name} (Phase {self.current_phase_num}/{self.total_phases})")
    
    def get_update(self) -> ProgressUpdate:
        """Get current progress update"""
        phase_name = ""
        if self.current_phase:
            phase_name = self.PHASE_PROGRESS.get(self.current_phase, {}).get("name", self.current_phase)
        
        # Build message
        if self.current_phase == "phase_1":
            if self.active_agents:
                message = f"Gathering data: {', '.join(self.active_agents)}"
            else:
                message = "Data gathering complete"
        elif self.current_phase == "phase_2":
            message = "Analyzing business frameworks..."
        elif self.current_phase == "phase_3":
            message = "Synthesizing executive summary..."
        else:
            message = "Processing..."
        
        return ProgressUpdate(
            phase=self.current_phase or "",
            phase_name=phase_name,
            phase_num=self.current_phase_num,
            total_phases=self.total_phases,
            progress=self.calculate_progress(),
            current_agents=self.active_agents.copy(),
            completed_agents=self.completed_agents.copy(),
            message=message,
            estimated_seconds_remaining=self.get_estimated_remaining()
        )

