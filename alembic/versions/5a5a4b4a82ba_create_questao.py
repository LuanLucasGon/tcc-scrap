"""create questao

Revision ID: 5a5a4b4a82ba
Revises:
Create Date: 2026-08-27 01:21:26.931090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5a5a4b4a82ba'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'questao',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('topics', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('year', sa.String(), nullable=True),
        sa.Column('exam_board', sa.String(), nullable=True),
        sa.Column('organization', sa.String(), nullable=True),
        sa.Column('exam_title', sa.String(), nullable=True),
        sa.Column('exam_url', sa.String(), nullable=True),
        sa.Column('associated_text', sa.Text(), nullable=True),
        sa.Column('enunciation', sa.Text(), nullable=True),
        sa.Column('alternatives', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('excluido', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_questao_question_id'), 'questao', ['question_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_questao_question_id'), table_name='questao')
    op.drop_table('questao')
