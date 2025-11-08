"""
Template library API endpoints (v0.4.0)
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Security
from consultantos.models.templates import (
    FrameworkTemplate,
    TemplateLibrary,
    CreateTemplateRequest,
    UpdateTemplateRequest
)
from consultantos.auth import verify_api_key
from datetime import datetime, timezone
import secrets

router = APIRouter(prefix="/templates", tags=["templates"])

# In-memory template store (in production, use database)
_templates: dict[str, FrameworkTemplate] = {}


@router.get("", response_model=TemplateLibrary)
async def list_templates(
    category: Optional[str] = None,
    framework_type: Optional[str] = None,
    visibility: Optional[str] = "public",
    page: int = 1,
    page_size: int = 20
):
    """List available templates"""
    filtered = list(_templates.values())
    
    if category:
        filtered = [t for t in filtered if t.category.value == category]
    if framework_type:
        filtered = [t for t in filtered if t.framework_type == framework_type]
    if visibility:
        filtered = [t for t in filtered if t.visibility.value == visibility]
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    return TemplateLibrary(
        templates=paginated,
        total=len(filtered),
        page=page,
        page_size=page_size
    )


@router.get("/{template_id}", response_model=FrameworkTemplate)
async def get_template(template_id: str):
    """Get a specific template"""
    if template_id not in _templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return _templates[template_id]


@router.post("", response_model=FrameworkTemplate, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: CreateTemplateRequest,
    user_info: dict = Security(verify_api_key)
):
    """Create a new template"""
    template_id = f"template_{secrets.token_urlsafe(16)}"
    
    template = FrameworkTemplate(
        template_id=template_id,
        name=request.name,
        category=request.category,
        description=request.description,
        framework_type=request.framework_type,
        prompt_template=request.prompt_template,
        structure=request.structure,
        examples=request.examples or [],
        created_by=user_info["user_id"],
        visibility=request.visibility,
        tags=request.tags or [],
        industry=request.industry,
        region=request.region
    )
    
    _templates[template_id] = template
    return template


@router.put("/{template_id}", response_model=FrameworkTemplate)
async def update_template(
    template_id: str,
    request: UpdateTemplateRequest,
    user_info: dict = Security(verify_api_key)
):
    """Update a template (only if owner)"""
    if template_id not in _templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    template = _templates[template_id]
    
    # Check ownership
    if template.created_by != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own templates"
        )
    
    # Update fields (Pydantic v2)
    updates = request.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(template, key, value)
    
    template.updated_at = datetime.now(timezone.utc).isoformat()
    _templates[template_id] = template
    
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Delete a template (only if owner)"""
    if template_id not in _templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    template = _templates[template_id]
    
    if template.created_by != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own templates"
        )
    
    del _templates[template_id]
    return {"message": "Template deleted successfully"}

