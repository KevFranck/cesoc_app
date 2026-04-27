"""rename users external_id to email

Revision ID: 20260424_email
Revises:
Create Date: 2026-04-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260424_email"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    with op.batch_alter_table("users") as batch_op:
        if "external_id" in columns and "email" not in columns:
            batch_op.alter_column("external_id", new_column_name="email", existing_type=sa.String(length=50))
        if "password_hash" not in columns:
            batch_op.add_column(sa.Column("password_hash", sa.String(length=255), nullable=True))

    bind.execute(sa.text("UPDATE users SET password_hash = '' WHERE password_hash IS NULL"))

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("email", existing_type=sa.String(length=50), type_=sa.String(length=255), existing_nullable=False)
        batch_op.alter_column("password_hash", existing_type=sa.String(length=255), nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    with op.batch_alter_table("users") as batch_op:
        if "password_hash" in columns:
            batch_op.drop_column("password_hash")
        if "email" in columns and "external_id" not in columns:
            batch_op.alter_column("email", new_column_name="external_id", existing_type=sa.String(length=255))
