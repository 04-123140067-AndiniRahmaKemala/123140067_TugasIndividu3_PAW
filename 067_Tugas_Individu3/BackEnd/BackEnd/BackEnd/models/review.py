from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Float,
    DateTime,
)
from datetime import datetime
from .meta import Base


class Review(Base):
    """Model for product reviews"""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(50), nullable=False)  # POSITIVE, NEGATIVE, NEUTRAL
    confidence = Column(Float, nullable=False)
    key_points = Column(Text)  # JSON string of key points
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review(id={self.id}, product={self.product_name}, sentiment={self.sentiment})>'
