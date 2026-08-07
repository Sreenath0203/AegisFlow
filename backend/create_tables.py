from backend.database import Base, engine

# Import all models
from backend.models.user import User
from backend.models.supplier import Supplier
from backend.models.risk import Risk
from backend.models.inventory import Inventory
from backend.models.recommendation import Recommendation
from backend.models.alert import Alert


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")