from sqlalchemy import Boolean, Column, ForeignKey, Integer, String , Float, func, DateTime
from database import Base


class Questions(Base):
    __tablename__="questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)


class Choices(Base):
    __tablename__ ='choices'
    id = Column(Integer,primary_key=True, index=True)
    choice_text= Column(String, index=True,nullable=True)
    is_correct= Column(Boolean, default=False,nullable=True)
    question_id = Column(Integer, ForeignKey("questions.id")) # this is the foreign key assosiated with questions table.

class Patient(Base):
    __tablename__ =  "patient"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True,nullable=True)
    age = Column(Integer, index=True,nullable=True)
    gender = Column(String)
    language= Column(String, nullable=True) 
    city = Column(String, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    verdict= Column(String,nullable=True)
    BMI= Column(Float,nullable=True)

class User(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)


    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())