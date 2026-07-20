"""add is_active to users

Revision ID: 20260720_0002
Revises: 20260720_0001
Create Date: 2026-07-20 00:00:00.000000
"""

# ruff: noqa: I001

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260720_0002"
down_revision = "20260720_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("users", "is_active")
