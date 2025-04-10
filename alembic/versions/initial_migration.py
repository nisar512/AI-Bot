"""initial migration

Revision ID: initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop existing tables if they exist
    op.execute('DROP TABLE IF EXISTS chatbots CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create chatbots table
    op.create_table(
        'chatbots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('index_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chatbots_id'), 'chatbots', ['id'], unique=False)
    op.create_index(op.f('ix_chatbots_user_id'), 'chatbots', ['user_id'], unique=False)

def downgrade() -> None:
    # Drop chatbots table first (due to foreign key constraint)
    op.drop_index(op.f('ix_chatbots_user_id'), table_name='chatbots')
    op.drop_index(op.f('ix_chatbots_id'), table_name='chatbots')
    op.drop_table('chatbots')

    # Drop users table
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users') 