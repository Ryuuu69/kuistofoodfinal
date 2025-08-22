"""Create product_options association (safe)

Revision ID: 20250817_product_options
Revises: 304a6823265e
Create Date: 2025-08-17 19:20:00
"""
from alembic import op
import sqlalchemy as sa

# IDs
revision = "20250817_product_options"
down_revision = "304a6823265e"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    insp = sa.inspect(conn)

    # Crée la table d'association produit<->option si absente
    if "product_options" not in insp.get_table_names():
        op.create_table(
            "product_options",
            sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), primary_key=True),
            sa.Column("option_id", sa.Integer(), sa.ForeignKey("options.id"), primary_key=True),
        )


def downgrade():
    op.execute("DROP TABLE IF EXISTS product_options CASCADE;")
