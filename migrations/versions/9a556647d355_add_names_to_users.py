"""Add names to users

Revision ID: 9a556647d355
Revises: 7de94907eadc
Create Date: 2018-11-25 20:23:05.740667

"""
from alembic import op
import sqlalchemy as sa

revision = "9a556647d355"
down_revision = "7de94907eadc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("firstname", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("lastname", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("users", "lastname")
    op.drop_column("users", "firstname")

