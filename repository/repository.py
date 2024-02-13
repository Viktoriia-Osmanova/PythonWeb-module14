from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Contact  # Імпортуємо модель Contact з файлу models.py

class ContactRepository:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def add_contact(self, contact_data):
        contact = Contact(**contact_data)
        session = self.Session()
        session.add(contact)
        session.commit()
        session.close()
        return contact.id

    def get_contact_by_id(self, contact_id):
        session = self.Session()
        contact = session.query(Contact).filter_by(id=contact_id).first()
        session.close()
        return contact

    def update_contact(self, contact_id, contact_data):
        session = self.Session()
        contact = session.query(Contact).filter_by(id=contact_id).first()
        if contact:
            for key, value in contact_data.items():
                setattr(contact, key, value)
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False

    def delete_contact(self, contact_id):
        session = self.Session()
        contact = session.query(Contact).filter_by(id=contact_id).first()
        if contact:
            session.delete(contact)
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
