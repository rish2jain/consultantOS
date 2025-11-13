"""
Progress tracking endpoints for analysis
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Optional
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["progress"])

# In-memory progress store (in production, use Redis or similar)
_progress_store: Dict[str, Dict] = {}


@router.get("/{report_id}/progress")
async def stream_progress(report_id: str, request: Request):
    """
    Stream progress updates for an analysis via Server-Sent Events (SSE)
    
    Usage:
        Connect to this endpoint to receive real-time progress updates
        while an analysis is running.
    
    Example:
        ```javascript
        const eventSource = new EventSource('/analyze/{report_id}/progress');
        eventSource.onmessage = (event) => {
            const update = JSON.parse(event.data);
            console.log(`Progress: ${update.progress}% - ${update.message}`);
        };
        ```
    """
    async def event_generator():
        """Generate SSE events"""
        last_progress = -1
        consecutive_no_change = 0
        
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
            
            # Get current progress
            progress_data = _progress_store.get(report_id)
            
            if not progress_data:
                # Send initial message
                yield f"data: {json.dumps({'status': 'not_found', 'message': 'Analysis not found or not started'})}\n\n"
                await asyncio.sleep(2)
                continue
            
            # Check if analysis is complete
            if progress_data.get("status") == "completed":
                yield f"data: {json.dumps({'status': 'completed', 'progress': 100, 'message': 'Analysis complete'})}\n\n"
                break
            
            if progress_data.get("status") == "failed":
                yield f"data: {json.dumps({'status': 'failed', 'error': progress_data.get('error', 'Unknown error')})}\n\n"
                break
            
            # Get current progress
            current_progress = progress_data.get("progress", 0)
            
            # Send update if progress changed or every 5 seconds
            if current_progress != last_progress or consecutive_no_change >= 5:
                update = {
                    "status": "running",
                    "phase": progress_data.get("phase", ""),
                    "phase_name": progress_data.get("phase_name", ""),
                    "phase_num": progress_data.get("phase_num", 0),
                    "total_phases": progress_data.get("total_phases", 3),
                    "progress": current_progress,
                    "current_agents": progress_data.get("current_agents", []),
                    "completed_agents": progress_data.get("completed_agents", []),
                    "message": progress_data.get("message", "Processing..."),
                    "estimated_seconds_remaining": progress_data.get("estimated_seconds_remaining"),
                    "timestamp": progress_data.get("timestamp", datetime.utcnow().isoformat())
                }
                
                yield f"data: {json.dumps(update)}\n\n"
                last_progress = current_progress
                consecutive_no_change = 0
            else:
                consecutive_no_change += 1
            
            await asyncio.sleep(1)  # Poll every second
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


def update_progress(report_id: str, progress_data: Dict):
    """Update progress for a report"""
    _progress_store[report_id] = {
        **progress_data,
        "timestamp": datetime.utcnow().isoformat(),
        "status": progress_data.get("status", "running")
    }


def mark_complete(report_id: str):
    """Mark analysis as complete"""
    if report_id in _progress_store:
        _progress_store[report_id]["status"] = "completed"
        _progress_store[report_id]["progress"] = 100


def mark_failed(report_id: str, error: str):
    """Mark analysis as failed"""
    if report_id in _progress_store:
        _progress_store[report_id]["status"] = "failed"
        _progress_store[report_id]["error"] = error

