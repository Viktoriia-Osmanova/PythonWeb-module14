from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    phone_number = Column(String)
    birth_date = Column(Date)
    additional_data = Column(String, nullable=True)
