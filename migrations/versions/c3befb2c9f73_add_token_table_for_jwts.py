from alembic import op
import sqlalchemy as sa

revision = "c3befb2c9f73"
down_revision = "9a556647d355"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "token",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("token", sa.String(length=1024), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("revoked_on", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )


def downgrade():
    op.drop_table("token")

