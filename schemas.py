from pydantic import BaseModel
from datetime import date

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: date
    additional_data: str = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class ContactSearch(BaseModel):
    query: str
