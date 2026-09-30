"""create question and subject

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
        'subject',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_subject_name'), 'subject', ['name'], unique=True)

    op.create_table(
        'question',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.Column('subject_id', sa.UUID(), nullable=False),
        sa.Column('topics', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('year', sa.String(), nullable=True),
        sa.Column('exam_board', sa.String(), nullable=True),
        sa.Column('organization', sa.String(), nullable=True),
        sa.Column('exam_title', sa.String(), nullable=True),
        sa.Column('exam_url', sa.String(), nullable=True),
        sa.Column('associated_text', sa.Text(), nullable=True),
        sa.Column('enunciation', sa.Text(), nullable=True),
        sa.Column('alternatives', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_question_question_id'), 'question', ['question_id'], unique=True)
    op.create_index(op.f('ix_question_subject_id'), 'question', ['subject_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_question_subject_id'), table_name='question')
    op.drop_index(op.f('ix_question_question_id'), table_name='question')
    op.drop_table('question')
    op.drop_index(op.f('ix_subject_name'), table_name='subject')
    op.drop_table('subject')
