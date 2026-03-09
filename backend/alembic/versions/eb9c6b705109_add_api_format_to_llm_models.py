"""add_api_format_to_llm_models

Revision ID: eb9c6b705109
Revises: add_agent_triggers
Create Date: 2026-03-09 13:42:58.439860
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb9c6b705109'
down_revision: Union[str, None] = 'add_agent_triggers'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('llm_models', sa.Column('api_format', sa.String(20), nullable=False, server_default='openai'))


def downgrade() -> None:
    op.drop_column('llm_models', 'api_format')
