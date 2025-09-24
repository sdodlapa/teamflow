"""Day 3 Part 1: Add analytics tables without modifying existing tables

Revision ID: day_3_part_1
Revises: 0349b8824f35
Create Date: 2025-01-14 10:57:16.186796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models.base import JSONField

# revision identifiers, used by Alembic.
revision: str = 'day_3_part_1'
down_revision: Union[str, None] = '0349b8824f35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new analytics tables
    op.create_table('bottleneck_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_template_generated', sa.Boolean(), nullable=False),
        sa.Column('template_version', sa.String(length=50), nullable=True),
        sa.Column('domain_config', JSONField(), nullable=True),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('scope_identifier', sa.String(length=100), nullable=False),
        sa.Column('analysis_period_start', sa.DateTime(), nullable=False),
        sa.Column('analysis_period_end', sa.DateTime(), nullable=False),
        sa.Column('bottleneck_type', sa.Enum('RESOURCE', 'DEPENDENCY', 'APPROVAL', 'TECHNICAL', 'COMMUNICATION', name='bottlenecktype'), nullable=False),
        sa.Column('bottleneck_location', sa.String(length=200), nullable=False),
        sa.Column('severity_score', sa.Float(), nullable=False),
        sa.Column('affected_tasks_count', sa.Integer(), nullable=True),
        sa.Column('avg_delay_hours', sa.Float(), nullable=True),
        sa.Column('productivity_impact', sa.Float(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('suggested_solutions', sa.JSON(), nullable=True),
        sa.Column('resolution_status', sa.String(length=50), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('validation_status', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bottleneck_analyses_id'), 'bottleneck_analyses', ['id'], unique=False)
    op.create_index(op.f('ix_bottleneck_analyses_scope_identifier'), 'bottleneck_analyses', ['scope_identifier'], unique=False)
    op.create_index(op.f('ix_bottleneck_analyses_uuid'), 'bottleneck_analyses', ['uuid'], unique=False)

    op.create_table('team_performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_template_generated', sa.Boolean(), nullable=False),
        sa.Column('template_version', sa.String(length=50), nullable=True),
        sa.Column('domain_config', JSONField(), nullable=True),
        sa.Column('team_identifier', sa.String(length=100), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('total_tasks_completed', sa.Integer(), nullable=False),
        sa.Column('avg_completion_time_hours', sa.Float(), nullable=True),
        sa.Column('velocity_points', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('productivity_score', sa.Float(), nullable=True),
        sa.Column('collaboration_score', sa.Float(), nullable=True),
        sa.Column('burnout_risk_score', sa.Float(), nullable=True),
        sa.Column('skill_coverage_score', sa.Float(), nullable=True),
        sa.Column('workload_balance_score', sa.Float(), nullable=True),
        sa.Column('bottleneck_count', sa.Integer(), nullable=True),
        sa.Column('improvement_suggestions', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_team_performance_metrics_id'), 'team_performance_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_team_performance_metrics_period_end'), 'team_performance_metrics', ['period_end'], unique=False)
    op.create_index(op.f('ix_team_performance_metrics_period_start'), 'team_performance_metrics', ['period_start'], unique=False)
    op.create_index(op.f('ix_team_performance_metrics_team_identifier'), 'team_performance_metrics', ['team_identifier'], unique=False)
    op.create_index(op.f('ix_team_performance_metrics_uuid'), 'team_performance_metrics', ['uuid'], unique=False)

    op.create_table('project_health_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_template_generated', sa.Boolean(), nullable=False),
        sa.Column('template_version', sa.String(length=50), nullable=True),
        sa.Column('domain_config', JSONField(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('health_score', sa.Float(), nullable=False),
        sa.Column('completion_percentage', sa.Float(), nullable=False),
        sa.Column('on_schedule_score', sa.Float(), nullable=False),
        sa.Column('budget_health_score', sa.Float(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('team_satisfaction_score', sa.Float(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('velocity_trend', sa.Float(), nullable=True),
        sa.Column('blockers_count', sa.Integer(), nullable=True),
        sa.Column('overdue_tasks_count', sa.Integer(), nullable=True),
        sa.Column('critical_issues_count', sa.Integer(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_health_metrics_id'), 'project_health_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_project_health_metrics_project_id'), 'project_health_metrics', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_health_metrics_uuid'), 'project_health_metrics', ['uuid'], unique=False)

    op.create_table('workflow_execution_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_template_generated', sa.Boolean(), nullable=False),
        sa.Column('template_version', sa.String(length=50), nullable=True),
        sa.Column('domain_config', JSONField(), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('workflow_template_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='workflowstatus'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('total_steps', sa.Integer(), nullable=False),
        sa.Column('completed_steps', sa.Integer(), nullable=False),
        sa.Column('failed_steps', sa.Integer(), nullable=False),
        sa.Column('execution_time_seconds', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_context', sa.JSON(), nullable=True),
        sa.Column('trigger_event', sa.String(length=100), nullable=True),
        sa.Column('triggered_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['triggered_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workflow_template_id'], ['workflow_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_execution_analytics_entity_id'), 'workflow_execution_analytics', ['entity_id'], unique=False)
    op.create_index(op.f('ix_workflow_execution_analytics_id'), 'workflow_execution_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_workflow_execution_analytics_uuid'), 'workflow_execution_analytics', ['uuid'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_workflow_execution_analytics_uuid'), table_name='workflow_execution_analytics')
    op.drop_index(op.f('ix_workflow_execution_analytics_id'), table_name='workflow_execution_analytics')
    op.drop_index(op.f('ix_workflow_execution_analytics_entity_id'), table_name='workflow_execution_analytics')
    op.drop_table('workflow_execution_analytics')
    
    op.drop_index(op.f('ix_project_health_metrics_uuid'), table_name='project_health_metrics')
    op.drop_index(op.f('ix_project_health_metrics_project_id'), table_name='project_health_metrics')
    op.drop_index(op.f('ix_project_health_metrics_id'), table_name='project_health_metrics')
    op.drop_table('project_health_metrics')
    
    op.drop_index(op.f('ix_team_performance_metrics_uuid'), table_name='team_performance_metrics')
    op.drop_index(op.f('ix_team_performance_metrics_team_identifier'), table_name='team_performance_metrics')
    op.drop_index(op.f('ix_team_performance_metrics_period_start'), table_name='team_performance_metrics')
    op.drop_index(op.f('ix_team_performance_metrics_period_end'), table_name='team_performance_metrics')
    op.drop_index(op.f('ix_team_performance_metrics_id'), table_name='team_performance_metrics')
    op.drop_table('team_performance_metrics')
    
    op.drop_index(op.f('ix_bottleneck_analyses_uuid'), table_name='bottleneck_analyses')
    op.drop_index(op.f('ix_bottleneck_analyses_scope_identifier'), table_name='bottleneck_analyses')
    op.drop_index(op.f('ix_bottleneck_analyses_id'), table_name='bottleneck_analyses')
    op.drop_table('bottleneck_analyses')