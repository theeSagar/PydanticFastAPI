from pydantic import BaseModel,EmailStr, Field,field_validator, computed_field
from typing import List, Dict, Optional,Annotated


class Patient(BaseModel):
    name:str
    email:str
    age:int
    weight:float
    height:float
    married:bool
    allergies:List[str]=None
    contact_details:Dict[str,str]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi_anyname=round(self.weight/(self.height**2),2)
        return bmi_anyname
    

patient_info={"name":"sagar","email":"Lala@gmail.com","age":30,"weight":65,"height":34,"married":False,"contact_details":{"city":"Agra"}} 
patient_obj1=Patient(**patient_info)



def insert_pydentic_data(patient:Patient):
    print(patient.name)
    print(patient.age)
    print("Email is->>>>>>",patient.email)
    print("Inserted!")
    print(patient.allergies) # prints none if allergies are not provided
    # print(patient.contact_details)
    print(patient.bmi)

insert_pydentic_data(patient_obj1)