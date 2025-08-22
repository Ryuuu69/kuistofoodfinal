"""Drop menus and menu_id from order_items (safe)

Revision ID: 304a6823265e
Revises: 20250817_delivery_only
Create Date: 2025-08-17 17:50:10.944767
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "304a6823265e"
down_revision = "20250817_delivery_only"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    insp = sa.inspect(conn)

    # 1) Supprimer la FK order_items.menu_id si présente
    if "order_items" in insp.get_table_names():
        # On tente de drop la contrainte par son nom standard Postgres si elle existe
        op.execute(
            "ALTER TABLE order_items DROP CONSTRAINT IF EXISTS order_items_menu_id_fkey;"
        )
        # Puis on drop la colonne si présente
        cols = [c["name"] for c in insp.get_columns("order_items")]
        if "menu_id" in cols:
            with op.batch_alter_table("order_items") as batch_op:
                batch_op.drop_column("menu_id")

    # 2) Drop tables liées aux menus si elles existent
    # NB: IF EXISTS + CASCADE pour éviter les erreurs si déjà partiellement supprimées
    op.execute("DROP TABLE IF EXISTS menu_choices CASCADE;")
    op.execute("DROP TABLE IF EXISTS menu_options CASCADE;")
    op.execute("DROP TABLE IF EXISTS menus CASCADE;")


def downgrade():
    # Downgrade best-effort : on recrée les tables supprimées et la colonne.
    op.create_table(
        "menus",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False, unique=True),
        sa.Column("image_url", sa.String(length=500)),
        sa.Column("description", sa.Text()),
        sa.Column("supplement", sa.DECIMAL(10, 2)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "menu_choices",
        sa.Column("menu_id", sa.Integer(), sa.ForeignKey("menus.id"), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), primary_key=True),
    )
    op.create_table(
        "menu_options",
        sa.Column("menu_id", sa.Integer(), sa.ForeignKey("menus.id"), primary_key=True),
        sa.Column("option_id", sa.Integer(), sa.ForeignKey("options.id"), primary_key=True),
    )
    with op.batch_alter_table("order_items") as batch_op:
        batch_op.add_column(sa.Column("menu_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("order_items_menu_id_fkey", "menus", ["menu_id"], ["id"])
