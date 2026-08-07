from sqlalchemy import Column, Integer, Float, String
from backend.database import Base


class Risk(Base):
    __tablename__ = "risks"

    risk_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    delay_days = Column(Integer, nullable=False)
    weather = Column(String, nullable=False)