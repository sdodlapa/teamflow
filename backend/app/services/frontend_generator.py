"""
Frontend Generation Service
For Section 3: Code Generation Engine - Phase 3D
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from app.core.template_engine import TemplateEngine, TemplateEngineError
from app.core.domain_config import DomainConfig, EntityConfig


logger = logging.getLogger(__name__)


class FrontendGeneratorError(Exception):
    """Exception raised by FrontendGenerator."""
    pass


class FrontendGenerator:
    """Service for generating React/TypeScript frontend components from domain configuration."""
    
    def __init__(self, template_engine: Optional[TemplateEngine] = None):
        """Initialize FrontendGenerator.
        
        Args:
            template_engine: Optional template engine instance
        """
        self.template_engine = template_engine or TemplateEngine()
        self.output_base_path = Path("frontend/src/generated")
    
    def generate_types(
        self, 
        domain_config: DomainConfig, 
        entity_config: EntityConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate TypeScript type definitions for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_path: Optional custom output path
            
        Returns:
            Generated TypeScript types as string
            
        Raises:
            FrontendGeneratorError: If generation fails
        """
        try:
            logger.info(f"Generating types for entity: {entity_config.name}")
            
            # Prepare template context
            context = {
                'domain': self._prepare_domain_context(domain_config),
                'entity': self._prepare_entity_context(entity_config)
            }
            
            # Generate types code
            types_code = self.template_engine.render_template(
                "frontend/types.ts.j2", 
                context
            )
            
            # Save to file if output_path specified
            if output_path:
                self._save_generated_code(types_code, output_path)
                logger.info(f"Types saved to: {output_path}")
            
            return types_code
            
        except TemplateEngineError as e:
            raise FrontendGeneratorError(f"Failed to generate types for {entity_config.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating types for {entity_config.name}: {e}")
            raise FrontendGeneratorError(f"Unexpected error: {e}")
    
    def generate_form_component(
        self, 
        domain_config: DomainConfig, 
        entity_config: EntityConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate React form component for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_path: Optional custom output path
            
        Returns:
            Generated form component code as string
        """
        try:
            logger.info(f"Generating form component for entity: {entity_config.name}")
            
            context = {
                'domain': self._prepare_domain_context(domain_config),
                'entity': self._prepare_entity_context(entity_config)
            }
            
            form_code = self.template_engine.render_template(
                "frontend/form.tsx.j2",
                context
            )
            
            if output_path:
                self._save_generated_code(form_code, output_path)
                logger.info(f"Form component saved to: {output_path}")
            
            return form_code
            
        except TemplateEngineError as e:
            raise FrontendGeneratorError(f"Failed to generate form component for {entity_config.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating form component for {entity_config.name}: {e}")
            raise FrontendGeneratorError(f"Unexpected error: {e}")
    
    def generate_list_component(
        self, 
        domain_config: DomainConfig, 
        entity_config: EntityConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate React list/table component for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_path: Optional custom output path
            
        Returns:
            Generated list component code as string
        """
        try:
            logger.info(f"Generating list component for entity: {entity_config.name}")
            
            context = {
                'domain': self._prepare_domain_context(domain_config),
                'entity': self._prepare_entity_context(entity_config)
            }
            
            list_code = self.template_engine.render_template(
                "frontend/list.tsx.j2",
                context
            )
            
            if output_path:
                self._save_generated_code(list_code, output_path)
                logger.info(f"List component saved to: {output_path}")
            
            return list_code
            
        except TemplateEngineError as e:
            raise FrontendGeneratorError(f"Failed to generate list component for {entity_config.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating list component for {entity_config.name}: {e}")
            raise FrontendGeneratorError(f"Unexpected error: {e}")
    
    def generate_api_service(
        self, 
        domain_config: DomainConfig, 
        entity_config: EntityConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate TypeScript API service for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_path: Optional custom output path
            
        Returns:
            Generated API service code as string
        """
        try:
            logger.info(f"Generating API service for entity: {entity_config.name}")
            
            context = {
                'domain': self._prepare_domain_context(domain_config),
                'entity': self._prepare_entity_context(entity_config)
            }
            
            service_code = self.template_engine.render_template(
                "frontend/service.ts.j2",
                context
            )
            
            if output_path:
                self._save_generated_code(service_code, output_path)
                logger.info(f"API service saved to: {output_path}")
            
            return service_code
            
        except TemplateEngineError as e:
            raise FrontendGeneratorError(f"Failed to generate API service for {entity_config.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating API service for {entity_config.name}: {e}")
            raise FrontendGeneratorError(f"Unexpected error: {e}")
    
    def generate_all_for_entity(
        self,
        domain_config: DomainConfig,
        entity_config: EntityConfig,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate all frontend components (types, form, list, service) for an entity.
        
        Args:
            domain_config: Domain configuration
            entity_config: Entity configuration
            output_dir: Optional output directory
            
        Returns:
            Dictionary with component names as keys and generated code as values
        """
        logger.info(f"Generating all frontend components for entity: {entity_config.name}")
        
        entity_snake = entity_config.name.lower().replace(' ', '_')
        
        # Determine output paths
        if output_dir:
            output_dir = Path(output_dir)
            types_path = output_dir / "types" / f"{entity_snake}.types.ts"
            form_path = output_dir / "components" / f"{entity_snake}-form.tsx"
            list_path = output_dir / "components" / f"{entity_snake}-list.tsx"
            service_path = output_dir / "services" / f"{entity_snake}.service.ts"
        else:
            types_path = form_path = list_path = service_path = None
        
        # Generate all components
        results = {}
        
        try:
            results['types'] = self.generate_types(domain_config, entity_config, str(types_path) if types_path else None)
            results['form'] = self.generate_form_component(domain_config, entity_config, str(form_path) if form_path else None)
            results['list'] = self.generate_list_component(domain_config, entity_config, str(list_path) if list_path else None)
            results['service'] = self.generate_api_service(domain_config, entity_config, str(service_path) if service_path else None)
            
            logger.info(f"Successfully generated all frontend components for {entity_config.name}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to generate frontend components for {entity_config.name}: {e}")
            raise FrontendGeneratorError(f"Failed to generate all frontend components: {e}")
    
    def generate_all_for_domain(
        self,
        domain_config: DomainConfig,
        output_dir: Optional[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate all frontend components for all entities in a domain.
        
        Args:
            domain_config: Domain configuration
            output_dir: Optional output directory
            
        Returns:
            Nested dictionary with entity names and their generated components
        """
        logger.info(f"Generating all frontend components for domain: {domain_config.name}")
        
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
                logger.error(f"Failed to generate frontend components for entity {entity_config.name}: {e}")
                # Continue with other entities
                results[entity_config.name] = {"error": str(e)}
        
        logger.info(f"Completed frontend generation for domain: {domain_config.name}")
        return results
    
    def generate_index_files(
        self,
        domain_config: DomainConfig,
        output_dir: str
    ) -> Dict[str, str]:
        """
        Generate index.ts files for organized exports.
        
        Args:
            domain_config: Domain configuration
            output_dir: Output directory
            
        Returns:
            Dictionary with index file paths and their content
        """
        results = {}
        output_path = Path(output_dir)
        
        # Generate types index
        types_index = self._generate_types_index(domain_config)
        types_index_path = output_path / "types" / "index.ts"
        results[str(types_index_path)] = types_index
        
        # Generate components index
        components_index = self._generate_components_index(domain_config)
        components_index_path = output_path / "components" / "index.ts"
        results[str(components_index_path)] = components_index
        
        # Generate services index
        services_index = self._generate_services_index(domain_config)
        services_index_path = output_path / "services" / "index.ts"
        results[str(services_index_path)] = services_index
        
        # Write index files
        for file_path, content in results.items():
            self._save_generated_code(content, file_path)
        
        return results
    
    def _generate_types_index(self, domain_config: DomainConfig) -> str:
        """Generate types index file."""
        exports = []
        for entity in domain_config.entities:
            entity_snake = entity.name.lower().replace(' ', '_')
            exports.append(f"export * from './{entity_snake}.types';")
        
        return "\n".join([
            "/**",
            f" * Generated Types Index for {domain_config.name}",
            f" * Generated on: {self.template_engine.env.globals['today']()}",
            " */",
            "",
            *exports,
            ""
        ])
    
    def _generate_components_index(self, domain_config: DomainConfig) -> str:
        """Generate components index file."""
        exports = []
        for entity in domain_config.entities:
            entity_snake = entity.name.lower().replace(' ', '_')
            entity_camel = entity.name.replace(' ', '')
            exports.append(f"export {{ {entity_camel}Form }} from './{entity_snake}-form';")
            exports.append(f"export {{ {entity_camel}List }} from './{entity_snake}-list';")
        
        return "\n".join([
            "/**",
            f" * Generated Components Index for {domain_config.name}",
            f" * Generated on: {self.template_engine.env.globals['today']()}",
            " */",
            "",
            *exports,
            ""
        ])
    
    def _generate_services_index(self, domain_config: DomainConfig) -> str:
        """Generate services index file."""
        exports = []
        for entity in domain_config.entities:
            entity_snake = entity.name.lower().replace(' ', '_')
            entity_camel = entity.name.replace(' ', '')
            exports.append(f"export {{ {entity_camel}API }} from './{entity_snake}.service';")
        
        return "\n".join([
            "/**",
            f" * Generated Services Index for {domain_config.name}",
            f" * Generated on: {self.template_engine.env.globals['today']()}",
            " */",
            "",
            *exports,
            ""
        ])
    
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
            raise FrontendGeneratorError(f"Failed to save code to {output_path}: {e}")
    
    def validate_entity_config(self, entity_config: EntityConfig) -> List[str]:
        """
        Validate entity configuration for frontend generation.
        
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
        
        # Check for TypeScript-incompatible field names
        js_reserved_words = ['class', 'function', 'var', 'let', 'const', 'return', 'if', 'else', 'for', 'while']
        for field in entity_config.fields:
            if field.name in js_reserved_words:
                issues.append(f"Field name '{field.name}' is a JavaScript reserved word")
        
        # Validate enum fields for frontend
        for field in entity_config.fields:
            if field.type == 'enum':
                if not field.options:
                    issues.append(f"Enum field {field.name} must have options")
                else:
                    for option in field.options:
                        if not option.value:
                            issues.append(f"Enum option in field {field.name} must have a value")
        
        return issues