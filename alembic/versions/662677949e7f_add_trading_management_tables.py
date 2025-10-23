"""Add trading management tables

Revision ID: 662677949e7f
Revises: 0001
Create Date: 2025-10-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '662677949e7f'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to trades table
    op.add_column('trades', sa.Column('allocated_fund', sa.Numeric(40, 8), nullable=True))
    op.add_column('trades', sa.Column('risk_amount', sa.Numeric(40, 8), nullable=True))
    op.add_column('trades', sa.Column('stop_loss_triggered', sa.Boolean(), default=False))
    op.add_column('trades', sa.Column('closed_by_user', sa.Boolean(), default=False))
    
    # Create allowed_instruments table
    op.create_table(
        'allowed_instruments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(), nullable=False, unique=True),
        sa.Column('value', sa.String(), nullable=True),
        sa.Column('value_type', sa.String(), default='string'),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create fund_allocations table
    op.create_table(
        'fund_allocations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('allocated_amount', sa.Numeric(40, 8), nullable=False),
        sa.Column('used_amount', sa.Numeric(40, 8), default=0),
        sa.Column('total_loss', sa.Numeric(40, 8), default=0),
        sa.Column('risk_limit', sa.Numeric(40, 8), nullable=False),
        sa.Column('trading_enabled', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Insert default system settings
    op.execute("""
        INSERT INTO system_settings (key, value, value_type, description) VALUES
        ('trading_enabled', 'true', 'boolean', 'Master switch for all trading'),
        ('total_fund', '100000', 'float', 'Total available fund for trading'),
        ('risk_per_instrument', '0.02', 'float', 'Risk percentage per instrument (2%)'),
        ('auto_stop_loss', 'true', 'boolean', 'Auto-stop trading when 2% loss reached')
    """)


def downgrade():
    # Remove columns from trades table
    op.drop_column('trades', 'closed_by_user')
    op.drop_column('trades', 'stop_loss_triggered')
    op.drop_column('trades', 'risk_amount')
    op.drop_column('trades', 'allocated_fund')
    
    # Drop tables
    op.drop_table('fund_allocations')
    op.drop_table('system_settings')
    op.drop_table('allowed_instruments')
