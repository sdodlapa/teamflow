"""add_template_persistence_models

Revision ID: 20081ebf1fe2
Revises: 21d6fc7a4164
Create Date: 2025-09-24 19:31:53.496561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20081ebf1fe2'
down_revision: Union[str, None] = '21d6fc7a4164'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite doesn't support ENUMs or UUIDs, we'll use String columns and CHECK constraints
    
    # Create templates table
    op.create_table(
        "templates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("domain_config", sa.JSON, nullable=False),
        sa.Column("entities", sa.JSON, nullable=False),
        sa.Column("relationships", sa.JSON, nullable=False),
        sa.Column("version", sa.Integer, nullable=False, default=1),
        sa.Column("status", sa.String(20), nullable=False, default="draft"),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("is_public", sa.Boolean, default=False, nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.CheckConstraint("status IN ('draft', 'published', 'archived')", name="ck_templates_status")
    )
    
    # Create template_versions table
    op.create_table(
        "template_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("template_id", sa.String(36), sa.ForeignKey("templates.id"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("domain_config", sa.JSON, nullable=False),
        sa.Column("entities", sa.JSON, nullable=False),
        sa.Column("relationships", sa.JSON, nullable=False),
        sa.Column("changes", sa.JSON, nullable=True),
        sa.Column("change_description", sa.Text, nullable=True),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False)
    )
    
    # Create template_collaborators table
    op.create_table(
        "template_collaborators",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("template_id", sa.String(36), sa.ForeignKey("templates.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("permissions", sa.String(20), nullable=False, default="read"),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.CheckConstraint("permissions IN ('read', 'write', 'admin')", name="ck_template_collaborators_permissions")
    )
    
    # Create template_collaboration_history table
    op.create_table(
        "template_collaboration_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("template_id", sa.String(36), sa.ForeignKey("templates.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("action_data", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.CheckConstraint("action IN ('join', 'leave', 'edit', 'comment', 'save', 'publish', 'archive')", name="ck_template_collaboration_history_action")
    )
    
    # Create indexes
    op.create_index("ix_templates_status", "templates", ["status"])
    op.create_index("ix_templates_is_public", "templates", ["is_public"])
    op.create_index("ix_templates_organization_id", "templates", ["organization_id"])
    
    op.create_index("ix_template_versions_template_id", "template_versions", ["template_id"])
    
    op.create_index("ix_template_collaborators_template_id", "template_collaborators", ["template_id"])
    op.create_index("ix_template_collaborators_user_id", "template_collaborators", ["user_id"])
    
    op.create_index("ix_template_collaboration_history_template_id", 
                   "template_collaboration_history", ["template_id"])
    op.create_index("ix_template_collaboration_history_user_id", 
                   "template_collaboration_history", ["user_id"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_template_collaboration_history_user_id", "template_collaboration_history")
    op.drop_index("ix_template_collaboration_history_template_id", "template_collaboration_history")
    op.drop_index("ix_template_collaborators_user_id", "template_collaborators")
    op.drop_index("ix_template_collaborators_template_id", "template_collaborators")
    op.drop_index("ix_template_versions_template_id", "template_versions")
    op.drop_index("ix_templates_organization_id", "templates")
    op.drop_index("ix_templates_is_public", "templates")
    op.drop_index("ix_templates_status", "templates")
    
    # Drop tables
    op.drop_table("template_collaboration_history")
    op.drop_table("template_collaborators")
    op.drop_table("template_versions")
    op.drop_table("templates")
