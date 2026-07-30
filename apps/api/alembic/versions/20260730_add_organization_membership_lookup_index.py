"""Add organization membership lookup index.

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-07-30 00:00:00.000000
"""

from alembic import op

revision = "2b3c4d5e6f7a"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_organization_memberships_organization_id_user_id",
        "organization_memberships",
        ["organization_id", "user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organization_memberships_organization_id_user_id",
        table_name="organization_memberships",
    )
