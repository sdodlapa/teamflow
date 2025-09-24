# 🏗️ PHASE 2: TEMPLATE EXTRACTION & ENGINE DESIGN
## Section 8: Migration & Adaptation Manual

---

## 🔄 MIGRATION & ADAPTATION FRAMEWORK

### **Domain Migration Engine**

The migration system provides automated tools for adapting existing TeamFlow applications to new domains, updating configurations, and handling data migrations seamlessly.

#### **Migration Generator** (`backend/app/core/migration_generator.py`)
```python
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import json
import yaml

from app.core.domain_config import DomainConfig, EntityConfig
from app.core.comparison_engine import DomainComparator

class MigrationGenerator:
    """Generate migration scripts and adaptation guides"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.alembic_migration_template = self.env.get_template('alembic_migration.py.j2')
        self.data_migration_template = self.env.get_template('data_migration.py.j2')
        self.config_migration_template = self.env.get_template('config_migration.py.j2')
        self.adaptation_guide_template = self.env.get_template('adaptation_guide.md.j2')
    
    def generate_schema_migration(self, 
                                source_config: DomainConfig,
                                target_config: DomainConfig,
                                migration_name: str) -> str:
        """Generate Alembic migration for schema changes"""
        
        # Compare configurations to identify changes
        comparator = DomainComparator()
        changes = comparator.compare_domains(source_config, target_config)
        
        # Generate migration operations
        migration_ops = self._generate_migration_operations(changes)
        
        # Create migration timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return self.alembic_migration_template.render(
            migration_name=migration_name,
            timestamp=timestamp,
            source_domain=source_config.domain.name,
            target_domain=target_config.domain.name,
            upgrade_operations=migration_ops['upgrade'],
            downgrade_operations=migration_ops['downgrade'],
            changes_summary=changes
        )
    
    def generate_data_migration(self,
                              source_config: DomainConfig,
                              target_config: DomainConfig,
                              migration_strategy: str = 'safe') -> str:
        """Generate data migration script for domain adaptation"""
        
        # Analyze data mapping requirements
        data_mappings = self._analyze_data_mappings(source_config, target_config)
        
        # Generate transformation rules
        transformations = self._generate_transformation_rules(data_mappings)
        
        # Generate validation checks
        validation_checks = self._generate_validation_checks(target_config)
        
        return self.data_migration_template.render(
            source_domain=source_config.domain.name,
            target_domain=target_config.domain.name,
            migration_strategy=migration_strategy,
            data_mappings=data_mappings,
            transformations=transformations,
            validation_checks=validation_checks,
            backup_required=migration_strategy == 'safe'
        )
    
    def generate_configuration_migration(self,
                                       source_config: DomainConfig,
                                       target_config: DomainConfig) -> str:
        """Generate configuration migration script"""
        
        # Compare configurations
        config_changes = self._compare_configurations(source_config, target_config)
        
        # Generate update operations
        update_operations = self._generate_config_updates(config_changes)
        
        return self.config_migration_template.render(
            source_domain=source_config.domain.name,
            target_domain=target_config.domain.name,
            config_changes=config_changes,
            update_operations=update_operations
        )
    
    def generate_adaptation_guide(self,
                                source_config: DomainConfig,
                                target_config: DomainConfig,
                                complexity_level: str = 'intermediate') -> str:
        """Generate comprehensive adaptation guide"""
        
        # Analyze adaptation requirements
        adaptation_analysis = self._analyze_adaptation_requirements(
            source_config, 
            target_config
        )
        
        # Generate step-by-step instructions
        adaptation_steps = self._generate_adaptation_steps(adaptation_analysis)
        
        # Calculate migration effort
        effort_estimation = self._estimate_migration_effort(adaptation_analysis)
        
        # Generate testing checklist
        testing_checklist = self._generate_testing_checklist(target_config)
        
        return self.adaptation_guide_template.render(
            source_domain=source_config.domain.name,
            target_domain=target_config.domain.name,
            complexity_level=complexity_level,
            adaptation_analysis=adaptation_analysis,
            adaptation_steps=adaptation_steps,
            effort_estimation=effort_estimation,
            testing_checklist=testing_checklist,
            generated_date=datetime.now().isoformat()
        )
    
    def _generate_migration_operations(self, changes: Dict) -> Dict[str, List]:
        """Generate Alembic migration operations"""
        upgrade_ops = []
        downgrade_ops = []
        
        # Handle new entities
        for entity_name, entity_config in changes.get('new_entities', {}).items():
            upgrade_ops.append({
                'operation': 'create_table',
                'table_name': entity_name.lower(),
                'columns': self._extract_columns_for_migration(entity_config),
                'constraints': self._extract_constraints_for_migration(entity_config)
            })
            
            downgrade_ops.append({
                'operation': 'drop_table',
                'table_name': entity_name.lower()
            })
        
        # Handle removed entities
        for entity_name in changes.get('removed_entities', []):
            upgrade_ops.append({
                'operation': 'drop_table',
                'table_name': entity_name.lower()
            })
            
            # Note: Would need original entity config for proper downgrade
            downgrade_ops.append({
                'operation': 'create_table',
                'table_name': entity_name.lower(),
                'note': 'Manual recreation required - refer to backup'
            })
        
        # Handle modified entities
        for entity_name, modifications in changes.get('modified_entities', {}).items():
            for modification in modifications:
                if modification['type'] == 'new_field':
                    upgrade_ops.append({
                        'operation': 'add_column',
                        'table_name': entity_name.lower(),
                        'column': modification['field']
                    })
                    downgrade_ops.append({
                        'operation': 'drop_column',
                        'table_name': entity_name.lower(),
                        'column_name': modification['field']['name']
                    })
                
                elif modification['type'] == 'removed_field':
                    upgrade_ops.append({
                        'operation': 'drop_column',
                        'table_name': entity_name.lower(),
                        'column_name': modification['field_name']
                    })
                    downgrade_ops.append({
                        'operation': 'add_column',
                        'table_name': entity_name.lower(),
                        'column': modification['original_field']
                    })
                
                elif modification['type'] == 'modified_field':
                    upgrade_ops.append({
                        'operation': 'alter_column',
                        'table_name': entity_name.lower(),
                        'column_name': modification['field_name'],
                        'changes': modification['changes']
                    })
                    downgrade_ops.append({
                        'operation': 'alter_column',
                        'table_name': entity_name.lower(),
                        'column_name': modification['field_name'],
                        'changes': modification['reverse_changes']
                    })
        
        return {
            'upgrade': upgrade_ops,
            'downgrade': list(reversed(downgrade_ops))
        }
    
    def _analyze_data_mappings(self, 
                             source_config: DomainConfig,
                             target_config: DomainConfig) -> List[Dict]:
        """Analyze data mapping requirements between domains"""
        mappings = []
        
        # Map similar entities
        for target_entity, target_config in target_config.entities.items():
            best_match = self._find_best_entity_match(target_entity, source_config)
            
            if best_match:
                field_mappings = self._map_entity_fields(
                    source_config.entities[best_match],
                    target_config
                )
                
                mappings.append({
                    'source_entity': best_match,
                    'target_entity': target_entity,
                    'confidence': self._calculate_mapping_confidence(
                        source_config.entities[best_match],
                        target_config
                    ),
                    'field_mappings': field_mappings,
                    'transformation_required': self._requires_transformation(
                        source_config.entities[best_match],
                        target_config
                    )
                })
        
        return mappings
    
    def _generate_adaptation_steps(self, analysis: Dict) -> List[Dict]:
        """Generate step-by-step adaptation instructions"""
        steps = []
        step_number = 1
        
        # Preparation steps
        steps.append({
            'number': step_number,
            'category': 'Preparation',
            'title': 'Backup Current System',
            'description': 'Create complete backup of database and configuration files',
            'commands': [
                'pg_dump your_database > backup_$(date +%Y%m%d_%H%M%S).sql',
                'cp -r config/ config_backup_$(date +%Y%m%d_%H%M%S)/'
            ],
            'estimated_time': '15 minutes',
            'risk_level': 'low'
        })
        step_number += 1
        
        # Configuration updates
        if analysis.get('config_changes'):
            steps.append({
                'number': step_number,
                'category': 'Configuration',
                'title': 'Update Domain Configuration',
                'description': 'Update configuration files with new domain settings',
                'commands': [
                    'python scripts/update_config.py --source old_domain.yaml --target new_domain.yaml',
                    'python scripts/validate_config.py new_domain.yaml'
                ],
                'estimated_time': '30 minutes',
                'risk_level': 'medium'
            })
            step_number += 1
        
        # Schema migrations
        if analysis.get('schema_changes'):
            steps.append({
                'number': step_number,
                'category': 'Database',
                'title': 'Run Schema Migrations',
                'description': 'Apply database schema changes',
                'commands': [
                    'alembic upgrade head',
                    'python scripts/verify_schema.py'
                ],
                'estimated_time': '20 minutes',
                'risk_level': 'high'
            })
            step_number += 1
        
        # Data migrations
        if analysis.get('data_transformations'):
            steps.append({
                'number': step_number,
                'category': 'Data',
                'title': 'Migrate Data',
                'description': 'Transform and migrate existing data to new schema',
                'commands': [
                    'python scripts/migrate_data.py --batch-size 1000',
                    'python scripts/validate_data_migration.py'
                ],
                'estimated_time': f"{analysis['estimated_data_migration_time']} minutes",
                'risk_level': 'high'
            })
            step_number += 1
        
        # Code generation
        steps.append({
            'number': step_number,
            'category': 'Code Generation',
            'title': 'Generate New Components',
            'description': 'Generate new models, schemas, and components',
            'commands': [
                'python -m app.core.template_generator generate --config new_domain.yaml',
                'python -m app.core.component_generator generate-frontend --config new_domain.yaml'
            ],
            'estimated_time': '10 minutes',
            'risk_level': 'low'
        })
        step_number += 1
        
        # Testing
        steps.append({
            'number': step_number,
            'category': 'Testing',
            'title': 'Run Comprehensive Tests',
            'description': 'Execute all generated tests and manual verification',
            'commands': [
                'pytest tests/ -v --cov=app',
                'npm test --watchAll=false',
                'python scripts/integration_test.py'
            ],
            'estimated_time': '45 minutes',
            'risk_level': 'low'
        })
        step_number += 1
        
        # Deployment
        steps.append({
            'number': step_number,
            'category': 'Deployment',
            'title': 'Deploy Updated Application',
            'description': 'Deploy the adapted application to staging/production',
            'commands': [
                'docker-compose build',
                'docker-compose up -d',
                'python scripts/health_check.py'
            ],
            'estimated_time': '30 minutes',
            'risk_level': 'medium'
        })
        
        return steps
```

#### **Alembic Migration Template** (`templates/migration/alembic_migration.py.j2`)
```python
"""{{ migration_name }}

Migration from {{ source_domain }} to {{ target_domain }}
Generated on: {{ timestamp }}

Revision ID: {{ timestamp }}_{{ migration_name | lower | replace(' ', '_') }}
Revises: 
Create Date: {{ timestamp }}

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '{{ timestamp }}_{{ migration_name | lower | replace(" ", "_") }}'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade operations for {{ target_domain }} domain"""
    
    {% for operation in upgrade_operations %}
    {% if operation.operation == 'create_table' %}
    # Create {{ operation.table_name }} table
    op.create_table('{{ operation.table_name }}',
        {% for column in operation.columns %}
        sa.Column('{{ column.name }}', {{ column.type }}{% if column.nullable is defined %}, nullable={{ column.nullable }}{% endif %}{% if column.default is defined %}, default={{ column.default }}{% endif %}),
        {% endfor %}
        {% for constraint in operation.constraints %}
        {% if constraint.type == 'primary_key' %}
        sa.PrimaryKeyConstraint({% for col in constraint.columns %}'{{ col }}'{% if not loop.last %}, {% endif %}{% endfor %}),
        {% elif constraint.type == 'foreign_key' %}
        sa.ForeignKeyConstraint(['{{ constraint.column }}'], ['{{ constraint.target_table }}.{{ constraint.target_column }}'], ),
        {% elif constraint.type == 'unique' %}
        sa.UniqueConstraint({% for col in constraint.columns %}'{{ col }}'{% if not loop.last %}, {% endif %}{% endfor %}),
        {% endif %}
        {% endfor %}
    )
    
    {% elif operation.operation == 'drop_table' %}
    # Drop {{ operation.table_name }} table
    op.drop_table('{{ operation.table_name }}')
    
    {% elif operation.operation == 'add_column' %}
    # Add {{ operation.column.name }} column to {{ operation.table_name }}
    op.add_column('{{ operation.table_name }}', 
                  sa.Column('{{ operation.column.name }}', {{ operation.column.type }}{% if operation.column.nullable is defined %}, nullable={{ operation.column.nullable }}{% endif %}{% if operation.column.default is defined %}, default={{ operation.column.default }}{% endif %}))
    
    {% elif operation.operation == 'drop_column' %}
    # Drop {{ operation.column_name }} column from {{ operation.table_name }}
    op.drop_column('{{ operation.table_name }}', '{{ operation.column_name }}')
    
    {% elif operation.operation == 'alter_column' %}
    # Alter {{ operation.column_name }} column in {{ operation.table_name }}
    {% for change in operation.changes %}
    {% if change.type == 'type_change' %}
    op.alter_column('{{ operation.table_name }}', '{{ operation.column_name }}',
                    type_={{ change.new_type }},
                    existing_type={{ change.old_type }})
    {% elif change.type == 'nullable_change' %}
    op.alter_column('{{ operation.table_name }}', '{{ operation.column_name }}',
                    nullable={{ change.new_nullable }},
                    existing_nullable={{ change.old_nullable }})
    {% elif change.type == 'default_change' %}
    op.alter_column('{{ operation.table_name }}', '{{ operation.column_name }}',
                    server_default={{ change.new_default }},
                    existing_server_default={{ change.old_default }})
    {% endif %}
    {% endfor %}
    {% endif %}
    
    {% endfor %}
    
    # Custom migration logic
    {% if changes_summary.custom_migrations %}
    {% for custom_migration in changes_summary.custom_migrations %}
    # {{ custom_migration.description }}
    connection = op.get_bind()
    connection.execute(sa.text("""
        {{ custom_migration.sql }}
    """))
    {% endfor %}
    {% endif %}

def downgrade():
    """Downgrade operations to revert to {{ source_domain }} domain"""
    
    {% for operation in downgrade_operations %}
    {% if operation.operation == 'create_table' %}
    # Recreate {{ operation.table_name }} table
    op.create_table('{{ operation.table_name }}',
        {% for column in operation.columns %}
        sa.Column('{{ column.name }}', {{ column.type }}{% if column.nullable is defined %}, nullable={{ column.nullable }}{% endif %}{% if column.default is defined %}, default={{ column.default }}{% endif %}),
        {% endfor %}
    )
    
    {% elif operation.operation == 'drop_table' %}
    # Drop {{ operation.table_name }} table
    op.drop_table('{{ operation.table_name }}')
    
    {% elif operation.operation == 'add_column' %}
    # Add {{ operation.column.name }} column to {{ operation.table_name }}
    op.add_column('{{ operation.table_name }}', 
                  sa.Column('{{ operation.column.name }}', {{ operation.column.type }}{% if operation.column.nullable is defined %}, nullable={{ operation.column.nullable }}{% endif %}))
    
    {% elif operation.operation == 'drop_column' %}
    # Drop {{ operation.column_name }} column from {{ operation.table_name }}
    op.drop_column('{{ operation.table_name }}', '{{ operation.column_name }}')
    
    {% elif operation.note %}
    # {{ operation.note }}
    pass
    {% endif %}
    
    {% endfor %}
```

#### **Data Migration Template** (`templates/migration/data_migration.py.j2`)
```python
"""
Data Migration Script: {{ source_domain }} → {{ target_domain }}
Migration Strategy: {{ migration_strategy }}
Generated: {{ generated_date }}
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, func
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataMigrator:
    """Handle data migration between domain configurations"""
    
    def __init__(self, database_url: str, batch_size: int = 1000):
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.batch_size = batch_size
        self.migration_log = []
    
    async def migrate_all_data(self) -> Dict[str, Any]:
        """Execute complete data migration"""
        
        migration_results = {
            'started_at': datetime.now(),
            'migrations': [],
            'total_records_migrated': 0,
            'errors': []
        }
        
        {% if backup_required %}
        # Create backup before migration
        logger.info("Creating data backup...")
        backup_result = await self.create_backup()
        if not backup_result['success']:
            raise Exception(f"Backup failed: {backup_result['error']}")
        {% endif %}
        
        try:
            {% for mapping in data_mappings %}
            logger.info("Migrating {{ mapping.source_entity }} → {{ mapping.target_entity }}")
            result = await self.migrate_entity_data(
                source_entity='{{ mapping.source_entity }}',
                target_entity='{{ mapping.target_entity }}',
                field_mappings={{ mapping.field_mappings | tojson }},
                transformations={{ mapping.transformations | tojson }}
            )
            migration_results['migrations'].append(result)
            migration_results['total_records_migrated'] += result['records_migrated']
            {% endfor %}
            
            # Run validation checks
            logger.info("Running validation checks...")
            validation_results = await self.run_validation_checks()
            migration_results['validation'] = validation_results
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            migration_results['errors'].append(str(e))
            
            {% if backup_required %}
            # Restore from backup on failure
            logger.info("Restoring from backup due to migration failure...")
            await self.restore_from_backup(backup_result['backup_file'])
            {% endif %}
            
            raise
        
        migration_results['completed_at'] = datetime.now()
        migration_results['duration'] = (
            migration_results['completed_at'] - migration_results['started_at']
        ).total_seconds()
        
        return migration_results
    
    async def migrate_entity_data(self, 
                                source_entity: str,
                                target_entity: str,
                                field_mappings: Dict[str, str],
                                transformations: List[Dict]) -> Dict[str, Any]:
        """Migrate data for a single entity"""
        
        async with self.async_session() as session:
            # Count total records to migrate
            count_query = text(f"SELECT COUNT(*) FROM {source_entity.lower()}")
            result = await session.execute(count_query)
            total_records = result.scalar()
            
            logger.info(f"Migrating {total_records} records from {source_entity} to {target_entity}")
            
            migrated_count = 0
            batch_number = 0
            
            # Process in batches
            while migrated_count < total_records:
                offset = batch_number * self.batch_size
                
                # Fetch batch of source records
                select_fields = ', '.join(field_mappings.keys())
                select_query = text(f"""
                    SELECT {select_fields} 
                    FROM {source_entity.lower()} 
                    ORDER BY id 
                    LIMIT {self.batch_size} OFFSET {offset}
                """)
                
                source_records = await session.execute(select_query)
                batch_records = source_records.fetchall()
                
                if not batch_records:
                    break
                
                # Transform and insert records
                for record in batch_records:
                    transformed_record = self.transform_record(
                        dict(record._mapping), 
                        field_mappings, 
                        transformations
                    )
                    
                    # Insert into target entity
                    await self.insert_transformed_record(
                        session, 
                        target_entity, 
                        transformed_record
                    )
                
                await session.commit()
                migrated_count += len(batch_records)
                batch_number += 1
                
                logger.info(f"Migrated batch {batch_number}: {migrated_count}/{total_records} records")
            
            return {
                'source_entity': source_entity,
                'target_entity': target_entity,
                'records_migrated': migrated_count,
                'batches_processed': batch_number
            }
    
    def transform_record(self, 
                        record: Dict[str, Any],
                        field_mappings: Dict[str, str],
                        transformations: List[Dict]) -> Dict[str, Any]:
        """Transform a single record according to mapping rules"""
        
        transformed = {}
        
        # Apply field mappings
        for source_field, target_field in field_mappings.items():
            if source_field in record:
                transformed[target_field] = record[source_field]
        
        # Apply transformations
        for transformation in transformations:
            field_name = transformation['field']
            transform_type = transformation['type']
            
            if field_name in transformed:
                if transform_type == 'string_case':
                    if transformation['case'] == 'upper':
                        transformed[field_name] = str(transformed[field_name]).upper()
                    elif transformation['case'] == 'lower':
                        transformed[field_name] = str(transformed[field_name]).lower()
                    elif transformation['case'] == 'title':
                        transformed[field_name] = str(transformed[field_name]).title()
                
                elif transform_type == 'date_format':
                    # Handle date format transformations
                    from datetime import datetime
                    if isinstance(transformed[field_name], str):
                        source_format = transformation['source_format']
                        target_format = transformation['target_format']
                        date_obj = datetime.strptime(transformed[field_name], source_format)
                        transformed[field_name] = date_obj.strftime(target_format)
                
                elif transform_type == 'value_mapping':
                    # Handle value mappings
                    value_map = transformation['mapping']
                    if transformed[field_name] in value_map:
                        transformed[field_name] = value_map[transformed[field_name]]
                
                elif transform_type == 'calculation':
                    # Handle calculated fields
                    formula = transformation['formula']
                    # Safely evaluate simple formulas
                    if formula.startswith('value *'):
                        multiplier = float(formula.split('* ')[1])
                        transformed[field_name] = float(transformed[field_name]) * multiplier
        
        return transformed
    
    async def insert_transformed_record(self,
                                      session: AsyncSession,
                                      target_entity: str,
                                      record: Dict[str, Any]):
        """Insert a transformed record into the target entity"""
        
        fields = ', '.join(record.keys())
        placeholders = ', '.join([f":{key}" for key in record.keys()])
        
        insert_query = text(f"""
            INSERT INTO {target_entity.lower()} ({fields})
            VALUES ({placeholders})
        """)
        
        await session.execute(insert_query, record)
    
    async def run_validation_checks(self) -> Dict[str, Any]:
        """Run validation checks on migrated data"""
        
        validation_results = {
            'checks_passed': 0,
            'checks_failed': 0,
            'details': []
        }
        
        async with self.async_session() as session:
            {% for check in validation_checks %}
            # {{ check.description }}
            try:
                result = await session.execute(text("""
                    {{ check.sql }}
                """))
                
                check_result = result.scalar()
                expected = {{ check.expected_value }}
                
                if check_result == expected:
                    validation_results['checks_passed'] += 1
                    validation_results['details'].append({
                        'check': '{{ check.name }}',
                        'status': 'passed',
                        'result': check_result,
                        'expected': expected
                    })
                else:
                    validation_results['checks_failed'] += 1
                    validation_results['details'].append({
                        'check': '{{ check.name }}',
                        'status': 'failed',
                        'result': check_result,
                        'expected': expected,
                        'error': 'Value mismatch'
                    })
            
            except Exception as e:
                validation_results['checks_failed'] += 1
                validation_results['details'].append({
                    'check': '{{ check.name }}',
                    'status': 'error',
                    'error': str(e)
                })
            {% endfor %}
        
        return validation_results
    
    {% if backup_required %}
    async def create_backup(self) -> Dict[str, Any]:
        """Create database backup before migration"""
        import subprocess
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"migration_backup_{timestamp}.sql"
        
        try:
            # This would need to be customized based on database type
            result = subprocess.run([
                'pg_dump', 
                '--no-password',
                '--clean',
                '--create',
                '--format=custom',
                '--file', backup_file,
                'your_database_url'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {'success': True, 'backup_file': backup_file}
            else:
                return {'success': False, 'error': result.stderr}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def restore_from_backup(self, backup_file: str):
        """Restore database from backup"""
        import subprocess
        
        try:
            result = subprocess.run([
                'pg_restore',
                '--no-password',
                '--clean',
                '--create',
                '--dbname', 'your_database_url',
                backup_file
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Restore failed: {result.stderr}")
        
        except Exception as e:
            logger.error(f"Backup restore failed: {str(e)}")
            raise
    {% endif %}

async def main():
    """Main migration execution"""
    
    migrator = DataMigrator(
        database_url="your_database_url_here",
        batch_size=1000
    )
    
    try:
        results = await migrator.migrate_all_data()
        
        print("\n" + "="*50)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Total records migrated: {results['total_records_migrated']}")
        print(f"Duration: {results['duration']:.2f} seconds")
        print(f"Validation checks passed: {results['validation']['checks_passed']}")
        print(f"Validation checks failed: {results['validation']['checks_failed']}")
        
        if results['validation']['checks_failed'] > 0:
            print("\nFAILED VALIDATION CHECKS:")
            for detail in results['validation']['details']:
                if detail['status'] != 'passed':
                    print(f"- {detail['check']}: {detail.get('error', 'Failed')}")
    
    except Exception as e:
        print(f"\nMIGRATION FAILED: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
```

#### **Adaptation Guide Template** (`templates/migration/adaptation_guide.md.j2`)
```markdown
# 🔄 Domain Adaptation Guide
## From {{ source_domain }} to {{ target_domain }}

**Generated on:** {{ generated_date }}  
**Complexity Level:** {{ complexity_level | title }}  
**Estimated Total Time:** {{ effort_estimation.total_hours }} hours

---

## 📋 Overview

This guide provides step-by-step instructions for adapting your {{ source_domain }} application to the {{ target_domain }} domain. The migration has been analyzed and categorized by complexity and risk level.

### Migration Summary

| Category | Changes | Estimated Time | Risk Level |
|----------|---------|----------------|------------|
{% for category, info in adaptation_analysis.summary.items() %}
| {{ category | title }} | {{ info.changes }} | {{ info.time }} | {{ info.risk }} |
{% endfor %}

### Prerequisites

- [ ] Full system backup completed
- [ ] Development environment ready
- [ ] Database access confirmed
- [ ] All team members notified of migration
- [ ] Rollback plan prepared

---

## 🛠️ Step-by-Step Migration Process

{% for step in adaptation_steps %}
### Step {{ step.number }}: {{ step.title }}
**Category:** {{ step.category }}  
**Estimated Time:** {{ step.estimated_time }}  
**Risk Level:** {{ step.risk_level | upper }}

{{ step.description }}

{% if step.commands %}
**Commands to Execute:**
```bash
{% for command in step.commands %}
{{ command }}
{% endfor %}
```
{% endif %}

{% if step.risk_level == 'high' %}
⚠️ **High Risk Step** - Ensure backup is available before proceeding.
{% endif %}

---
{% endfor %}

## ✅ Post-Migration Testing Checklist

{% for test_category, tests in testing_checklist.items() %}
### {{ test_category | title }} Tests

{% for test in tests %}
- [ ] **{{ test.name }}**: {{ test.description }}
  - Command: `{{ test.command }}`
  - Expected: {{ test.expected }}
{% endfor %}
{% endfor %}

## 🔧 Configuration Changes

### Environment Variables
{% if adaptation_analysis.config_changes.environment_variables %}
Update the following environment variables:

| Variable | Old Value | New Value | Notes |
|----------|-----------|-----------|-------|
{% for var in adaptation_analysis.config_changes.environment_variables %}
| `{{ var.name }}` | {{ var.old_value }} | {{ var.new_value }} | {{ var.notes }} |
{% endfor %}
{% else %}
No environment variable changes required.
{% endif %}

### Configuration Files
{% if adaptation_analysis.config_changes.files %}
Update the following configuration files:

{% for file in adaptation_analysis.config_changes.files %}
**{{ file.path }}**
```{{ file.format }}
{{ file.content }}
```
{% endfor %}
{% else %}
No configuration file changes required.
{% endif %}

## 📊 Database Schema Changes

{% if adaptation_analysis.schema_changes %}
### New Tables
{% for table in adaptation_analysis.schema_changes.new_tables %}
- `{{ table.name }}` - {{ table.description }}
{% endfor %}

### Modified Tables
{% for table in adaptation_analysis.schema_changes.modified_tables %}
- `{{ table.name }}` - {{ table.modifications | join(', ') }}
{% endfor %}

### Removed Tables
{% for table in adaptation_analysis.schema_changes.removed_tables %}
- `{{ table }}` - ⚠️ **Data will be lost**
{% endfor %}
{% else %}
No database schema changes required.
{% endif %}

## 🔄 Data Migration Details

{% if adaptation_analysis.data_transformations %}
### Data Transformations Required

{% for transformation in adaptation_analysis.data_transformations %}
**{{ transformation.entity }}**
- **Type:** {{ transformation.type }}
- **Description:** {{ transformation.description }}
- **Risk:** {{ transformation.risk }}
- **Estimated Records:** {{ transformation.estimated_records }}

{% if transformation.field_mappings %}
Field Mappings:
{% for mapping in transformation.field_mappings %}
- `{{ mapping.source }}` → `{{ mapping.target }}` {% if mapping.transformation %}({{ mapping.transformation }}){% endif %}
{% endfor %}
{% endif %}
{% endfor %}
{% else %}
No data transformations required - direct copy migration.
{% endif %}

## 🚨 Rollback Plan

In case of migration failure, follow these steps to rollback:

1. **Stop the application:**
   ```bash
   docker-compose down
   ```

2. **Restore database backup:**
   ```bash
   pg_restore --clean --create --dbname your_database backup_file.sql
   ```

3. **Restore configuration files:**
   ```bash
   cp -r config_backup_*/ config/
   ```

4. **Restart with original configuration:**
   ```bash
   docker-compose -f docker-compose.original.yml up -d
   ```

## 📞 Support and Troubleshooting

### Common Issues

{% if adaptation_analysis.common_issues %}
{% for issue in adaptation_analysis.common_issues %}
**{{ issue.problem }}**
- **Cause:** {{ issue.cause }}
- **Solution:** {{ issue.solution }}
- **Prevention:** {{ issue.prevention }}
{% endfor %}
{% else %}
No known common issues for this migration path.
{% endif %}

### Getting Help

- Check the application logs: `docker-compose logs -f`
- Review migration logs in `migration_logs/`
- Contact support with migration ID: `{{ effort_estimation.migration_id }}`

---

## 📈 Performance Considerations

### Before Migration
- Current database size: {{ adaptation_analysis.performance.current_db_size }}
- Average response time: {{ adaptation_analysis.performance.current_response_time }}
- Active users: {{ adaptation_analysis.performance.active_users }}

### After Migration (Estimated)
- Expected database size: {{ adaptation_analysis.performance.expected_db_size }}
- Expected response time: {{ adaptation_analysis.performance.expected_response_time }}
- Performance impact: {{ adaptation_analysis.performance.impact }}

---

*Generated by TeamFlow Template System v2.0*  
*Migration Complexity: {{ complexity_level }} | Total Estimated Time: {{ effort_estimation.total_hours }}h*
```

---

*This completes Section 8 and the comprehensive Phase 2 documentation. All sections are now complete with detailed technical specifications for the template extraction and engine design.*