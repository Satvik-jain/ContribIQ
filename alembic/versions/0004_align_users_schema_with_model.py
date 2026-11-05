"""align users table with the User model

- email: replace the separate non-unique index + unique constraint with the
  single unique index (ix_users_email) that the model's
  ``unique=True, index=True`` produces
- created_at / updated_at: timezone-aware, with a server-side default of now()

Existing rows are preserved. Naive timestamps are interpreted as UTC when
converted to timezone-aware ones.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-06
"""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    # Redundant pair -> one unique index
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_index("ix_users_email", table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    for column in ("created_at", "updated_at"):
        op.alter_column(
            "users",
            column,
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=True,
            server_default=sa.func.now(),
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )


def downgrade():
    for column in ("created_at", "updated_at"):
        op.alter_column(
            "users",
            column,
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=True,
            server_default=None,
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )

    op.drop_index("ix_users_email", table_name="users")
    op.create_index("ix_users_email", "users", ["email"])
    op.create_unique_constraint("uq_users_email", "users", ["email"])
