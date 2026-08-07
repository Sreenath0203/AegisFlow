from database import Base, engine

# Import all models
from models.user import User
from models.supplier import Supplier
from models.risk import Risk
from models.inventory import Inventory
from models.recommendation import Recommendation
from models.alert import Alert


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")