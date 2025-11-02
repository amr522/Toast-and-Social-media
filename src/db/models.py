from sqlalchemy import Column, Integer, String, Date, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    last_order_date = Column(Date)
    last_order_items = Column(JSON)
    birthday = Column(Date)
    loyalty_tier = Column(String)
    email_opt_in = Column(Boolean, default=True)
    opt_in_at = Column(DateTime)
    updated_at = Column(DateTime)
