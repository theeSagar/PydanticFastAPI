#let's create router
from fastapi import APIRouter
import models
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel,Field,computed_field, EmailStr
import re
from fastapi import FastAPI,Path, HTTPException,Depends, Body
from typing import Optional, Annotated,Literal,List,Union
from passlib.context import CryptContext
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError, InvalidTokenError




router = APIRouter(
prefix='/user',
tags = ['student']
)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#______________ creating student registration _________________________>


def get_db():
    db=SessionLocal()

    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session,Depends(get_db)]

class UserCreate(BaseModel):
    # id: int
    name:str=Field(max_length=50)
    age:int=Field(gt=0,lt=120)
    email: Annotated[EmailStr,Field(...,description="Email id of the student")]
    gender: Literal["male", "female", "others"]
    phone_number : Annotated[str,Field(..., description="Phone number of the student or gaurdian.")]
    blood_group : Annotated[str,Field(..., description="Blood group of the student.")]= None
    password : Annotated[str,Field(...,description="Password here.")]

    model_config = {
        "from_attributes": True }

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/create_student",response_model=UserCreate)


def create_student(db: db_dependency, input_data:UserCreate = Body(...)):
    hashed_password = hash_password(input_data.password)

    print("unhashed_password",input_data.password)
    print("hashed_password",hashed_password)
    message=""
    print(input_data.email,"_________")
    phone_pattern=re.compile(r"^[6-9]\d{9}$")
    email_pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

    if not phone_pattern.match(input_data.phone_number):
        message="Invalid phone number"
    if not email_pattern.match(input_data.email):
        message="Invalid email address"        
    print(models.User.email,"304")
    print(input_data.email,"305")                #SQLAlchemy column
    existing_student=db.query(models.User).filter(models.User.email == input_data.email).first() # this means where 

    if existing_student:
        message="Student already exits"

    if message:
        print(message)
        raise HTTPException(status_code=400,detail=message)
        
    print(existing_student,"____+_+_+")
    new_student=models.User(
        name=input_data.name,
        email=input_data.email,
        age=input_data.age,
        gender=input_data.gender,
        phone_number=input_data.phone_number,
        blood_group=input_data.blood_group,
        password=hashed_password  # hash if needed
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return JSONResponse (status_code=201,content="Student registered.")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class UserOutDetatils(BaseModel):
    id:int
    email: EmailStr | None = None
    name:str=Field(max_length=50)
    age:int
    gender: Literal["male", "female", "others"]
    phone_number : str
    blood_group : str | None

    model_config = {
        "from_attributes": True }
    
class Token(BaseModel):
    access_token: str
    token_type: str
    # refresh_token:str


class TokenData(BaseModel):
    email: EmailStr | None = None

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        print("____________________>")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload,"__________________________________________+_+__")
        email: str = payload.get("sub")
        print(email)
        if email is None:
            raise HTTPException(
                status_code=400,
                detail="Token payload invalid",
            )
        return TokenData(email=email)
    except InvalidTokenError:
        raise HTTPException(
            status_code=400,
            detail="Invalid token",
        )


@router.get("/user/details",response_model = UserOutDetatils)
def get_my_info(db: db_dependency,current_user: models.User = Depends(get_current_user)):
    print(current_user,"_________________________++++++++++++++++++++++++++++++++++++++")
    user_data = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user_data:
        raise HTTPException(status_code=400, detail="User not found")
    print(user_data,"!!!!!!!!!!!!!!")
    return UserOutDetatils(
        id=user_data.id,
        email=user_data.email,
        name=user_data.name,
        age=user_data.age,
        gender=user_data.gender,
        phone_number=user_data.phone_number,
        blood_group=user_data.blood_group
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token)
def login_user(input_data: LoginRequest = Body(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == input_data.email).first()

    if not user or not verify_password(input_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
