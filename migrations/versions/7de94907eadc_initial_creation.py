from alembic import op
import sqlalchemy as sa

revision = "7de94907eadc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "invitation_group",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("friendly_name", sa.String(length=255), nullable=False),
        sa.Column("group_code", sa.String(length=16), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("friendly_name"),
    )
    op.create_table(
        "invitation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "invitation_type",
            sa.Enum("HOUSE", "WEEKEND", "DAY", name="invitationtype"),
            nullable=False,
        ),
        sa.Column(
            "response",
            sa.Enum("NO_RESPONSE", "CONFIRMED", "DECLINED", name="responsetype"),
            nullable=False,
        ),
        sa.Column("requirements", sa.String(length=1000), nullable=True),
        sa.Column("plus_one", sa.Boolean(), nullable=False),
        sa.Column("plus_one_name", sa.String(length=256), nullable=True),
        sa.Column("locked", sa.Boolean(), nullable=False),
        sa.Column("invitation_group_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["invitation_group_id"], ["invitation_group.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("registered_on", sa.DateTime(), nullable=False),
        sa.Column("admin", sa.Boolean(), nullable=False),
        sa.Column("password_hash", sa.String(length=100), nullable=True),
        sa.Column("invitation_group_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["invitation_group_id"], ["invitation_group.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )


def downgrade():
    op.drop_table("user")
    op.drop_table("invitation")
    op.drop_table("invitation_group")
