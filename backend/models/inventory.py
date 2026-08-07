from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    item_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    status = Column(String, nullable=False)