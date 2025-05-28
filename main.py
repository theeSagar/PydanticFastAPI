from fastapi import FastAPI,Path, HTTPException
import json
from pydantic import BaseModel,Field,computed_field
from typing import Optional, Annotated,Literal
from fastapi.responses import JSONResponse

app=FastAPI()

def load_data():
    with open("patients.json","r") as f:
        data=json.load(f)

    return data

def save_data(data): # jo bhi data yaha milega usko dump krna h 
    with open('patients.json','w') as f:
        json.dump(data,f)

@app.get("/")
def hello():
    return {"message":"Hello world!"}

@app.get("/about")
def about():
    return{"message":"This is about patients project."}

@app.get("/view_patient_data")
def patient_data():
    p_data=load_data()
    return p_data

@app.get("/patient_id/{id}")

def get_patientId(id:int=Path(..., description="Id of the patient in the db",example="1",gt=0)): #... means it is required
    p_data=load_data()
    for p in p_data:
        # print(p,"+++++++++++++++")
        if p["id"]==id:
            print(p)
            return p
    raise HTTPException(status_code=400,detail="Not found.")
      
class Patient(BaseModel):
    id:Annotated[int,Field(...,description="Id of the patient",examples=[1])]

    name:str=Field(max_length=50)
    age:int=Field(gt=0,lt=120)

    gender: Literal["male", "female", "others"]
    language:Optional[str]
    city:str

    height:Annotated[float,Field(...,description="Height in meters",gt=0)]

    weight:Annotated[float,Field(...,description="weight in kgs",gt=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi_anyname=round(self.weight/(self.height**2),2)
        return bmi_anyname
    
    @computed_field
    @property

    def verdict_bmi(self)-> str:
        if self.bmi <18.5:
            return "Underweight"
        # elif self.bmi <25:
        #     return "Normal"
        elif self.bmi <30:
            return "Normal"
        else:
            return "Obese"


@app.post("/create")

def create_patient(patient:Patient): # here patient data is validated as here we do not need to make an object of patient pass the data in the same FastAPI is doing all this for me.{Request body se data aya Patient model k pas gaya validate hua }

    # we will load check existing data--
    patient_id=patient.id

    data=load_data()
    for i in data:
        if i["id"]==patient_id:
            raise HTTPException(status_code=400,detail="Patient already exits")
        
    data_dict=(patient.model_dump())
    data.append(data_dict) # here the data is inserted in the json
    save_data(data)
    return JSONResponse(status_code=201,content={"messahe":"patient created👍"})
    
    # now load the updated data in json file


    # check if the patient already exits---
    # print(patient.id)
    # if patient.id in data

    # create new patient in db.

# We will create a new pydantic model as above PAtient pydantic model all feilds are mendatory , we have to make the feilds optional.


class PatientUpdate(BaseModel):
   
    name: Annotated[Optional[str], Field(description="Full name", max_length=50)] # Annotated is used when you want to add extra metadata or validation (like description, max_length, etc.).  name: Optional[str]

    age:Annotated[Optional[int],Field(gt=0,lt=120,default=None)]

    gender: Annotated[Optional[Literal["male", "female", "others"]],Field(default=None)]
    language:Optional[str]=None
    city:Optional[str]=None

    height:Annotated[Optional[float],Field(...,description="Height in meters")]

    weight:Annotated[Optional[float],Field(...,description="weight in kgs")]


@app.put("/update/{user_id}")
def updateUserData(patient:PatientUpdate,user_id:int):
    
    found=""
    data=load_data()
    for i in data:
        if i["id"]==user_id:
            found=True
            # print(i,"________")
            print(type(patient))
            updated_patient_dict=patient.model_dump(exclude_unset=True) # this means that jo feilds aaegi usko hi dega
            # print(updated_patient_dict)
            for keys in updated_patient_dict:
                print(updated_patient_dict[keys])
                i[keys]=updated_patient_dict[keys]
            save_data(i)
            print(data)
                

            break

    if not found:
        raise HTTPException(status_code=400,detail="Patient id not found.")
        # return {"status":False,"message":"Patient id not found."}

@app.delete("/deletePatient/{id}")
def deletePatient(id:int):
    data=load_data()
    found=False
    for i in data:
        if i["id"]==id:
            found=True
            print(i)
            data.remove(i)
            save_data(data)
            print(data)
            break
    if not found:
        raise HTTPException(status_code=400,detail="Not found")