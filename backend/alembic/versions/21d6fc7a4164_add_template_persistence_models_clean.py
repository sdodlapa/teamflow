"""Add template persistence models (clean)

Revision ID: 21d6fc7a4164_clean
Revises: 21d6fc7a4164
Create Date: 2025-01-06 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "21d6fc7a4164_clean"
down_revision: Union[str, None] = "21d6fc7a4164"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Note: This is a clean version of the template persistence migration
    # The current database already has the template tables from previous migration
    # This is just for documentation purposes
    pass


def downgrade() -> None:
    # This would normally drop the template tables, but since this is a
    # documentation migration, we'll leave it empty
    pass