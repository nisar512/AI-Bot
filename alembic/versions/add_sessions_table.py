"""add sessions table and update chat_history

Revision ID: add_sessions_table
Revises: add_chat_history_table
Create Date: 2024-04-10 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_sessions_table'
down_revision = 'add_chat_history_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('chatbot_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_id'), 'sessions', ['id'], unique=False)
    op.create_index(op.f('ix_sessions_chatbot_id'), 'sessions', ['chatbot_id'], unique=False)

    # Update chat_history table
    op.add_column('chat_history', sa.Column('session_id', sa.String(), nullable=False))
    op.create_foreign_key('fk_chat_history_session_id', 'chat_history', 'sessions', ['session_id'], ['id'])
    op.create_index(op.f('ix_chat_history_session_id'), 'chat_history', ['session_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_chat_history_session_id'), table_name='chat_history')
    op.drop_constraint('fk_chat_history_session_id', 'chat_history', type_='foreignkey')
    op.drop_column('chat_history', 'session_id')
    
    op.drop_index(op.f('ix_sessions_chatbot_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_id'), table_name='sessions')
    op.drop_table('sessions') 