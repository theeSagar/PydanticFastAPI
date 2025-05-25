from pydantic import BaseModel,EmailStr, Field
from typing import List, Dict, Optional,Annotated
# doing type validation-

#below we have created a pydantic model
# by default all pydantic feilds defined in the model are mendatory
class Patient(BaseModel):
    name:str=Field(max_length=50) # name lenght should be max 50

    email:Optional[EmailStr] =None
    age:int= Field(gt=0,lt=120) # age should be greater then o always

    weight:Annotated[float,Field(gt=0,strict=True)] # This will surpass the pydeantic defatult type converion and demands weight in flot only
    married:bool = False

    allergies:Optional[List[str]] = None # why not just list why list[str]? This is done to ensure that the items in the list are also validated as items in the list should be string. Same for below Dict. Optional means this feild is optional,default value None.
    contact_details:Dict[str,str]


patient_info={"name":"sagar","email":"Lala@gmail.com","age":30,"weight":65,"married":False,"contact_details":{"city":"agra","pin":"282005"}} # if age "30" pydantic will convert it into int 30. If age is given "thirty" will throw pydntic error.

patient_obj1=Patient(**patient_info)
patient_obj2=Patient(**patient_info)
print(patient_obj1)


def insert_pydentic_data(patient:Patient):
    print(patient.name)
    print(patient.age)
    print("Email is->>>>>>",patient.email)
    print("Inserted!")
    print(patient.allergies) # prints none if allergies are not provided
    print(patient.contact_details)


insert_pydentic_data(patient_obj1)