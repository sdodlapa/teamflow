"""
Template Engine Core - Section 3: Code Generation Engine
Provides Jinja2-based template loading, caching, and code generation orchestration.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError

from app.core.enhanced_domain_config import DomainConfig, EntityConfig, FieldConfig

logger = logging.getLogger(__name__)


class TemplateEngineError(Exception):
    """Template engine related errors."""
    pass


class TemplateEngine:
    """
    Core template engine for code generation using Jinja2.
    
    Features:
    - Template loading and caching
    - Custom filters for code generation
    - Template inheritance and macros
    - Error handling and validation
    """
    
    def __init__(self, template_dir: Union[str, Path] = "templates"):
        """
        Initialize template engine.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = Path(template_dir)
        self._setup_jinja_environment()
        self._template_cache: Dict[str, Template] = {}
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }
        
        logger.info(f"Template engine initialized with directory: {self.template_dir}")
    
    def _setup_jinja_environment(self) -> None:
        """Setup Jinja2 environment with custom configuration."""
        try:
            # Create Jinja2 environment
            self.env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )
            
            # Add custom filters
            self._register_custom_filters()
            
            # Add global functions
            self._register_global_functions()
            
            logger.info("Jinja2 environment setup complete")
            
        except Exception as e:
            raise TemplateEngineError(f"Failed to setup Jinja2 environment: {e}")
    
    def _register_custom_filters(self) -> None:
        """Register custom Jinja2 filters for code generation."""
        
        def snake_case(text: str) -> str:
            """Convert text to snake_case."""
            import re
            # Replace spaces and hyphens with underscores first
            text = re.sub(r'[-\s]+', '_', text)
            # Insert underscore before capital letters (but not at start)
            text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
            return text.lower()
        
        def camel_case(text: str) -> str:
            """Convert text to CamelCase."""
            components = text.split('_')
            return ''.join(word.capitalize() for word in components)
        
        def pascal_case(text: str) -> str:
            """Convert text to PascalCase (same as CamelCase)."""
            return camel_case(text)
        
        def plural(text: str) -> str:
            """Convert singular noun to plural."""
            # Simple pluralization rules
            if text.endswith('y'):
                return text[:-1] + 'ies'
            elif text.endswith(('s', 'sh', 'ch', 'x', 'z')):
                return text + 'es'
            else:
                return text + 's'
        
        def singular(text: str) -> str:
            """Convert plural noun to singular."""
            # Simple singularization rules
            if text.endswith('ies'):
                return text[:-3] + 'y'
            elif text.endswith('es') and text[:-2].endswith(('s', 'sh', 'ch', 'x', 'z')):
                return text[:-2]
            elif text.endswith('s') and not text.endswith('ss'):
                return text[:-1]
            else:
                return text
        
        def sqlalchemy_type(field_type: str) -> str:
            """Convert domain field type to SQLAlchemy column type."""
            type_mapping = {
                'string': 'String',
                'text': 'Text',
                'integer': 'Integer',
                'decimal': 'Numeric',
                'boolean': 'Boolean',
                'date': 'Date',
                'datetime': 'DateTime',
                'time': 'Time',
                'email': 'String',
                'phone': 'String',
                'url': 'String',
                'json': 'JSON',
                'file': 'String'
            }
            return type_mapping.get(field_type, 'String')
        
        def python_type(field_type: str, optional: bool = False) -> str:
            """Convert domain field type to Python type annotation."""
            type_mapping = {
                'string': 'str',
                'text': 'str', 
                'integer': 'int',
                'decimal': 'Decimal',
                'boolean': 'bool',
                'date': 'date',
                'datetime': 'datetime',
                'time': 'time',
                'email': 'str',
                'phone': 'str',
                'url': 'str',
                'json': 'Dict[str, Any]',
                'file': 'str'
            }
            python_type = type_mapping.get(field_type, 'str')
            
            if optional:
                return f"Optional[{python_type}]"
            return python_type
        
        def typescript_type(field_type: str, optional: bool = False) -> str:
            """Convert domain field type to TypeScript type."""
            type_mapping = {
                'string': 'string',
                'text': 'string',
                'integer': 'number',
                'decimal': 'number',
                'boolean': 'boolean',
                'date': 'string',  # ISO date string
                'datetime': 'string',  # ISO datetime string
                'time': 'string',  # ISO time string
                'email': 'string',
                'phone': 'string',
                'url': 'string',
                'json': 'any',
                'file': 'string'
            }
            ts_type = type_mapping.get(field_type, 'string')
            
            if optional:
                return f"{ts_type} | null"
            return ts_type
        
        # Register filters
        self.env.filters['snake_case'] = snake_case
        self.env.filters['camel_case'] = camel_case
        self.env.filters['pascal_case'] = pascal_case
        self.env.filters['plural'] = plural
        self.env.filters['singular'] = singular
        self.env.filters['sqlalchemy_type'] = sqlalchemy_type
        self.env.filters['python_type'] = python_type
        self.env.filters['typescript_type'] = typescript_type
        
        logger.info("Custom Jinja2 filters registered")
    
    def _register_global_functions(self) -> None:
        """Register global functions available in all templates."""
        
        def now() -> datetime:
            """Get current datetime."""
            return datetime.now()
        
        def today() -> str:
            """Get today's date as string."""
            return datetime.now().strftime("%Y-%m-%d")
        
        def timestamp() -> str:
            """Get current timestamp as string."""
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        def get_imports(entity_config: EntityConfig) -> List[str]:
            """Generate Python imports for an entity."""
            imports = set()
            
            # Base imports
            imports.add("from datetime import datetime, date, time")
            imports.add("from typing import Optional, List, Dict, Any")
            imports.add("from decimal import Decimal")
            
            # SQLAlchemy imports based on field types
            has_relationships = bool(entity_config.relationships)
            has_enum = any(hasattr(field, 'options') and field.options for field in entity_config.fields)
            
            if has_relationships:
                imports.add("from sqlalchemy.orm import relationship")
            if has_enum:
                imports.add("import enum")
            
            return sorted(list(imports))
        
        # Register global functions
        self.env.globals['now'] = now
        self.env.globals['today'] = today
        self.env.globals['timestamp'] = timestamp
        self.env.globals['get_imports'] = get_imports
        
        logger.info("Global template functions registered")
    
    def load_template(self, template_name: str, use_cache: bool = True) -> Template:
        """
        Load a Jinja2 template with optional caching.
        
        Args:
            template_name: Name/path of template relative to template_dir
            use_cache: Whether to use template caching
            
        Returns:
            Loaded Jinja2 template
            
        Raises:
            TemplateEngineError: If template loading fails
        """
        try:
            # Check cache first
            if use_cache and template_name in self._template_cache:
                self._cache_stats['hits'] += 1
                logger.debug(f"Template cache hit: {template_name}")
                return self._template_cache[template_name]
            
            # Load template
            template = self.env.get_template(template_name)
            
            # Cache template if caching enabled
            if use_cache:
                self._template_cache[template_name] = template
                self._cache_stats['misses'] += 1
                logger.debug(f"Template loaded and cached: {template_name}")
            
            return template
            
        except TemplateNotFound as e:
            self._cache_stats['errors'] += 1
            raise TemplateEngineError(f"Template not found: {template_name}")
        except TemplateSyntaxError as e:
            self._cache_stats['errors'] += 1
            raise TemplateEngineError(f"Template syntax error in {template_name}: {e}")
        except Exception as e:
            self._cache_stats['errors'] += 1
            raise TemplateEngineError(f"Failed to load template {template_name}: {e}")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with given context.
        
        Args:
            template_name: Name of template to render
            context: Template context variables
            
        Returns:
            Rendered template content
            
        Raises:
            TemplateEngineError: If rendering fails
        """
        try:
            template = self.load_template(template_name)
            
            # Add common context variables
            common_context = {
                'generated_at': datetime.now(),
                'generator': 'TeamFlow Template Engine',
                'version': '1.0.0'
            }
            
            # Merge contexts (explicit context takes precedence)
            full_context = {**common_context, **context}
            
            # Render template
            rendered = template.render(**full_context)
            
            logger.debug(f"Template rendered successfully: {template_name}")
            return rendered
            
        except Exception as e:
            raise TemplateEngineError(f"Failed to render template {template_name}: {e}")
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with given context.
        
        Args:
            template_string: Template content as string
            context: Template context variables
            
        Returns:
            Rendered template content
        """
        try:
            template = self.env.from_string(template_string)
            
            # Add common context variables
            common_context = {
                'generated_at': datetime.now(),
                'generator': 'TeamFlow Template Engine',
                'version': '1.0.0'
            }
            
            # Merge contexts
            full_context = {**common_context, **context}
            
            return template.render(**full_context)
            
        except Exception as e:
            raise TemplateEngineError(f"Failed to render template string: {e}")
    
    def get_available_templates(self) -> List[str]:
        """Get list of available templates."""
        templates = []
        try:
            for template_name in self.env.list_templates():
                templates.append(template_name)
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
        
        return sorted(templates)
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validate a template and return validation results.
        
        Args:
            template_name: Template to validate
            
        Returns:
            Validation results with status and any errors
        """
        try:
            template = self.load_template(template_name, use_cache=False)
            
            # Try to parse template
            self.env.parse(template.source)
            
            return {
                'valid': True,
                'template': template_name,
                'message': 'Template is valid',
                'errors': []
            }
            
        except TemplateSyntaxError as e:
            return {
                'valid': False,
                'template': template_name,
                'message': f'Template syntax error: {e}',
                'errors': [str(e)],
                'line': e.lineno
            }
        except Exception as e:
            return {
                'valid': False,
                'template': template_name,
                'message': f'Template validation error: {e}',
                'errors': [str(e)]
            }
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self._template_cache.clear()
        logger.info("Template cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get template cache statistics."""
        total_requests = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = (self._cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cached_templates': len(self._template_cache),
            'cache_hits': self._cache_stats['hits'],
            'cache_misses': self._cache_stats['misses'],
            'cache_errors': self._cache_stats['errors'],
            'hit_rate_percent': round(hit_rate, 2),
            'available_templates': len(self.get_available_templates())
        }


# Global template engine instance
_template_engine_instance: Optional[TemplateEngine] = None

def get_template_engine(template_dir: Union[str, Path] = "templates") -> TemplateEngine:
    """
    Get global template engine instance.
    
    Args:
        template_dir: Template directory path
        
    Returns:
        Template engine instance
    """
    global _template_engine_instance
    
    if _template_engine_instance is None:
        _template_engine_instance = TemplateEngine(template_dir)
    
    return _template_engine_instance


def reset_template_engine() -> None:
    """Reset global template engine instance (useful for testing)."""
    global _template_engine_instance
    _template_engine_instance = None