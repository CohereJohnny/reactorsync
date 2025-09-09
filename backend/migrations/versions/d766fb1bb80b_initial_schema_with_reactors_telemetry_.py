"""Initial schema with reactors, telemetry, faults, and knowledge_base

Revision ID: d766fb1bb80b
Revises: 
Create Date: 2025-09-09 16:47:29.592563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'd766fb1bb80b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Create enum types
    reactor_status_enum = postgresql.ENUM('healthy', 'warning', 'unhealthy', name='reactor_status')
    reactor_type_enum = postgresql.ENUM('CANDU', 'SMR', 'PWR', 'BWR', name='reactor_type')
    fault_severity_enum = postgresql.ENUM('yellow', 'red', name='fault_severity')
    
    reactor_status_enum.create(op.get_bind())
    reactor_type_enum.create(op.get_bind())
    fault_severity_enum.create(op.get_bind())
    
    # Create reactors table
    op.create_table('reactors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', reactor_type_enum, nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('status', reactor_status_enum, nullable=False),
        sa.Column('health_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reactors_id'), 'reactors', ['id'], unique=False)
    op.create_index(op.f('ix_reactors_name'), 'reactors', ['name'], unique=True)
    
    # Create telemetry table
    op.create_table('telemetry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('neutron_flux', sa.Float(), nullable=True),
        sa.Column('core_temperature', sa.Float(), nullable=True),
        sa.Column('pressure', sa.Float(), nullable=True),
        sa.Column('vibration', sa.Float(), nullable=True),
        sa.Column('tritium_level', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telemetry_id'), 'telemetry', ['id'], unique=False)
    op.create_index(op.f('ix_telemetry_timestamp'), 'telemetry', ['timestamp'], unique=False)
    op.create_index('ix_telemetry_reactor_timestamp', 'telemetry', ['reactor_id', 'timestamp'], unique=False)
    op.create_index('ix_telemetry_timestamp_reactor', 'telemetry', ['timestamp', 'reactor_id'], unique=False)
    
    # Create faults table
    op.create_table('faults',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=False),
        sa.Column('fault_type', sa.String(length=255), nullable=False),
        sa.Column('severity', fault_severity_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_faults_fault_type'), 'faults', ['fault_type'], unique=False)
    op.create_index(op.f('ix_faults_id'), 'faults', ['id'], unique=False)
    op.create_index(op.f('ix_faults_reactor_id'), 'faults', ['reactor_id'], unique=False)
    op.create_index(op.f('ix_faults_timestamp'), 'faults', ['timestamp'], unique=False)
    
    # Create knowledge_base table
    op.create_table('knowledge_base',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('doc_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_base_document_name'), 'knowledge_base', ['document_name'], unique=False)
    op.create_index(op.f('ix_knowledge_base_id'), 'knowledge_base', ['id'], unique=False)
    
    # Create vector index for similarity search
    op.execute("CREATE INDEX IF NOT EXISTS ix_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops)")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('knowledge_base')
    op.drop_table('faults')
    op.drop_table('telemetry')
    op.drop_table('reactors')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS fault_severity")
    op.execute("DROP TYPE IF EXISTS reactor_type")
    op.execute("DROP TYPE IF EXISTS reactor_status")
    
    # Drop pgvector extension
    op.execute("DROP EXTENSION IF EXISTS vector")
