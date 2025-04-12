"""add chat history table

Revision ID: add_chat_history_table
Revises: initial
Create Date: 2024-04-10 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_chat_history_table'
down_revision = 'initial'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'chat_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chatbot_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_history_id'), 'chat_history', ['id'], unique=False)
    op.create_index(op.f('ix_chat_history_chatbot_id'), 'chat_history', ['chatbot_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_chat_history_chatbot_id'), table_name='chat_history')
    op.drop_index(op.f('ix_chat_history_id'), table_name='chat_history')
    op.drop_table('chat_history') 