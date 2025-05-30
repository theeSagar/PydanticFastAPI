from fastapi import FastAPI,Path, HTTPException,Depends, Body
import json
from pydantic import BaseModel,Field,computed_field
from typing import Optional, Annotated,Literal,List,Union
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app=FastAPI()

def load_data():
    with open("patients.json","r") as f:
        data=json.load(f)

    return data

def save_data(data): # jo bhi data yaha milega usko dump krna h 
    with open('patients.json','w') as f:
        json.dump(data,f)

class Patient(BaseModel):
    id:Annotated[int,Field(...,description="Id of the patient",examples=[1])]

    name:str=Field(max_length=50)
    age:int=Field(gt=0,lt=120)

    gender: Literal["male", "female", "others"]
    language:Optional[str]
    city:str

    height:Annotated[float,Field(...,description="Height in meters",gt=0)]

    weight:Annotated[float,Field(...,description="weight in kgs",gt=0)]
    # BMI:Optional[float]
    class Config: # this tells the Pydantic model to allow conversion from non-dict Python objects like ORM models
        from_attributes = True

    @computed_field
    @property
    def BMI(self) -> float:
        bmi_anyname=round(self.weight/(self.height**2),2)
        print(bmi_anyname,"44")
        return bmi_anyname
    
    @computed_field
    @property

    def verdict(self)-> str: # this function name should be same name as the  colomn name in the db
        print("50")
        if self.BMI <18.5:
            print("52")
            return "Underweight"
        # elif self.bmi <25:
        #     return "Normal"            
        elif self.BMI <30:
            print("58")
            return "Normal"
        else:
            print("61")
            return "Obese"
        
def get_db():
    db=SessionLocal()

    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session,Depends(get_db)]

@app.get("/")
def hello():
    return {"message":"Hello world!"}

@app.get("/about")
def about():
    return{"message":"This is about patients project."}

@app.get("/view_patient_data",response_model=Patient) # need to convert List[Patient] when accessing multiple objects {FastAPI is serializing and validating the data returned from your function using the Patient Pydantic model, which turns the data into clean, JSON-compatible output.}

def patient_data(db: db_dependency):
    try:
        patients = db.query(models.Patient).first() # returns a SQLAlchemy model instance
        print(patients)
        # patients_data = [Patient.from_orm(p).dict() for p in patients] # fetching multiple objects we need to convert into list
        #This converts the SQLAlchemy object into a Pydantic model (Patient) which is serializable.
        patients_data = Patient.from_orm(patients) # when fetching single object 
        print(patients_data)
        return patients_data  # FastAPI uses the response_model to serialize
        
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500,detail=str(e))
    
@app.get("/patient_id/{patient_ID}",response_model=Patient)

def get_patientId(db: db_dependency,patient_ID:int=Path(..., description="Id of the patient in the db",example="1",gt=0)): #... means it is required
    print("____________")
    # p_data=load_data()
    # for p in p_data:
    #     # print(p,"+++++++++++++++")
    #     if p["id"]==id:
    #         print(p)
    #         return p
    # raise HTTPException(status_code=400,detail="Not found.")
    try:
        print("103",patient_ID)
        patient_id_instance = db.query(models.Patient).filter(models.Patient.id==patient_ID).first()
        if not patient_id_instance:
            raise HTTPException(status_code=400,detail="Patient id not found.")
        print("105",patient_id_instance)
        patient_data= Patient.from_orm(patient_id_instance)
        print(patient_data,"____________")
        return patient_data
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500,detail=str(e))



@app.post("/create",response_model=Union[Patient, List[Patient]]) # After processing the request, I will return either a single Patient or a list of Patient objects as the response.

def create_patient(
    db: db_dependency,input_data: Union[Patient, List[Patient]] = Body(...)
):    # here patient data is validated as here we do not need to make an object of patient pass the data in the same FastAPI is doing all this for me.{Request body se data aya Patient model k pas gaya validate hua }

    # we will load check existing data--
    #------------ this code gets the data from the json file and inserts in the same.
    # patient_id=patient.id

    # data=load_data()
    # for i in data:
    #     if i["id"]==patient_id:
    #         raise HTTPException(status_code=400,detail="Patient already exits")
        
    # data_dict=(patient.model_dump())
    # data.append(data_dict) # here the data is inserted in the json
    # save_data(data)
    # return JSONResponse(status_code=201,content={"messahe":"patient created👍"})
    try:

        if isinstance(input_data, list):
            # If input is a list of patients
            patient_objs = [models.Patient(**p.dict()) for p in input_data]
            print(patient_objs,"!!!!!!!!!!!!!!")
            db.add_all(patient_objs)
            db.commit()
            for p in patient_objs:
                db.refresh(p)
            return JSONResponse(status_code=200,content="patient created 👍")
        else:
            # If input is a single patient
            patient_obj = models.Patient(**input_data.dict())
            db.add(patient_obj)
            db.commit()
            db.refresh(patient_obj)
            print(patient_obj,"!!!!!!!!!!!!!!")
            print("162")
            return JSONResponse(status_code=200,content="created")
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500,detail=str(e))





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
    

# ---------- Now connection with postgres db-------------
# models.Base.metadata.drop_all(bind=engine)   # Drops all tables
models.Base.metadata.create_all(bind=engine) # this line will create all tables,colomns in data base. 

class ChoiceBase(BaseModel):
    choice_text:Optional[str]
    is_correct:Optional[bool] =False

class QuestionBase(BaseModel):
    question_text:Annotated[Optional[str],Field(max_length=200)]
    choice:Optional[list[ChoiceBase]]



@app.post('/questions')

def create_questions(question: QuestionBase, db: db_dependency):
    print("190")
    db_question = models.Questions(question_text=question.question_text)
    print("192")
    db.add(db_question)
    print("194")
    db.commit()
    print("196")
    db.refresh(db_question)

    if question.choice:
        for choice in question.choice:
            print(choice,"_")
            db_choice = models.Choices(
                choice_text=choice.choice_text,
                is_correct=choice.is_correct,
                question_id=db_question.id
            )
            db.add(db_choice)
        db.commit()

    return {"message": "Question and choices created successfully"}