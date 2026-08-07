from sqlalchemy import Column, Integer, String

from backend.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)

    supplier_name = Column(String(150), nullable=False)

    location = Column(String(100), nullable=False)

    status = Column(String(50), nullable=False)