"""create users table

Revision ID: 20260711_0001
Revises: None
Create Date: 2026-07-11 00:00:00.000000
"""

# ruff: noqa: I001

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260711_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("platform_role", sa.String(length=32), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_platform_role", "users", ["platform_role"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_platform_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
