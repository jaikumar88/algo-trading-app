"""initial migration

Create all tables from models metadata.
"""
from alembic import op
import sqlalchemy as sa
import sys
import os
sys.path.append(os.getcwd())
from models import Base

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    # create all tables as defined by SQLAlchemy models
    Base.metadata.create_all(bind=bind)


def downgrade():
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
