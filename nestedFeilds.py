from fastapi import FastAPI
from pydantic import BaseModel

class Address(BaseModel):
    city:str
    state:str
    pincode:int

class Patient(BaseModel):
    name:str
    age:int
    weight:float
    address: Address

# now creating an object of Address class
address_data={"city":"Agra","state":"UP","pincode":282887}
address_obj=Address(**address_data) # here data is validated
patient_data={"name":"sagar","age":30,"weight":65,"address":address_obj}

patient_obj=Patient(**patient_data)
print((patient_obj),"_______________")


def normal_patient_func(patient:Patient):
    print(patient.name)
    print(patient.address.city)


normal_patient_func(patient_obj)


# Reusable code 
# better readibility and better orginization

#___------------> Exporing pydantic models into dict.

dict_data=(patient_obj.model_dump(),"PPPPPPPPPPPP") # this will convert the existing python model into dict

dict_data_include=(patient_obj.model_dump(include=["name"]),"PPPPPPPPPPPP") # this will only export name key

dict_data_exclude=patient_obj.model_dump(exclude=["name"]) # this will exclude name 

dict_data_exclude=patient_obj.model_dump(exclude={"address":["city"]}) # this will exclude city key from address dict.
print(dict_data_exclude)

json_data=(patient_obj.model_dump_json(),"PPPPPPPPPPPP") # this will convert the existing python model into json