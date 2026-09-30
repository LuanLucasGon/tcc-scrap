"""create questionfile

Revision ID: 8b171f542021
Revises: b74ff08269d0
Create Date: 2026-09-05 02:57:12.751703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b171f542021'
down_revision: Union[str, Sequence[str], None] = 'b74ff08269d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'questionfile',
        sa.Column(
            'id',
            sa.UUID(),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('question_number_id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('content', sa.LargeBinary(), nullable=False),
        sa.Column(
            'active', sa.Boolean(), server_default=sa.text('true'), nullable=False
        ),
        sa.Column(
            'deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'question_number_id',
            'url',
            name='uq_questionfile_question_number_id_url',
        ),
    )
    op.create_index(
        op.f('ix_questionfile_question_number_id'),
        'questionfile',
        ['question_number_id'],
    )
    op.create_index(op.f('ix_questionfile_url'), 'questionfile', ['url'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_questionfile_url'), table_name='questionfile')
    op.drop_index(
        op.f('ix_questionfile_question_number_id'), table_name='questionfile'
    )
    op.drop_table('questionfile')
