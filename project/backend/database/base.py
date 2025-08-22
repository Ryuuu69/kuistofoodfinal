from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import des modèles pour l'enregistrement auprès de Base.metadata
from models.models import *  # noqa: F401,F403
