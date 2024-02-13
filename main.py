from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List
from sqlalchemy.orm import Session

from models import Contact
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "Vikki123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


app = FastAPI()

@app.get("/hello")
def read_hello():
    """
    Опис маршруту /hello

    Returns:
        dict: Об'єкт JSON 
    """
    return {"message": "Hello, World!"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class User(BaseModel):
    username: str

def register_user(username: str, email: str, password: str, db: dict = Depends(get_db)):
    if username in db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    new_user = UserInDB(username=username, email=email, hashed_password=password)
    db[username] = create_user(new_user)
    return {"message": "User registered successfully"}


def verify_email(email: str, db: dict = Depends(get_db)):
    user = get_user(db, email)
    if user:
        user.email_verified = True
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

class UserInDB(User):
    hashed_password: str


def create_user(db_user: UserInDB):
    hashed_password = pwd_context.hash(db_user.hashed_password)
    return UserInDB(**db_user.dict(), hashed_password=hashed_password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db, username: str):
    user_dict = db.get(username)
    if user_dict:
        return UserInDB(**user_dict)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = {"sub": username}
    except JWTError:
        raise credentials_exception
    return token_data


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/register")
def register_user(username: str, password: str, db: dict = Depends(get_db)):
    if username in db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    new_user = UserInDB(username=username, hashed_password=password)
    db[username] = create_user(new_user)
    return {"message": "User registered successfully"}


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordBearer = Depends()):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

db = {}

def get_db():
       return db

@app.post("/contacts/", response_model=Contact)
def create_contact(contact: ContactCreate, current_user: User = Depends(get_current_user)):
    db_contact = Contact(**contact.dict(), user_id=current_user.username)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[Contact])
def read_contacts(skip: int = 0, limit: int = 10, current_user: User = Depends(get_current_user)):
    contacts = db.query(Contact).filter_by(user_id=current_user.username).offset(skip).limit(limit).all()
    return contacts

@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.username).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact.dict().items():
        setattr(db_contact, key, value)

    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.delete("/contacts/{contact_id}", response_model=dict)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.username).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

@app.get("/contacts/search/", response_model=List[Contact])
def search_contacts(query: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contacts = db.query(Contact).filter(
        (Contact.first_name.ilike(f"%{query}%")) |
        (Contact.last_name.ilike(f"%{query}%")) |
        (Contact.email.ilike(f"%{query}%")),
        Contact.user_id == current_user.username
    ).all()
    return contacts

@app.get("/contacts/birthdays/", response_model=List[Contact])
def upcoming_birthdays(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    end_date = today + timedelta(days=7)
    contacts = db.query(Contact).filter(
        (Contact.birth_date >= today) & (Contact.birth_date <= end_date),
        Contact.user_id == current_user.username
    ).all()
    return contacts


