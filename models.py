from sqlalchemy import Boolean, Column, ForeignKey, Integer, String , Float
from database import Base

from sqlalchemy import Boolean,Column,ForeignKey,Integer,String
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
