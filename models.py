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

