"""initial migration

Revision ID: 0001
Revises:
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # buyer_requests
    # ---------------------------------------------------------------
    op.create_table(
        "buyer_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column(
            "source",
            sa.Enum("specs", "image", name="requestsource"),
            nullable=False,
        ),
        sa.Column(
            "intent",
            sa.Enum("search_for_me", "browse_myself", name="requestintent"),
            nullable=True,
        ),
        sa.Column("property_type", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("budget_min", sa.Integer(), nullable=True),
        sa.Column("budget_max", sa.Integer(), nullable=True),
        sa.Column("area", sa.Integer(), nullable=True),
        sa.Column("purpose", sa.String(length=50), nullable=True),
        sa.Column("features", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_buyer_requests"),
    )
    op.create_index(
        "ix_buyer_requests_session_id",
        "buyer_requests",
        ["session_id"],
    )

    # ---------------------------------------------------------------
    # properties
    # ---------------------------------------------------------------
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("property_type", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("area", sa.Integer(), nullable=True),
        sa.Column("purpose", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_properties"),
    )

    # ---------------------------------------------------------------
    # request_images
    # ---------------------------------------------------------------
    op.create_table(
        "request_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=255), nullable=False),
        sa.Column("image_type", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["buyer_requests.id"],
            ondelete="CASCADE",
            name="fk_request_images_request_id_buyer_requests",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_request_images"),
    )
    op.create_index(
        "ix_request_images_request_id",
        "request_images",
        ["request_id"],
    )

    # ---------------------------------------------------------------
    # property_images
    # ---------------------------------------------------------------
    op.create_table(
        "property_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=255), nullable=False),
        sa.Column(
            "is_cover",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            ondelete="CASCADE",
            name="fk_property_images_property_id_properties",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_property_images"),
    )
    op.create_index(
        "ix_property_images_property_id",
        "property_images",
        ["property_id"],
    )


def downgrade() -> None:
    # property_images
    op.drop_index("ix_property_images_property_id", table_name="property_images")
    op.drop_table("property_images")

    # request_images
    op.drop_index("ix_request_images_request_id", table_name="request_images")
    op.drop_table("request_images")

    # properties
    op.drop_table("properties")

    # buyer_requests
    op.drop_index("ix_buyer_requests_session_id", table_name="buyer_requests")
    op.drop_table("buyer_requests")

    # Enums (PostgreSQL فقط)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="requestsource").drop(bind, checkfirst=True)
        sa.Enum(name="requestintent").drop(bind, checkfirst=True)
