"""
Template Agent for managing framework templates and custom frameworks
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.templates import (
    FrameworkTemplate,
    TemplateLibrary,
    CreateTemplateRequest,
    UpdateTemplateRequest,
    TemplateCategory,
    TemplateVisibility
)
import logging
from datetime import datetime
import secrets
import threading

logger = logging.getLogger(__name__)

# In-memory template store (in production, use database)
_templates: dict[str, FrameworkTemplate] = {}
_templates_lock = threading.Lock()  # Thread-safety lock for _templates


class TemplateListRequest(BaseModel):
    category: Optional[str] = Field(None, description="Filter by template category.")
    framework_type: Optional[str] = Field(None, description="Filter by framework type.")
    visibility: Optional[str] = Field("public", description="Filter by visibility (public, private, shared).")
    page: int = Field(1, ge=1, description="Page number.")
    page_size: int = Field(20, ge=1, le=100, description="Page size.")


class TemplateCreateRequest(BaseModel):
    name: str = Field(..., description="Template name.")
    category: str = Field(..., description="Template category.")
    description: Optional[str] = Field(None, description="Template description.")
    framework_type: str = Field(..., description="Framework type.")
    prompt_template: str = Field(..., description="Prompt template with placeholders.")
    structure: Dict[str, Any] = Field(..., description="Expected output structure.")
    examples: Optional[List[Dict[str, Any]]] = Field(None, description="Example outputs.")
    visibility: str = Field("private", description="Template visibility.")
    tags: Optional[List[str]] = Field(None, description="Template tags.")
    industry: Optional[str] = Field(None, description="Industry filter.")
    region: Optional[str] = Field(None, description="Region filter.")
    user_id: str = Field(..., description="User ID creating the template.")


class TemplateResponse(BaseModel):
    templates: List[Dict[str, Any]] = Field(default_factory=list, description="List of templates.")
    total: int = Field(0, description="Total number of templates.")
    page: int = Field(1, description="Current page.")
    page_size: int = Field(20, description="Page size.")
    template: Optional[Dict[str, Any]] = Field(None, description="Single template (for get/create/update).")
    message: Optional[str] = Field(None, description="Confirmation message for actions.")


class TemplateAgent(BaseAgent):
    """Agent for managing framework templates and custom frameworks"""

    def __init__(self, timeout: int = 60):
        super().__init__(name="TemplateAgent", timeout=timeout)

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action_type = input_data.get("action_type", "list")

        if action_type == "list":
            request = TemplateListRequest(**input_data)
            library = await self._list_templates(
                category=request.category,
                framework_type=request.framework_type,
                visibility=request.visibility,
                page=request.page,
                page_size=request.page_size
            )
            return {
                "success": True,
                "data": TemplateResponse(
                    templates=[t.model_dump() for t in library.templates],
                    total=library.total,
                    page=library.page,
                    page_size=library.page_size
                ).model_dump(),
                "error": None
            }

        elif action_type == "get":
            template_id = input_data.get("template_id")
            if not template_id:
                raise ValueError("template_id is required for get action.")
            template = await self._get_template(template_id)
            return {
                "success": True,
                "data": TemplateResponse(
                    template=template.model_dump() if template else None
                ).model_dump(),
                "error": None
            }

        elif action_type == "create":
            request = TemplateCreateRequest(**input_data)
            template = await self._create_template(request)
            return {
                "success": True,
                "data": TemplateResponse(
                    template=template.model_dump(),
                    message=f"Template '{template.name}' created successfully."
                ).model_dump(),
                "error": None
            }

        elif action_type == "update":
            template_id = input_data.get("template_id")
            if not template_id:
                raise ValueError("template_id is required for update action.")
            update_data = {k: v for k, v in input_data.items() if k != "action_type" and k != "template_id"}
            template = await self._update_template(template_id, update_data)
            return {
                "success": True,
                "data": TemplateResponse(
                    template=template.model_dump() if template else None,
                    message=f"Template updated successfully."
                ).model_dump(),
                "error": None
            }

        elif action_type == "delete":
            template_id = input_data.get("template_id")
            user_id = input_data.get("user_id")
            if not template_id or not user_id:
                raise ValueError("template_id and user_id are required for delete action.")
            await self._delete_template(template_id, user_id)
            return {
                "success": True,
                "data": TemplateResponse(
                    message=f"Template deleted successfully."
                ).model_dump(),
                "error": None
            }

        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    async def _list_templates(
        self,
        category: Optional[str],
        framework_type: Optional[str],
        visibility: Optional[str],
        page: int,
        page_size: int
    ) -> TemplateLibrary:
        """List available templates"""
        try:
            with _templates_lock:
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
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            return TemplateLibrary(
                templates=[],
                total=0,
                page=page,
                page_size=page_size
            )

    async def _get_template(self, template_id: str) -> Optional[FrameworkTemplate]:
        """Get a specific template"""
        with _templates_lock:
            return _templates.get(template_id)

    async def _create_template(self, request: TemplateCreateRequest) -> FrameworkTemplate:
        """Create a new template"""
        try:
            template_id = f"template_{secrets.token_urlsafe(16)}"

            template = FrameworkTemplate(
                template_id=template_id,
                name=request.name,
                category=TemplateCategory(request.category),
                description=request.description,
                framework_type=request.framework_type,
                prompt_template=request.prompt_template,
                structure=request.structure,
                examples=request.examples or [],
                created_by=request.user_id,
                visibility=TemplateVisibility(request.visibility),
                tags=request.tags or [],
                industry=request.industry,
                region=request.region
            )

            with _templates_lock:
                _templates[template_id] = template
            return template
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise

    async def _update_template(
        self,
        template_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[FrameworkTemplate]:
        """Update a template"""
        try:
            with _templates_lock:
                template = _templates.get(template_id)
                if not template:
                    return None

                # Update fields
                if "name" in update_data:
                    template.name = update_data["name"]
                if "description" in update_data:
                    template.description = update_data["description"]
                if "prompt_template" in update_data:
                    template.prompt_template = update_data["prompt_template"]
                if "structure" in update_data:
                    template.structure = update_data["structure"]
                if "examples" in update_data:
                    template.examples = update_data["examples"]
                if "visibility" in update_data:
                    template.visibility = TemplateVisibility(update_data["visibility"])
                if "tags" in update_data:
                    template.tags = update_data["tags"]
                if "industry" in update_data:
                    template.industry = update_data["industry"]
                if "region" in update_data:
                    template.region = update_data["region"]

                template.updated_at = datetime.now().isoformat()
                _templates[template_id] = template

            return template
        except Exception as e:
            logger.error(f"Failed to update template: {e}")
            raise

    async def _delete_template(self, template_id: str, user_id: str):
        """Delete a template (only if user is owner)"""
        try:
            with _templates_lock:
                template = _templates.get(template_id)
                if not template:
                    raise ValueError(f"Template {template_id} not found")

                if template.created_by != user_id:
                    raise ValueError("Only template owner can delete template")

                del _templates[template_id]
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            raise

