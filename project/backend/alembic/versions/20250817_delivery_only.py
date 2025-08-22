"""Force delivery-only on deliverymode enum"""

from alembic import op

# IDs
revision = "20250817_delivery_only"
down_revision = "a296d9936608"  # <-- adapte si ton dernier ID diffère
branch_labels = None
depends_on = None


def upgrade():
    # 1) Créer un type temporaire avec la seule valeur 'delivery'
    op.execute("CREATE TYPE deliverymode_new AS ENUM ('delivery');")

    # 2) Convertir la colonne et normaliser les anciennes valeurs -> 'delivery'
    op.execute("""
        ALTER TABLE public.orders
        ALTER COLUMN delivery_mode TYPE deliverymode_new
        USING CASE
            WHEN delivery_mode::text IN ('maison','click_collect','ubereats','delivery') THEN 'delivery'::deliverymode_new
            ELSE 'delivery'::deliverymode_new
        END;
    """)

    # 3) Définir la valeur par défaut
    op.execute("ALTER TABLE public.orders ALTER COLUMN delivery_mode SET DEFAULT 'delivery';")

    # 4) Remplacer l'ancien type par le nouveau
    op.execute("DROP TYPE deliverymode;")
    op.execute("ALTER TYPE deliverymode_new RENAME TO deliverymode;")


def downgrade():
    # Revenir à un type large (au besoin)
    op.execute("CREATE TYPE deliverymode_old AS ENUM ('maison','click_collect','ubereats');")
    op.execute("""
        ALTER TABLE public.orders
        ALTER COLUMN delivery_mode TYPE deliverymode_old
        USING 'maison'::deliverymode_old;
    """)
    op.execute("ALTER TABLE public.orders ALTER COLUMN delivery_mode SET DEFAULT 'maison';")
    op.execute("DROP TYPE deliverymode;")
    op.execute("ALTER TYPE deliverymode_old RENAME TO deliverymode;")
