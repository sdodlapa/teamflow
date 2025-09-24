"""
Template Builder API endpoints for domain configuration management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.template import (
    TemplateConfigCreate,
    TemplateConfigResponse, 
    TemplateConfigUpdate,
    ValidationRequest,
    ValidationResponse,
    GenerationRequest,
    GenerationResponse,
    TemplateListResponse
)
from app.services.template_builder import (
    template_service,
    validation_service,
    code_generation_service
)

router = APIRouter()

@router.post("/validate", response_model=ValidationResponse)
async def validate_template_config(
    validation_request: ValidationRequest,
    current_user: User = Depends(get_current_user)
) -> ValidationResponse:
    """
    Validate a template configuration without saving it
    """
    try:
        result = await validation_service.validate_domain_config(validation_request.config)
        return ValidationResponse(
            is_valid=result.is_valid,
            errors=result.errors,
            warnings=result.warnings
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )

@router.post("/generate", response_model=GenerationResponse)
async def generate_template_code(
    generation_request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> GenerationResponse:
    """
    Generate code from a template configuration
    """
    try:
        # First validate the configuration
        validation_result = await validation_service.validate_domain_config(generation_request.domain_config)
        if not validation_result.is_valid:
            return GenerationResponse(
                success=False,
                files_generated=[],
                errors=[f"Configuration validation failed: {error.message}" for error in validation_result.errors]
            )

        # Start code generation in background
        task_id = await code_generation_service.start_generation(
            config=generation_request.domain_config,
            user_id=current_user.id,
            generate_backend=generation_request.generate_backend,
            generate_frontend=generation_request.generate_frontend,
            target_directory=generation_request.target_directory
        )

        return GenerationResponse(
            success=True,
            files_generated=[],
            task_id=task_id,
            message="Code generation started successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )

@router.get("/generate/{task_id}/status")
async def get_generation_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a code generation task
    """
    try:
        status_info = await code_generation_service.get_generation_status(task_id, current_user.id)
        return status_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation task not found: {str(e)}"
        )

@router.post("", response_model=TemplateConfigResponse)
async def create_template_config(
    template_data: TemplateConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TemplateConfigResponse:
    """
    Create and save a new template configuration
    """
    try:
        # Validate the configuration first
        validation_result = await validation_service.validate_domain_config(template_data.config)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid configuration: {[error.message for error in validation_result.errors]}"
            )

        template_config = await template_service.create_template(
            db=db,
            template_data=template_data,
            user_id=current_user.id
        )
        return template_config
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this name already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )

@router.get("", response_model=TemplateListResponse)
async def list_templates(
    skip: int = 0,
    limit: int = 20,
    domain_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TemplateListResponse:
    """
    List available template configurations
    """
    try:
        templates = await template_service.list_templates(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            domain_type=domain_type,
            search=search
        )
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )

@router.get("/{template_id}", response_model=TemplateConfigResponse)
async def get_template_config(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TemplateConfigResponse:
    """
    Get a specific template configuration by ID
    """
    try:
        template_config = await template_service.get_template_by_id(
            db=db,
            template_id=template_id,
            user_id=current_user.id
        )
        if not template_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return template_config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )

@router.put("/{template_id}", response_model=TemplateConfigResponse)
async def update_template_config(
    template_id: str,
    template_data: TemplateConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TemplateConfigResponse:
    """
    Update an existing template configuration
    """
    try:
        # Validate the updated configuration
        if template_data.config:
            validation_result = await validation_service.validate_domain_config(template_data.config)
            if not validation_result.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid configuration: {[error.message for error in validation_result.errors]}"
                )

        template_config = await template_service.update_template(
            db=db,
            template_id=template_id,
            template_data=template_data,
            user_id=current_user.id
        )
        if not template_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return template_config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )

@router.delete("/{template_id}")
async def delete_template_config(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a template configuration
    """
    try:
        success = await template_service.delete_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return {"message": "Template deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}"
        )

@router.get("/check-name/{name}")
async def check_template_name_availability(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a template name is available for use
    """
    try:
        available = await template_service.is_name_available(
            db=db,
            name=name,
            user_id=current_user.id
        )
        return {"available": available}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check name availability: {str(e)}"
        )

@router.post("/{template_id}/clone", response_model=TemplateConfigResponse)
async def clone_template_config(
    template_id: str,
    new_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TemplateConfigResponse:
    """
    Clone an existing template configuration with a new name
    """
    try:
        template_config = await template_service.clone_template(
            db=db,
            template_id=template_id,
            new_name=new_name,
            user_id=current_user.id
        )
        if not template_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return template_config
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this name already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clone template: {str(e)}"
        )

@router.get("/{template_id}/preview")
async def preview_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a preview of what the template will produce
    """
    try:
        template_config = await template_service.get_template_by_id(
            db=db,
            template_id=template_id,
            user_id=current_user.id
        )
        if not template_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        preview = await code_generation_service.generate_preview(template_config.config)
        return preview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )

@router.post("/import")
async def import_template_config(
    file_content: dict,  # JSON content of template file
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TemplateConfigResponse:
    """
    Import a template configuration from a file
    """
    try:
        template_config = await template_service.import_template(
            db=db,
            file_content=file_content,
            user_id=current_user.id
        )
        return template_config
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid template file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import template: {str(e)}"
        )

@router.get("/{template_id}/export")
async def export_template_config(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export a template configuration as a downloadable file
    """
    try:
        template_config = await template_service.get_template_by_id(
            db=db,
            template_id=template_id,
            user_id=current_user.id
        )
        if not template_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        export_data = await template_service.export_template(template_config)
        
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename={template_config.name}.json"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export template: {str(e)}"
        )