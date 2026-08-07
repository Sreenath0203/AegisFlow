from sqlalchemy import Column, Integer, String, ForeignKey

from database import Base


class Recommendation(Base):

    __tablename__ = "recommendations"


    recommendation_id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.supplier_id"),
        nullable=False
    )


    recommendation = Column(
        String(500),
        nullable=False
    )


    reason = Column(
        String(500),
        nullable=False
    )


    priority = Column(
        String(20),
        nullable=False
    )