from pydantic import BaseModel,EmailStr, Field,field_validator
from typing import List, Dict, Optional,Annotated


class Patient(BaseModel):
    name:str
    email:str
    age:int
    weight:float
    married:bool
    allergies:List[str]
    contact_details:Dict[str]

# in this we are checking email like email should be of any specific domain like of gmail.com or yahooho.com or any bank specifi.(field_validator)

