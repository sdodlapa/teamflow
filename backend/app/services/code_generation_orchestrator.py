"""
Code Generation Orchestrator Service
For Section 3: Code Generation Engine - Phase 3E

This service coordinates all code generators to create complete full-stack applications
from domain configurations. It manages the generation workflow, file organization,
and output structure.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

from app.core.domain_config import DomainConfig, EntityConfig
from app.core.template_engine import TemplateEngine
from app.services.model_generator import ModelGenerator
from app.services.frontend_generator import FrontendGenerator

logger = logging.getLogger(__name__)


class CodeGenerationError(Exception):
    """Exception raised when code generation fails."""
    pass


@dataclass
class GenerationResult:
    """Result of a code generation operation."""
    success: bool
    entity_name: str
    component_type: str  # 'model', 'schema', 'routes', 'service', 'frontend'
    file_path: Optional[str] = None
    content_length: int = 0
    error_message: Optional[str] = None
    generation_time_seconds: Optional[float] = None


@dataclass
class GenerationSummary:
    """Summary of entire generation operation."""
    domain_name: str
    total_entities: int
    successful_generations: int
    failed_generations: int
    total_files_created: int
    total_content_length: int
    generation_time_seconds: float
    output_directory: str
    results: List[GenerationResult]
    errors: List[str]


class CodeGenerationOrchestrator:
    """
    Main orchestrator for code generation.
    
    Coordinates ModelGenerator and FrontendGenerator to create complete
    full-stack applications from domain configurations.
    """
    
    def __init__(
        self, 
        template_engine: Optional[TemplateEngine] = None,
        output_base_path: Optional[str] = None
    ):
        """
        Initialize the orchestrator.
        
        Args:
            template_engine: Optional template engine instance
            output_base_path: Base path for generated code output
        """
        self.template_engine = template_engine or TemplateEngine()
        self.output_base_path = Path(output_base_path or "generated")
        self.model_generator = ModelGenerator(self.template_engine)
        self.frontend_generator = FrontendGenerator(self.template_engine)
        
        # Ensure output directory exists
        self.output_base_path.mkdir(parents=True, exist_ok=True)
    
    def generate_full_application(
        self, 
        domain_config: DomainConfig,
        include_backend: bool = True,
        include_frontend: bool = True,
        entities: Optional[List[str]] = None
    ) -> GenerationSummary:
        """
        Generate a complete full-stack application from domain configuration.
        
        Args:
            domain_config: Domain configuration to generate from
            include_backend: Whether to generate backend components
            include_frontend: Whether to generate frontend components  
            entities: Optional list of specific entities to generate (default: all)
            
        Returns:
            GenerationSummary with results and statistics
            
        Raises:
            CodeGenerationError: If generation fails critically
        """
        start_time = datetime.now()
        logger.info(f"Starting full application generation for domain: {domain_config.name}")
        
        # Create domain-specific output directory
        domain_output_path = self.output_base_path / domain_config.name.lower().replace(' ', '_')
        domain_output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize results tracking
        results: List[GenerationResult] = []
        errors: List[str] = []
        total_files_created = 0
        total_content_length = 0
        
        # Determine which entities to generate
        target_entities = entities or [entity.name for entity in domain_config.entities]
        
        # Generate for each entity
        for entity_name in target_entities:
            entity_config = domain_config.get_entity(entity_name)
            if not entity_config:
                error_msg = f"Entity '{entity_name}' not found in domain configuration"
                errors.append(error_msg)
                logger.error(error_msg)
                continue
            
            logger.info(f"Generating components for entity: {entity_name}")
            
            try:
                # Generate backend components
                if include_backend:
                    backend_results = self._generate_backend_for_entity(
                        domain_config, entity_config, domain_output_path
                    )
                    results.extend(backend_results)
                    
                    # Update statistics
                    successful_backend = [r for r in backend_results if r.success]
                    total_files_created += len(successful_backend)
                    total_content_length += sum(r.content_length for r in successful_backend)
                
                # Generate frontend components
                if include_frontend:
                    frontend_results = self._generate_frontend_for_entity(
                        domain_config, entity_config, domain_output_path
                    )
                    results.extend(frontend_results)
                    
                    # Update statistics
                    successful_frontend = [r for r in frontend_results if r.success]
                    total_files_created += len(successful_frontend)
                    total_content_length += sum(r.content_length for r in successful_frontend)
                    
            except Exception as e:
                error_msg = f"Failed to generate components for entity '{entity_name}': {e}"
                errors.append(error_msg)
                logger.error(error_msg, exc_info=True)
        
        # Generate application structure files
        try:
            structure_results = self._generate_application_structure(
                domain_config, domain_output_path, include_backend, include_frontend
            )
            results.extend(structure_results)
            
            successful_structure = [r for r in structure_results if r.success]
            total_files_created += len(successful_structure)
            total_content_length += sum(r.content_length for r in successful_structure)
            
        except Exception as e:
            error_msg = f"Failed to generate application structure: {e}"
            errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
        
        # Create generation summary
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        successful_count = sum(1 for r in results if r.success)
        failed_count = sum(1 for r in results if not r.success)
        
        summary = GenerationSummary(
            domain_name=domain_config.name,
            total_entities=len(target_entities),
            successful_generations=successful_count,
            failed_generations=failed_count,
            total_files_created=total_files_created,
            total_content_length=total_content_length,
            generation_time_seconds=generation_time,
            output_directory=str(domain_output_path),
            results=results,
            errors=errors
        )
        
        # Save generation report
        self._save_generation_report(summary, domain_output_path)
        
        logger.info(f"Application generation completed in {generation_time:.2f}s. "
                   f"Success: {successful_count}, Failed: {failed_count}, "
                   f"Files: {total_files_created}, Size: {total_content_length} chars")
        
        return summary
    
    def _generate_backend_for_entity(
        self, 
        domain_config: DomainConfig,
        entity_config: EntityConfig,
        output_path: Path
    ) -> List[GenerationResult]:
        """Generate all backend components for an entity."""
        results = []
        backend_path = output_path / "backend"
        
        # Backend component types and their output subdirectories
        backend_components = [
            ("model", "models"),
            ("schema", "schemas"),
            ("routes", "routes"),
            ("service", "services")
        ]
        
        for component_type, subdirectory in backend_components:
            start_time = datetime.now()
            
            try:
                # Generate component
                if component_type == "model":
                    content = self.model_generator.generate_model(domain_config, entity_config)
                elif component_type == "schema":
                    content = self.model_generator.generate_schema(domain_config, entity_config)
                elif component_type == "routes":
                    content = self.model_generator.generate_routes(domain_config, entity_config)
                elif component_type == "service":
                    content = self.model_generator.generate_service(domain_config, entity_config)
                
                # Write to file
                component_dir = backend_path / subdirectory
                component_dir.mkdir(parents=True, exist_ok=True)
                
                filename = f"{entity_config.name.lower()}.py"
                file_path = component_dir / filename
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                # Record success
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                results.append(GenerationResult(
                    success=True,
                    entity_name=entity_config.name,
                    component_type=f"backend_{component_type}",
                    file_path=str(file_path),
                    content_length=len(content),
                    generation_time_seconds=generation_time
                ))
                
                logger.debug(f"Generated {component_type} for {entity_config.name}: "
                           f"{len(content)} chars -> {file_path}")
                
            except Exception as e:
                # Record failure
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                results.append(GenerationResult(
                    success=False,
                    entity_name=entity_config.name,
                    component_type=f"backend_{component_type}",
                    error_message=str(e),
                    generation_time_seconds=generation_time
                ))
                
                logger.error(f"Failed to generate {component_type} for {entity_config.name}: {e}")
        
        return results
    
    def _generate_frontend_for_entity(
        self, 
        domain_config: DomainConfig,
        entity_config: EntityConfig,
        output_path: Path
    ) -> List[GenerationResult]:
        """Generate all frontend components for an entity."""
        results = []
        frontend_path = output_path / "frontend" / "src"
        
        # Frontend component types and their configurations
        frontend_components = [
            ("types", "types", "ts"),
            ("form", "components", "tsx"),
            ("list", "components", "tsx"),
            ("service", "services", "ts")
        ]
        
        for component_type, subdirectory, extension in frontend_components:
            start_time = datetime.now()
            
            try:
                # Generate component
                if component_type == "types":
                    content = self.frontend_generator.generate_types(domain_config, entity_config)
                elif component_type == "form":
                    content = self.frontend_generator.generate_form_component(domain_config, entity_config)
                elif component_type == "list":
                    content = self.frontend_generator.generate_list_component(domain_config, entity_config)
                elif component_type == "service":
                    content = self.frontend_generator.generate_api_service(domain_config, entity_config)
                
                # Write to file
                component_dir = frontend_path / subdirectory
                component_dir.mkdir(parents=True, exist_ok=True)
                
                if component_type == "types":
                    filename = f"{entity_config.name.lower()}-types.{extension}"
                elif component_type == "service":
                    filename = f"{entity_config.name.lower()}-api.{extension}"
                else:
                    filename = f"{entity_config.name}{component_type.title()}.{extension}"
                
                file_path = component_dir / filename
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                # Record success
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                results.append(GenerationResult(
                    success=True,
                    entity_name=entity_config.name,
                    component_type=f"frontend_{component_type}",
                    file_path=str(file_path),
                    content_length=len(content),
                    generation_time_seconds=generation_time
                ))
                
                logger.debug(f"Generated frontend {component_type} for {entity_config.name}: "
                           f"{len(content)} chars -> {file_path}")
                
            except Exception as e:
                # Record failure
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                results.append(GenerationResult(
                    success=False,
                    entity_name=entity_config.name,
                    component_type=f"frontend_{component_type}",
                    error_message=str(e),
                    generation_time_seconds=generation_time
                ))
                
                logger.error(f"Failed to generate frontend {component_type} for {entity_config.name}: {e}")
        
        return results
    
    def _generate_application_structure(
        self, 
        domain_config: DomainConfig,
        output_path: Path,
        include_backend: bool,
        include_frontend: bool
    ) -> List[GenerationResult]:
        """Generate application structure files (main.py, __init__.py, etc.)."""
        results = []
        
        try:
            if include_backend:
                # Generate backend structure files
                backend_structure_results = self._generate_backend_structure(domain_config, output_path)
                results.extend(backend_structure_results)
            
            if include_frontend:
                # Generate frontend structure files
                frontend_structure_results = self._generate_frontend_structure(domain_config, output_path)
                results.extend(frontend_structure_results)
            
            # Generate README and documentation
            readme_result = self._generate_readme(domain_config, output_path)
            if readme_result:
                results.append(readme_result)
                
        except Exception as e:
            logger.error(f"Failed to generate application structure: {e}")
            results.append(GenerationResult(
                success=False,
                entity_name="application",
                component_type="structure",
                error_message=str(e)
            ))
        
        return results
    
    def _generate_backend_structure(self, domain_config: DomainConfig, output_path: Path) -> List[GenerationResult]:
        """Generate backend application structure files."""
        results = []
        backend_path = output_path / "backend"
        
        # Create __init__.py files
        init_dirs = ["models", "schemas", "routes", "services"]
        for dir_name in init_dirs:
            dir_path = backend_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
            init_file = dir_path / "__init__.py"
            with open(init_file, 'w') as f:
                f.write(f'"""{dir_name.title()} module for {domain_config.name}."""\n')
            
            results.append(GenerationResult(
                success=True,
                entity_name="application",
                component_type=f"backend_init_{dir_name}",
                file_path=str(init_file),
                content_length=len(f'"""{dir_name.title()} module for {domain_config.name}."""\n')
            ))
        
        return results
    
    def _generate_frontend_structure(self, domain_config: DomainConfig, output_path: Path) -> List[GenerationResult]:
        """Generate frontend application structure files."""
        results = []
        frontend_path = output_path / "frontend"
        
        # Create directory structure
        dirs_to_create = ["src/components", "src/types", "src/services", "src/pages"]
        for dir_name in dirs_to_create:
            dir_path = frontend_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Generate package.json
        package_json_content = self._generate_package_json(domain_config)
        package_json_path = frontend_path / "package.json"
        
        with open(package_json_path, 'w') as f:
            f.write(package_json_content)
        
        results.append(GenerationResult(
            success=True,
            entity_name="application",
            component_type="frontend_package_json",
            file_path=str(package_json_path),
            content_length=len(package_json_content)
        ))
        
        return results
    
    def _generate_package_json(self, domain_config: DomainConfig) -> str:
        """Generate package.json for the frontend application."""
        package_config = {
            "name": f"{domain_config.name.lower().replace(' ', '-')}-frontend",
            "version": "1.0.0",
            "description": f"Frontend application for {domain_config.name}",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
                "test": "jest"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "typescript": "^5.0.0",
                "axios": "^1.4.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0"
            },
            "devDependencies": {
                "vite": "^4.3.0",
                "@vitejs/plugin-react": "^4.0.0",
                "jest": "^29.5.0",
                "@types/jest": "^29.5.0"
            }
        }
        
        return json.dumps(package_config, indent=2)
    
    def _generate_readme(self, domain_config: DomainConfig, output_path: Path) -> Optional[GenerationResult]:
        """Generate README.md for the generated application."""
        try:
            readme_content = f"""# {domain_config.name} Application

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
{domain_config.description or f'Full-stack application for {domain_config.name} domain management.'}

## Entities
{chr(10).join(f'- **{entity.name}**: {entity.description or "Entity for domain operations"}' for entity in domain_config.entities)}

## Structure
```
backend/
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
├── routes/         # FastAPI routes
└── services/       # Business logic services

frontend/
├── src/
│   ├── components/ # React components
│   ├── types/      # TypeScript types
│   ├── services/   # API services
│   └── pages/      # Page components
└── package.json    # Dependencies
```

## Getting Started

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Generated Components

### Backend
{chr(10).join(f'- {entity.name} model, schema, routes, and service' for entity in domain_config.entities)}

### Frontend
{chr(10).join(f'- {entity.name} types, form, list, and API service' for entity in domain_config.entities)}

## API Endpoints

The backend provides RESTful endpoints for each entity:
{chr(10).join(f'''
### {entity.name}
- GET /api/v1/{entity.name.lower()}s - List {entity.name.lower()}s
- POST /api/v1/{entity.name.lower()}s - Create {entity.name.lower()}
- GET /api/v1/{entity.name.lower()}s/{{id}} - Get {entity.name.lower()}
- PUT /api/v1/{entity.name.lower()}s/{{id}} - Update {entity.name.lower()}
- DELETE /api/v1/{entity.name.lower()}s/{{id}} - Delete {entity.name.lower()}''' for entity in domain_config.entities)}

---
*Generated by TeamFlow Code Generation Engine*
"""
            
            readme_path = output_path / "README.md"
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            
            return GenerationResult(
                success=True,
                entity_name="application",
                component_type="readme",
                file_path=str(readme_path),
                content_length=len(readme_content)
            )
            
        except Exception as e:
            logger.error(f"Failed to generate README: {e}")
            return GenerationResult(
                success=False,
                entity_name="application",
                component_type="readme",
                error_message=str(e)
            )
    
    def _save_generation_report(self, summary: GenerationSummary, output_path: Path) -> None:
        """Save detailed generation report to JSON file."""
        try:
            report_data = {
                "domain_name": summary.domain_name,
                "generation_timestamp": datetime.now().isoformat(),
                "statistics": {
                    "total_entities": summary.total_entities,
                    "successful_generations": summary.successful_generations,
                    "failed_generations": summary.failed_generations,
                    "total_files_created": summary.total_files_created,
                    "total_content_length": summary.total_content_length,
                    "generation_time_seconds": summary.generation_time_seconds
                },
                "output_directory": summary.output_directory,
                "results": [
                    {
                        "success": r.success,
                        "entity_name": r.entity_name,
                        "component_type": r.component_type,
                        "file_path": r.file_path,
                        "content_length": r.content_length,
                        "error_message": r.error_message,
                        "generation_time_seconds": r.generation_time_seconds
                    }
                    for r in summary.results
                ],
                "errors": summary.errors
            }
            
            report_path = output_path / "generation_report.json"
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"Generation report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save generation report: {e}")