"""
Model Generation Service
For Section 3: Code Generation Engine
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from app.core.template_engine import TemplateEngine, TemplateEngineError
from app.core.domain_config import DomainConfig, EntityConfig


logger = logging.getLogger(__name__)


class ModelGeneratorError(Exception):
    """Exception raised by ModelGenerator."""
    pass


class ModelGenerator:
    """Service for generating SQLAlchemy models from domain configuration."""
    
    def __init__(self, template_engine: Optional[TemplateEngine] = None):
        """Initialize ModelGenerator.
        
        Args:
            template_engine: Optional template engine instance
        """
        self.template_engine = template_engine or TemplateEngine()
        self.output_base_path = Path("backend/app/generated")
    
    def generate_model(
        self, 
        domain_config: DomainConfig, 
        entity_config: EntityConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate SQLAlchemy model for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_path: Optional custom output path
            
        Returns:
            Generated model code as string
            
        Raises:
            ModelGeneratorError: If generation fails
        """
        try:
            logger.info(f"Generating model for entity: {entity_config.name}")
            
            # Prepare template context
            context = {
                'domain': self._prepare_domain_context(domain_config),
                'entity': self._prepare_entity_context(entity_config)
            }
            
            # Generate model code
            model_code = self.template_engine.render_template(
                "backend/model.py.j2", 
                context
            )
            
            # Save to file if output_path specified
            if output_path:
                self._save_generated_code(model_code, output_path)
                logger.info(f"Model saved to: {output_path}")
            
            return model_code
            
        except TemplateEngineError as e:
            raise ModelGeneratorError(f"Failed to generate model for {entity_config.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating model for {entity_config.name}: {e}")
            raise ModelGeneratorError(f"Unexpected error: {e}")
    
    def generate_schema(
        self, 
        domain_config: DomainConfig, 
        entity_config: EntityConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate Pydantic schemas for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_path: Optional custom output path
            
        Returns:
            Generated schema code as string
        """
        try:
            logger.info(f"Generating schema for entity: {entity_config.name}")
            
            context = {
                'domain': self._prepare_domain_context(domain_config),
                'entity': self._prepare_entity_context(entity_config)
            }
            
            schema_code = self.template_engine.render_template(
                "backend/schema.py.j2",
                context
            )
            
            if output_path:
                self._save_generated_code(schema_code, output_path)
                logger.info(f"Schema saved to: {output_path}")
            
            return schema_code
            
        except TemplateEngineError as e:
            raise ModelGeneratorError(f"Failed to generate schema for {entity_config.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating schema for {entity_config.name}: {e}")
            raise ModelGeneratorError(f"Unexpected error: {e}")
    
    def generate_routes(
        self, 
        domain_config: DomainConfig, 
        entity_config: EntityConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate FastAPI routes for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_path: Optional custom output path
            
        Returns:
            Generated routes code as string
        """
        try:
            logger.info(f"Generating routes for entity: {entity_config.name}")
            
            context = {
                'domain': self._prepare_domain_context(domain_config),
                'entity': self._prepare_entity_context(entity_config)
            }
            
            routes_code = self.template_engine.render_template(
                "backend/routes.py.j2",
                context
            )
            
            if output_path:
                self._save_generated_code(routes_code, output_path)
                logger.info(f"Routes saved to: {output_path}")
            
            return routes_code
            
        except TemplateEngineError as e:
            raise ModelGeneratorError(f"Failed to generate routes for {entity_config.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating routes for {entity_config.name}: {e}")
            raise ModelGeneratorError(f"Unexpected error: {e}")
    
    def generate_service(
        self, 
        domain_config: DomainConfig, 
        entity_config: EntityConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate service class for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_path: Optional custom output path
            
        Returns:
            Generated service code as string
        """
        try:
            logger.info(f"Generating service for entity: {entity_config.name}")
            
            context = {
                'domain': self._prepare_domain_context(domain_config),
                'entity': self._prepare_entity_context(entity_config)
            }
            
            service_code = self.template_engine.render_template(
                "backend/service.py.j2",
                context
            )
            
            if output_path:
                self._save_generated_code(service_code, output_path)
                logger.info(f"Service saved to: {output_path}")
            
            return service_code
            
        except TemplateEngineError as e:
            raise ModelGeneratorError(f"Failed to generate service for {entity_config.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating service for {entity_config.name}: {e}")
            raise ModelGeneratorError(f"Unexpected error: {e}")
    
    def generate_all_for_entity(
        self,
        domain_config: DomainConfig,
        entity_config: EntityConfig,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate all components (model, schema, routes, service) for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_dir: Optional output directory
            
        Returns:
            Dictionary with component names as keys and generated code as values
        """
        logger.info(f"Generating all components for entity: {entity_config.name}")
        
        entity_snake = entity_config.name.lower().replace(' ', '_')
        
        # Determine output paths
        if output_dir:
            output_dir = Path(output_dir)
            model_path = output_dir / f"{entity_snake}.py"
            schema_path = output_dir / f"{entity_snake}_schema.py"
            routes_path = output_dir / f"{entity_snake}_routes.py"
            service_path = output_dir / f"{entity_snake}_service.py"
        else:
            model_path = schema_path = routes_path = service_path = None
        
        # Generate all components
        results = {}
        
        try:
            results['model'] = self.generate_model(domain_config, entity_config, str(model_path) if model_path else None)
            results['schema'] = self.generate_schema(domain_config, entity_config, str(schema_path) if schema_path else None)
            results['routes'] = self.generate_routes(domain_config, entity_config, str(routes_path) if routes_path else None)
            results['service'] = self.generate_service(domain_config, entity_config, str(service_path) if service_path else None)
            
            logger.info(f"Successfully generated all components for {entity_config.name}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to generate components for {entity_config.name}: {e}")
            raise ModelGeneratorError(f"Failed to generate all components: {e}")
    
    def generate_all_for_domain(
        self,
        domain_config: DomainConfig,
        output_dir: Optional[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate all components for all entities in a domain.
        
        Args:
            domain_config: Domain configuration
            output_dir: Optional output directory
            
        Returns:
            Nested dictionary with entity names and their generated components
        """
        logger.info(f"Generating all components for domain: {domain_config.name}")
        
        results = {}
        
        for entity_config in domain_config.entities:
            try:
                entity_output_dir = None
                if output_dir:
                    entity_snake = entity_config.name.lower().replace(' ', '_')
                    entity_output_dir = os.path.join(output_dir, entity_snake)
                    os.makedirs(entity_output_dir, exist_ok=True)
                
                results[entity_config.name] = self.generate_all_for_entity(
                    domain_config, 
                    entity_config, 
                    entity_output_dir
                )
                
            except Exception as e:
                logger.error(f"Failed to generate components for entity {entity_config.name}: {e}")
                # Continue with other entities
                results[entity_config.name] = {"error": str(e)}
        
        logger.info(f"Completed generation for domain: {domain_config.name}")
        return results
    
    def _prepare_domain_context(self, domain_config: DomainConfig) -> Dict[str, Any]:
        """Prepare domain context for templates."""
        return {
            'name': domain_config.name,
            'description': domain_config.description,
            'api_prefix': domain_config.api_prefix,
            'enable_audit': domain_config.enable_audit,
            'enable_cache': domain_config.enable_cache
        }
    
    def _prepare_entity_context(self, entity_config: EntityConfig) -> Dict[str, Any]:
        """Prepare entity context for templates."""
        # Convert dataclass to dict for template access
        entity_dict = asdict(entity_config)
        
        # Add computed properties manually since they don't serialize
        entity_dict['enums'] = [asdict(enum_field) for enum_field in entity_config.enums]
        entity_dict['validations'] = [asdict(validation) for validation in entity_config.validations]
        
        return entity_dict
    
    def _save_generated_code(self, code: str, output_path: str) -> None:
        """Save generated code to file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
                
        except Exception as e:
            raise ModelGeneratorError(f"Failed to save code to {output_path}: {e}")
    
    def validate_entity_config(self, entity_config: EntityConfig) -> List[str]:
        """
        Validate entity configuration and return list of issues.
        
        Args:
            entity_config: Entity configuration to validate
            
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Check entity name
        if not entity_config.name or not entity_config.name.strip():
            issues.append("Entity name is required")
        
        # Check fields
        if not entity_config.fields:
            issues.append("Entity must have at least one field")
        
        field_names = set()
        for field in entity_config.fields:
            if not field.name:
                issues.append("Field name is required")
                continue
            
            if field.name in field_names:
                issues.append(f"Duplicate field name: {field.name}")
            field_names.add(field.name)
            
            # Validate enum fields
            if field.type == 'enum':
                if not field.options or not field.options:
                    issues.append(f"Enum field {field.name} must have options")
        
        # Check relationships
        relationship_names = set()
        for rel in entity_config.relationships:
            if not rel.name:
                issues.append("Relationship name is required")
                continue
                
            if rel.name in relationship_names:
                issues.append(f"Duplicate relationship name: {rel.name}")
            relationship_names.add(rel.name)
            
            if not rel.target:
                issues.append(f"Relationship {rel.name} must have a target entity")
        
        return issues