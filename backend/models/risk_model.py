from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from database import Base


class Risk(Base):
    __tablename__ = "risk_management"

    risk_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    probability = Column(String(50), nullable=False)
    impact = Column(String(50), nullable=False)
    mitigation_plan = Column(Text, nullable=True)
    owner = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())