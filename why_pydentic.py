from pydantic import BaseModel

# doing type validation-
class Patient(BaseModel):
    name:str
    age:int

patient_info={"name":"sagar","age":30} # if age "30" pydantic will convert it into int 30. If age is given "thirty" will throw pydntic error.

patient_obj1=Patient(**patient_info)
patient_obj2=Patient(**patient_info)
print(patient_obj1)


def insert_pydentic_data(patient:Patient):
    print(patient.name)
    print(patient.age)
    print("Inserted!")


insert_pydentic_data(patient_obj1)