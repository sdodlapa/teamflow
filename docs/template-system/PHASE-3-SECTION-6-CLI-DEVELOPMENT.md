# 🚀 PHASE 3: IMPLEMENTATION GUIDE
## Section 6: CLI Development Implementation

---

## 🖥️ CLI DEVELOPMENT IMPLEMENTATION

### **Implementation Strategy**

The Command Line Interface (CLI) serves as the primary interface for developers to interact with the template system, providing an intuitive and powerful way to generate, manage, and deploy applications across multiple domains.

### **CLI Architecture Overview**

```
CLI Architecture:
1. Command Parser (argparse/click based)
2. Configuration Manager (YAML/JSON handling)
3. Domain Validator (Real-time validation)
4. Generation Orchestrator (Process management)
5. Progress Reporter (Real-time feedback)
6. Error Handler (Comprehensive error management)
```

### **Step 1: Core CLI Framework**

#### **File: `backend/app/template_system/cli/core.py`**

**Implementation Strategy:**
- Modern CLI framework with rich formatting and progress bars
- Intuitive command structure with subcommands
- Comprehensive help system with examples
- Configuration management and profile support

**CLI Core Implementation:**
```python
import click
import asyncio
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.syntax import Syntax
from dataclasses import dataclass

from app.template_system.core.template_system import TemplateSystem
from app.template_system.core.domain_config import DomainConfig
from app.template_system.cli.config_manager import CLIConfigManager
from app.template_system.cli.validators import DomainConfigValidator
from app.template_system.cli.progress_reporter import ProgressReporter

console = Console()

@dataclass
class CLIContext:
    config_manager: CLIConfigManager
    template_system: TemplateSystem
    progress_reporter: ProgressReporter
    current_profile: Optional[str] = None
    debug_mode: bool = False
    quiet_mode: bool = False

@click.group()
@click.option('--profile', '-p', help='Configuration profile to use')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-essential output')
@click.option('--config-dir', type=click.Path(), help='Configuration directory path')
@click.pass_context
def cli(ctx, profile, debug, quiet, config_dir):
    """TeamFlow Template System CLI - Generate applications from domain configurations"""
    
    # Initialize CLI context
    config_manager = CLIConfigManager(config_dir or Path.home() / '.teamflow')
    template_system = TemplateSystem()
    progress_reporter = ProgressReporter(console, quiet_mode=quiet)
    
    ctx.obj = CLIContext(
        config_manager=config_manager,
        template_system=template_system,
        progress_reporter=progress_reporter,
        current_profile=profile,
        debug_mode=debug,
        quiet_mode=quiet
    )
    
    # Load configuration
    if profile:
        try:
            config_manager.load_profile(profile)
        except Exception as e:
            console.print(f"[red]Error loading profile '{profile}': {e}[/red]")
            sys.exit(1)

@cli.command()
@click.argument('domain_config_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--template', '-t', help='Template name to use')
@click.option('--force', is_flag=True, help='Overwrite existing files')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without creating files')
@click.option('--validate-only', is_flag=True, help='Only validate configuration without generating')
@click.pass_obj
def generate(ctx: CLIContext, domain_config_file, output, template, force, dry_run, validate_only):
    """Generate application from domain configuration file"""
    
    try:
        # Load and validate domain configuration
        console.print("[bold blue]Loading domain configuration...[/bold blue]")
        domain_config = ctx.config_manager.load_domain_config(Path(domain_config_file))
        
        # Validate configuration
        console.print("[bold blue]Validating configuration...[/bold blue]")
        validator = DomainConfigValidator()
        validation_result = validator.validate(domain_config)
        
        if not validation_result.is_valid:
            console.print("[red]Configuration validation failed:[/red]")
            for error in validation_result.errors:
                console.print(f"  • {error}")
            sys.exit(1)
        
        if validation_result.warnings:
            console.print("[yellow]Configuration warnings:[/yellow]")
            for warning in validation_result.warnings:
                console.print(f"  • {warning}")
        
        if validate_only:
            console.print("[green]✓ Configuration is valid[/green]")
            return
        
        # Determine output directory
        if not output:
            output = Path.cwd() / domain_config.domain.name.lower().replace(' ', '_')
        else:
            output = Path(output)
        
        # Check for existing files
        if output.exists() and not force and not dry_run:
            if not click.confirm(f"Directory {output} already exists. Continue?"):
                console.print("[yellow]Generation cancelled[/yellow]")
                return
        
        # Run generation
        if dry_run:
            console.print(f"[yellow]DRY RUN - Would generate to: {output}[/yellow]")
            preview = ctx.template_system.preview_generation(domain_config)
            _display_generation_preview(preview)
        else:
            console.print(f"[bold green]Generating application to: {output}[/bold green]")
            asyncio.run(_run_generation(ctx, domain_config, output, template))
        
    except Exception as e:
        if ctx.debug_mode:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

async def _run_generation(ctx: CLIContext, domain_config: DomainConfig, 
                         output_path: Path, template_name: Optional[str]):
    """Run the generation process with progress reporting"""
    
    # Create progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        # Add main task
        main_task = progress.add_task("Generating application...", total=100)
        
        # Setup progress callbacks
        def on_stage_start(stage_name: str, stage_progress: int):
            progress.update(main_task, description=f"[bold blue]{stage_name}[/bold blue]", completed=stage_progress)
        
        def on_stage_complete(stage_name: str, stage_progress: int):
            progress.update(main_task, completed=stage_progress)
        
        # Configure template system with callbacks
        ctx.template_system.set_progress_callbacks(on_stage_start, on_stage_complete)
        
        # Run generation
        generation_result = await ctx.template_system.generate_application_async(
            domain_config, output_path, template_name
        )
        
        progress.update(main_task, completed=100, description="[bold green]Generation complete![/bold green]")
    
    # Display results
    _display_generation_results(generation_result)

def _display_generation_results(result):
    """Display generation results in a formatted table"""
    
    if result.success:
        console.print("[bold green]✓ Generation completed successfully![/bold green]")
        
        # Files generated table
        table = Table(title="Generated Files")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_column("Size", justify="right", style="green")
        
        for file_type, files in result.files_by_type.items():
            total_size = sum(f.size for f in files)
            table.add_row(file_type.title(), str(len(files)), _format_file_size(total_size))
        
        console.print(table)
        
        # Summary statistics
        console.print(f"\n[bold]Total files generated:[/bold] {result.total_files}")
        console.print(f"[bold]Total lines of code:[/bold] {result.total_lines:,}")
        console.print(f"[bold]Generation time:[/bold] {result.generation_time:.2f}s")
        console.print(f"[bold]Estimated development time saved:[/bold] {result.estimated_time_saved}")
        
    else:
        console.print("[red]✗ Generation failed![/red]")
        for error in result.errors:
            console.print(f"  • {error}")

@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_obj
def validate(ctx: CLIContext, config_file):
    """Validate a domain configuration file"""
    
    try:
        domain_config = ctx.config_manager.load_domain_config(Path(config_file))
        validator = DomainConfigValidator()
        result = validator.validate(domain_config)
        
        if result.is_valid:
            console.print("[green]✓ Configuration is valid[/green]")
            if result.warnings:
                console.print("[yellow]Warnings:[/yellow]")
                for warning in result.warnings:
                    console.print(f"  • {warning}")
        else:
            console.print("[red]✗ Configuration is invalid[/red]")
            for error in result.errors:
                console.print(f"  • {error}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error validating configuration: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('domain_name')
@click.option('--template', '-t', default='basic', help='Template to use as base')
@click.option('--interactive', '-i', is_flag=True, help='Interactive configuration wizard')
@click.pass_obj
def init(ctx: CLIContext, domain_name, template, interactive):
    """Initialize a new domain configuration"""
    
    config_file = Path(f"{domain_name.lower().replace(' ', '_')}_config.yaml")
    
    if config_file.exists():
        if not click.confirm(f"Configuration file {config_file} already exists. Overwrite?"):
            console.print("[yellow]Initialization cancelled[/yellow]")
            return
    
    if interactive:
        domain_config = _run_interactive_wizard(domain_name, template)
    else:
        domain_config = ctx.config_manager.create_basic_config(domain_name, template)
    
    # Save configuration
    ctx.config_manager.save_domain_config(domain_config, config_file)
    
    console.print(f"[green]✓ Domain configuration created: {config_file}[/green]")
    console.print(f"Edit the configuration file and run: [bold]teamflow generate {config_file}[/bold]")

def _run_interactive_wizard(domain_name: str, template: str) -> DomainConfig:
    """Run interactive configuration wizard"""
    
    console.print(Panel(f"[bold blue]Interactive Configuration Wizard for '{domain_name}'[/bold blue]"))
    
    # Basic domain information
    description = click.prompt("Domain description", default="")
    business_model = click.prompt("Business model", default="saas")
    
    # Create base configuration
    domain_config = DomainConfig.create_basic(domain_name, description, business_model)
    
    # Entity creation loop
    console.print("\n[bold]Add entities to your domain:[/bold]")
    
    while True:
        entity_name = click.prompt("Entity name (or 'done' to finish)", default="done")
        if entity_name.lower() == 'done':
            break
        
        entity_description = click.prompt(f"Description for {entity_name}", default="")
        
        # Create entity with basic fields
        entity_config = EntityConfig(
            name=entity_name,
            description=entity_description,
            fields=_create_basic_fields_interactive()
        )
        
        domain_config.add_entity(entity_name, entity_config)
        console.print(f"[green]✓ Added entity: {entity_name}[/green]")
    
    return domain_config

def _create_basic_fields_interactive() -> List[FieldConfig]:
    """Interactive field creation"""
    
    fields = []
    common_fields = {
        'id': 'uuid',
        'name': 'string',
        'description': 'text',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    }
    
    console.print("Add common fields? (id, name, description, timestamps)")
    if click.confirm("Add common fields", default=True):
        for field_name, field_type in common_fields.items():
            fields.append(FieldConfig(
                name=field_name,
                type=field_type,
                required=field_name in ['id', 'name']
            ))
    
    # Custom fields
    while True:
        field_name = click.prompt("Additional field name (or 'done')", default="done")
        if field_name.lower() == 'done':
            break
        
        field_type = click.prompt("Field type", type=click.Choice([
            'string', 'text', 'integer', 'decimal', 'boolean', 
            'date', 'datetime', 'uuid', 'json'
        ]))
        
        required = click.confirm(f"Is {field_name} required?", default=False)
        
        fields.append(FieldConfig(
            name=field_name,
            type=field_type,
            required=required
        ))
    
    return fields
```

### **Step 2: Advanced CLI Commands**

#### **File: `backend/app/template_system/cli/advanced_commands.py`**

**Implementation Strategy:**
- Domain management commands (list, update, delete)
- Template management and customization
- Multi-domain operations
- Plugin management commands

**Advanced Commands Implementation:**
```python
import click
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from pathlib import Path
from typing import List, Dict, Optional

@cli.group()
def domain():
    """Domain management commands"""
    pass

@domain.command()
@click.pass_obj
def list(ctx: CLIContext):
    """List all available domain configurations"""
    
    configs = ctx.config_manager.list_domain_configs()
    
    if not configs:
        console.print("[yellow]No domain configurations found[/yellow]")
        return
    
    table = Table(title="Available Domain Configurations")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Entities", justify="right", style="magenta")
    table.add_column("Last Modified", style="green")
    
    for config in configs:
        table.add_row(
            config.name,
            config.description[:50] + "..." if len(config.description) > 50 else config.description,
            str(len(config.entities)),
            config.last_modified.strftime("%Y-%m-%d %H:%M")
        )
    
    console.print(table)

@domain.command()
@click.argument('domain_name')
@click.pass_obj
def info(ctx: CLIContext, domain_name):
    """Show detailed information about a domain"""
    
    try:
        config = ctx.config_manager.get_domain_config(domain_name)
        
        # Domain overview
        console.print(Panel(f"[bold blue]{config.domain.name}[/bold blue]\n{config.domain.description}"))
        
        # Entities tree
        tree = Tree(f"[bold]Entities ({len(config.entities)})[/bold]")
        
        for entity_name, entity_config in config.entities.items():
            entity_branch = tree.add(f"[cyan]{entity_name}[/cyan]")
            
            # Fields
            fields_branch = entity_branch.add(f"[yellow]Fields ({len(entity_config.fields)})[/yellow]")
            for field in entity_config.fields[:5]:  # Show first 5 fields
                fields_branch.add(f"{field.name}: {field.type}")
            if len(entity_config.fields) > 5:
                fields_branch.add(f"... and {len(entity_config.fields) - 5} more")
            
            # Relationships
            if entity_config.relationships:
                rel_branch = entity_branch.add(f"[green]Relationships ({len(entity_config.relationships)})[/green]")
                for rel in entity_config.relationships[:3]:
                    rel_branch.add(f"{rel.type} -> {rel.target}")
                if len(entity_config.relationships) > 3:
                    rel_branch.add(f"... and {len(entity_config.relationships) - 3} more")
        
        console.print(tree)
        
        # Statistics
        total_fields = sum(len(entity.fields) for entity in config.entities.values())
        total_relationships = sum(len(entity.relationships) for entity in config.entities.values())
        
        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total entities: {len(config.entities)}")
        console.print(f"  Total fields: {total_fields}")
        console.print(f"  Total relationships: {total_relationships}")
        
    except Exception as e:
        console.print(f"[red]Error loading domain '{domain_name}': {e}[/red]")

@cli.group()
def template():
    """Template management commands"""
    pass

@template.command()
@click.pass_obj
def list(ctx: CLIContext):
    """List available templates"""
    
    templates = ctx.template_system.list_available_templates()
    
    table = Table(title="Available Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Version", style="magenta")
    table.add_column("Framework", style="green")
    
    for template in templates:
        table.add_row(
            template.name,
            template.description,
            template.version,
            template.framework
        )
    
    console.print(table)

@template.command()
@click.argument('template_name')
@click.argument('new_name')
@click.option('--description', help='Description for the custom template')
@click.pass_obj
def customize(ctx: CLIContext, template_name, new_name, description):
    """Create a customized version of an existing template"""
    
    try:
        # Copy base template
        custom_template = ctx.template_system.customize_template(
            template_name, new_name, description
        )
        
        console.print(f"[green]✓ Created custom template '{new_name}' based on '{template_name}'[/green]")
        console.print(f"Template location: {custom_template.path}")
        console.print("You can now modify the template files to suit your needs.")
        
    except Exception as e:
        console.print(f"[red]Error creating custom template: {e}[/red]")

@cli.group()
def plugin():
    """Plugin management commands"""
    pass

@plugin.command()
@click.pass_obj
def list(ctx: CLIContext):
    """List installed plugins"""
    
    plugins = ctx.template_system.plugin_manager.list_installed_plugins()
    
    if not plugins:
        console.print("[yellow]No plugins installed[/yellow]")
        return
    
    table = Table(title="Installed Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Description", style="white")
    
    for plugin in plugins:
        status_color = "green" if plugin.enabled else "red"
        status_text = "Enabled" if plugin.enabled else "Disabled"
        
        table.add_row(
            plugin.name,
            plugin.version,
            f"[{status_color}]{status_text}[/{status_color}]",
            plugin.description
        )
    
    console.print(table)

@plugin.command()
@click.argument('plugin_name')
@click.pass_obj
def install(ctx: CLIContext, plugin_name):
    """Install a plugin"""
    
    with console.status(f"Installing plugin '{plugin_name}'..."):
        try:
            result = ctx.template_system.plugin_manager.install_plugin(plugin_name)
            
            if result.success:
                console.print(f"[green]✓ Plugin '{plugin_name}' installed successfully[/green]")
            else:
                console.print(f"[red]✗ Failed to install plugin '{plugin_name}': {result.error}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error installing plugin: {e}[/red]")

@cli.command()
@click.argument('domain_configs', nargs=-1, required=True)
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.pass_obj
def multi_generate(ctx: CLIContext, domain_configs, output):
    """Generate applications from multiple domain configurations"""
    
    if len(domain_configs) < 2:
        console.print("[red]At least 2 domain configurations required for multi-domain generation[/red]")
        sys.exit(1)
    
    console.print(f"[bold blue]Multi-domain generation for {len(domain_configs)} domains[/bold blue]")
    
    # Load all configurations
    configs = []
    for config_path in domain_configs:
        try:
            config = ctx.config_manager.load_domain_config(Path(config_path))
            configs.append(config)
            console.print(f"  ✓ Loaded: {config.domain.name}")
        except Exception as e:
            console.print(f"  ✗ Failed to load {config_path}: {e}")
            sys.exit(1)
    
    # Validate multi-domain compatibility
    compatibility_result = ctx.template_system.validate_multi_domain_compatibility(configs)
    if not compatibility_result.is_compatible:
        console.print("[red]Multi-domain compatibility issues:[/red]")
        for issue in compatibility_result.issues:
            console.print(f"  • {issue}")
        sys.exit(1)
    
    # Determine output directory
    if not output:
        domain_names = [config.domain.name.lower().replace(' ', '_') for config in configs]
        output = Path.cwd() / f"multi_domain_{'_'.join(domain_names)}"
    else:
        output = Path(output)
    
    # Run multi-domain generation
    console.print(f"[bold green]Generating multi-domain application to: {output}[/bold green]")
    
    try:
        result = asyncio.run(ctx.template_system.generate_multi_domain_application(configs, output))
        
        if result.success:
            console.print("[green]✓ Multi-domain generation completed successfully![/green]")
            _display_multi_domain_results(result)
        else:
            console.print("[red]✗ Multi-domain generation failed![/red]")
            for error in result.errors:
                console.print(f"  • {error}")
                
    except Exception as e:
        console.print(f"[red]Error during multi-domain generation: {e}[/red]")
        sys.exit(1)

def _display_multi_domain_results(result):
    """Display multi-domain generation results"""
    
    # Domain summary table
    table = Table(title="Generated Domains")
    table.add_column("Domain", style="cyan")
    table.add_column("Entities", justify="right", style="magenta")
    table.add_column("Files", justify="right", style="green")
    table.add_column("Lines", justify="right", style="yellow")
    
    for domain_result in result.domain_results:
        table.add_row(
            domain_result.domain_name,
            str(domain_result.entity_count),
            str(domain_result.file_count),
            f"{domain_result.line_count:,}"
        )
    
    console.print(table)
    
    # Shared components
    if result.shared_components:
        console.print(f"\n[bold]Shared Components:[/bold] {len(result.shared_components)}")
        for component in result.shared_components[:5]:
            console.print(f"  • {component.name} ({component.type})")
        if len(result.shared_components) > 5:
            console.print(f"  ... and {len(result.shared_components) - 5} more")
    
    # Integration points
    if result.integration_points:
        console.print(f"\n[bold]Integration Points:[/bold] {len(result.integration_points)}")
        for integration in result.integration_points[:3]:
            console.print(f"  • {integration.source} ↔ {integration.target}")
        if len(result.integration_points) > 3:
            console.print(f"  ... and {len(result.integration_points) - 3} more")

@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_obj
def analyze(ctx: CLIContext, config_file):
    """Analyze domain configuration and provide insights"""
    
    try:
        domain_config = ctx.config_manager.load_domain_config(Path(config_file))
        analysis = ctx.template_system.analyze_domain_config(domain_config)
        
        # Display analysis results
        console.print(Panel(f"[bold blue]Analysis Results for '{domain_config.domain.name}'[/bold blue]"))
        
        # Complexity metrics
        console.print(f"[bold]Complexity Metrics:[/bold]")
        console.print(f"  Domain complexity: {analysis.complexity_score}/100")
        console.print(f"  Estimated development time: {analysis.estimated_dev_time}")
        console.print(f"  Generated code size: ~{analysis.estimated_code_size:,} lines")
        
        # Recommendations
        if analysis.recommendations:
            console.print(f"\n[bold]Recommendations:[/bold]")
            for rec in analysis.recommendations:
                icon = "⚠️" if rec.type == "warning" else "💡"
                console.print(f"  {icon} {rec.message}")
        
        # Potential optimizations
        if analysis.optimizations:
            console.print(f"\n[bold]Potential Optimizations:[/bold]")
            for opt in analysis.optimizations:
                console.print(f"  🚀 {opt.description} (Impact: {opt.impact})")
        
    except Exception as e:
        console.print(f"[red]Error analyzing configuration: {e}[/red]")
```

### **Step 3: Configuration Management System**

#### **File: `backend/app/template_system/cli/config_manager.py`**

**Implementation Strategy:**
- Profile-based configuration management
- Environment-specific settings
- Configuration validation and migration
- Secure credential management

**Configuration Manager Implementation:**
```python
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import keyring
from datetime import datetime

@dataclass
class CLIProfile:
    name: str
    description: str
    default_template: str
    output_directory: str
    api_settings: Dict[str, Any]
    generation_settings: Dict[str, Any]
    created_at: datetime
    last_used: datetime

class CLIConfigManager:
    """Comprehensive configuration management for CLI"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.profiles_file = self.config_dir / 'profiles.yaml'
        self.domains_dir = self.config_dir / 'domains'
        self.templates_dir = self.config_dir / 'templates'
        self.cache_dir = self.config_dir / 'cache'
        
        # Create directories
        self.domains_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize encryption for sensitive data
        self.cipher_suite = self._initialize_encryption()
    
    def _initialize_encryption(self) -> Fernet:
        """Initialize encryption for sensitive configuration data"""
        
        # Try to get existing key from keyring
        key = keyring.get_password("teamflow_cli", "encryption_key")
        
        if not key:
            # Generate new key
            key = Fernet.generate_key().decode()
            keyring.set_password("teamflow_cli", "encryption_key", key)
        
        return Fernet(key.encode())
    
    def create_profile(self, name: str, description: str = "", 
                      settings: Optional[Dict[str, Any]] = None) -> CLIProfile:
        """Create a new CLI profile"""
        
        profile = CLIProfile(
            name=name,
            description=description,
            default_template=settings.get('default_template', 'basic') if settings else 'basic',
            output_directory=settings.get('output_directory', str(Path.cwd())) if settings else str(Path.cwd()),
            api_settings=settings.get('api_settings', {}) if settings else {},
            generation_settings=settings.get('generation_settings', {}) if settings else {},
            created_at=datetime.now(),
            last_used=datetime.now()
        )
        
        # Save profile
        self._save_profile(profile)
        
        return profile
    
    def _save_profile(self, profile: CLIProfile):
        """Save profile to configuration file"""
        
        profiles = self._load_profiles()
        profiles[profile.name] = asdict(profile)
        
        with open(self.profiles_file, 'w') as f:
            yaml.dump(profiles, f, default_flow_style=False)
    
    def _load_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load all profiles from configuration file"""
        
        if not self.profiles_file.exists():
            return {}
        
        with open(self.profiles_file, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def list_profiles(self) -> List[CLIProfile]:
        """List all available profiles"""
        
        profiles_data = self._load_profiles()
        profiles = []
        
        for profile_data in profiles_data.values():
            profile = CLIProfile(**profile_data)
            profiles.append(profile)
        
        return sorted(profiles, key=lambda p: p.last_used, reverse=True)
    
    def load_profile(self, profile_name: str) -> CLIProfile:
        """Load a specific profile"""
        
        profiles = self._load_profiles()
        
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        profile_data = profiles[profile_name]
        profile = CLIProfile(**profile_data)
        
        # Update last used
        profile.last_used = datetime.now()
        self._save_profile(profile)
        
        return profile
    
    def save_domain_config(self, domain_config: DomainConfig, filename: Optional[Path] = None):
        """Save domain configuration to file"""
        
        if not filename:
            safe_name = domain_config.domain.name.lower().replace(' ', '_').replace('-', '_')
            filename = self.domains_dir / f"{safe_name}_config.yaml"
        
        # Convert to dictionary
        config_dict = domain_config.to_dict()
        
        # Add metadata
        config_dict['_metadata'] = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'created_by': 'teamflow_cli'
        }
        
        with open(filename, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def load_domain_config(self, config_file: Path) -> DomainConfig:
        """Load domain configuration from file"""
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            if config_file.suffix.lower() == '.json':
                config_dict = json.load(f)
            else:
                config_dict = yaml.safe_load(f)
        
        # Remove metadata if present
        config_dict.pop('_metadata', None)
        
        return DomainConfig.from_dict(config_dict)
    
    def list_domain_configs(self) -> List[DomainConfigSummary]:
        """List all available domain configurations"""
        
        configs = []
        
        for config_file in self.domains_dir.glob("*.yaml"):
            try:
                config = self.load_domain_config(config_file)
                summary = DomainConfigSummary(
                    name=config.domain.name,
                    description=config.domain.description,
                    file_path=config_file,
                    entities=list(config.entities.keys()),
                    last_modified=datetime.fromtimestamp(config_file.stat().st_mtime)
                )
                configs.append(summary)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load {config_file}: {e}[/yellow]")
        
        return sorted(configs, key=lambda c: c.last_modified, reverse=True)
    
    def backup_configuration(self, backup_name: Optional[str] = None) -> Path:
        """Create a backup of all configuration"""
        
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = self.config_dir / 'backups' / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy profiles
        if self.profiles_file.exists():
            shutil.copy2(self.profiles_file, backup_dir / 'profiles.yaml')
        
        # Copy domain configurations
        if self.domains_dir.exists():
            shutil.copytree(self.domains_dir, backup_dir / 'domains', dirs_exist_ok=True)
        
        # Copy custom templates
        if self.templates_dir.exists():
            shutil.copytree(self.templates_dir, backup_dir / 'templates', dirs_exist_ok=True)
        
        return backup_dir
    
    def restore_configuration(self, backup_path: Path):
        """Restore configuration from backup"""
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Restore profiles
        profiles_backup = backup_path / 'profiles.yaml'
        if profiles_backup.exists():
            shutil.copy2(profiles_backup, self.profiles_file)
        
        # Restore domains
        domains_backup = backup_path / 'domains'
        if domains_backup.exists():
            shutil.rmtree(self.domains_dir, ignore_errors=True)
            shutil.copytree(domains_backup, self.domains_dir)
        
        # Restore templates
        templates_backup = backup_path / 'templates'
        if templates_backup.exists():
            shutil.rmtree(self.templates_dir, ignore_errors=True)
            shutil.copytree(templates_backup, self.templates_dir)
```

### **Step 4: Interactive Development Mode**

#### **File: `backend/app/template_system/cli/interactive_mode.py`**

**Implementation Strategy:**
- Real-time configuration editing
- Live preview of generated code
- Interactive debugging and troubleshooting
- Configuration wizard with smart suggestions

**Interactive Mode Implementation:**
```python
import asyncio
from typing import Dict, List, Optional, Any
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Group
from rich.table import Table
from rich.syntax import Syntax

class InteractiveDevelopmentMode:
    """Interactive development mode for real-time configuration and generation"""
    
    def __init__(self, ctx: CLIContext):
        self.ctx = ctx
        self.current_config: Optional[DomainConfig] = None
        self.live_preview = LivePreviewGenerator()
        self.config_editor = InteractiveConfigEditor()
        
    async def run(self, config_file: Optional[Path] = None):
        """Run interactive development mode"""
        
        # Load initial configuration
        if config_file:
            self.current_config = self.ctx.config_manager.load_domain_config(config_file)
        else:
            self.current_config = await self._create_config_interactively()
        
        # Setup layout
        layout = self._create_interactive_layout()
        
        with Live(layout, refresh_per_second=2, screen=True) as live:
            self.live = live
            await self._run_interactive_loop()
    
    def _create_interactive_layout(self) -> Layout:
        """Create the interactive layout"""
        
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="config", ratio=1),
            Layout(name="preview", ratio=2)
        )
        
        return layout
    
    async def _run_interactive_loop(self):
        """Main interactive loop"""
        
        while True:
            # Update display
            self._update_display()
            
            # Wait for user input
            command = await self._get_user_command()
            
            if command == 'quit':
                break
            elif command.startswith('edit'):
                await self._handle_edit_command(command)
            elif command == 'generate':
                await self._handle_generate_command()
            elif command == 'preview':
                await self._handle_preview_command()
            elif command == 'save':
                await self._handle_save_command()
            elif command == 'help':
                self._show_help()
    
    def _update_display(self):
        """Update the interactive display"""
        
        layout = self.live.renderable
        
        # Header
        layout["header"].update(Panel(
            f"[bold blue]TeamFlow Interactive Mode[/bold blue] - {self.current_config.domain.name if self.current_config else 'New Domain'}",
            style="blue"
        ))
        
        # Configuration panel
        config_content = self._render_config_summary()
        layout["config"].update(Panel(
            config_content,
            title="Configuration",
            border_style="green"
        ))
        
        # Preview panel
        preview_content = self._render_preview()
        layout["preview"].update(Panel(
            preview_content,
            title="Live Preview",
            border_style="yellow"
        ))
        
        # Footer
        layout["footer"].update(Panel(
            "[bold]Commands:[/bold] edit <entity> | generate | preview | save | help | quit",
            style="dim"
        ))
    
    def _render_config_summary(self) -> Group:
        """Render configuration summary"""
        
        if not self.current_config:
            return Group("No configuration loaded")
        
        # Domain info
        domain_info = f"[bold]{self.current_config.domain.name}[/bold]\n{self.current_config.domain.description}"
        
        # Entities table
        entities_table = Table(show_header=True, header_style="bold magenta")
        entities_table.add_column("Entity", style="cyan")
        entities_table.add_column("Fields", justify="right")
        entities_table.add_column("Relations", justify="right")
        
        for entity_name, entity_config in self.current_config.entities.items():
            entities_table.add_row(
                entity_name,
                str(len(entity_config.fields)),
                str(len(entity_config.relationships))
            )
        
        return Group(domain_info, "", entities_table)
    
    def _render_preview(self) -> Group:
        """Render live code preview"""
        
        if not self.current_config:
            return Group("No preview available")
        
        # Generate sample code
        sample_entity = next(iter(self.current_config.entities.items()))
        entity_name, entity_config = sample_entity
        
        # Generate model preview
        model_code = self.live_preview.generate_model_preview(entity_name, entity_config)
        
        return Group(
            f"[bold]Sample Model: {entity_name}[/bold]",
            "",
            Syntax(model_code, "python", theme="monokai", line_numbers=True)
        )
    
    async def _handle_edit_command(self, command: str):
        """Handle edit command"""
        
        parts = command.split()
        if len(parts) < 2:
            return
        
        entity_name = parts[1]
        
        if entity_name in self.current_config.entities:
            updated_entity = await self.config_editor.edit_entity_interactive(
                entity_name, self.current_config.entities[entity_name]
            )
            self.current_config.entities[entity_name] = updated_entity
        else:
            # Create new entity
            new_entity = await self.config_editor.create_entity_interactive(entity_name)
            self.current_config.entities[entity_name] = new_entity
    
    async def _handle_generate_command(self):
        """Handle generate command"""
        
        output_dir = Path.cwd() / f"{self.current_config.domain.name.lower().replace(' ', '_')}_generated"
        
        try:
            result = await self.ctx.template_system.generate_application_async(
                self.current_config, output_dir
            )
            
            if result.success:
                self._show_notification(f"✓ Generated to {output_dir}", "green")
            else:
                self._show_notification("✗ Generation failed", "red")
                
        except Exception as e:
            self._show_notification(f"Error: {e}", "red")
    
    def _show_notification(self, message: str, style: str):
        """Show a temporary notification"""
        
        # Implementation for showing notifications in the UI
        pass

class InteractiveConfigEditor:
    """Interactive configuration editor"""
    
    async def edit_entity_interactive(self, entity_name: str, entity_config: EntityConfig) -> EntityConfig:
        """Edit entity configuration interactively"""
        
        # Implementation for interactive entity editing
        # This would involve creating forms, field editors, etc.
        pass
    
    async def create_entity_interactive(self, entity_name: str) -> EntityConfig:
        """Create new entity interactively"""
        
        # Implementation for interactive entity creation
        pass

class LivePreviewGenerator:
    """Generate live previews of code"""
    
    def generate_model_preview(self, entity_name: str, entity_config: EntityConfig) -> str:
        """Generate a preview of the SQLAlchemy model"""
        
        # Simplified model generation for preview
        lines = [
            f"class {entity_name.title()}(BaseModel):",
            f'    __tablename__ = "{entity_name.lower()}"',
            ""
        ]
        
        for field in entity_config.fields[:5]:  # Show first 5 fields
            field_def = f"    {field.name} = sa.Column(sa.{field.type.title()}"
            if not field.required:
                field_def += ", nullable=True"
            field_def += ")"
            lines.append(field_def)
        
        if len(entity_config.fields) > 5:
            lines.append(f"    # ... and {len(entity_config.fields) - 5} more fields")
        
        return "\n".join(lines)
```

---

*Continue to Section 7: Production Deployment Implementation...*