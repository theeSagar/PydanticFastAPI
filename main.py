from fastapi import FastAPI,Path, HTTPException,Depends, Body
import json
from pydantic import BaseModel,Field,computed_field, EmailStr
from typing import Optional, Annotated,Literal,List,Union
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
import re
import jwt
from jwt import PyJWTError
from jwt.exceptions import InvalidTokenError, InvalidTokenError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app=FastAPI()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

@app.get("/view_patient_data",response_model=List[Patient]) # need to convert List[Patient] when accessing multiple objects {FastAPI is serializing and validating the data returned from your function using the Patient Pydantic model, which turns the data into clean, JSON-compatible output.}

def patient_data(db: db_dependency):
    try:
        patients = db.query(models.Patient) # returns a SQLAlchemy model instance
        print(patients)
        # patients_data = [Patient.from_orm(p).dict() for p in patients] # fetching multiple objects we need to convert into list
        #This converts the SQLAlchemy object into a Pydantic model (Patient) which is serializable.
        # patients_data = Patient.from_orm(patients) # when fetching single object 
        # print(patients_data)
        return patients  # FastAPI uses the response_model to serialize
        
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


#______________ creating student registration _________________________>

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

class UserCreate(BaseModel):
    # id: int
    name:str=Field(max_length=50)
    age:int=Field(gt=0,lt=120)
    email: Annotated[EmailStr,Field(...,description="Email id of the student")]
    gender: Literal["male", "female", "others"]
    phone_number : Annotated[str,Field(..., description="Phone number of the student or gaurdian.")]
    blood_group : Annotated[str,Field(..., description="Blood group of the student.")]= None
    password : Annotated[str,Field(...,description="Password here.")]

    model_config = {
        "from_attributes": True }

@app.post("/create_student",response_model=UserCreate)
def create_student(db: db_dependency, input_data:UserCreate = Body(...)):
    hashed_password = hash_password(input_data.password)

    print("unhashed_password",input_data.password)
    print("hashed_password",hashed_password)
    message=""
    print(input_data.email,"_________")
    phone_pattern=re.compile(r"^[6-9]\d{9}$")
    email_pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

    if not phone_pattern.match(input_data.phone_number):
        message="Invalid phone number"
    if not email_pattern.match(input_data.email):
        message="Invalid email address"        
    print(models.User.email,"304")
    print(input_data.email,"305")                #SQLAlchemy column
    existing_student=db.query(models.User).filter(models.User.email == input_data.email).first() # this means where 

    if existing_student:
        message="Student already exits"

    if message:
        print(message)
        raise HTTPException(status_code=400,detail=message)
        
    print(existing_student,"____+_+_+")
    new_student=models.User(
        name=input_data.name,
        email=input_data.email,
        age=input_data.age,
        gender=input_data.gender,
        phone_number=input_data.phone_number,
        blood_group=input_data.blood_group,
        password=hashed_password  # hash if needed
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return JSONResponse (status_code=201,content="Student registered.")

class Token(BaseModel):
    access_token: str
    token_type: str
    # refresh_token:str


class TokenData(BaseModel):
    email: EmailStr | None = None
    # name:str=Field(max_length=50)
    # age:int
    # gender: Literal["male", "female", "others"]
    # phone_number : Annotated[str,Field(..., description="Phone number of the student or gaurdian.")]
    # blood_group : Annotated[str,Field(..., description="Blood group of the student.")]

# from pydantic import BaseModel, EmailStr

class UserOutDetatils(BaseModel):
    id:int
    email: EmailStr | None = None
    name:str=Field(max_length=50)
    age:int
    gender: Literal["male", "female", "others"]
    phone_number : str
    blood_group : str | None

    model_config = {
        "from_attributes": True }

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserView(BaseModel):
    # id: int
    name:str=Field(max_length=50)
    age:int=Field(gt=0,lt=120)
    email: Annotated[EmailStr,Field(...,description="Email id of the student")]
    gender: Literal["male", "female", "others"]
    phone_number : Annotated[str,Field(..., description="Phone number of the student or gaurdian.")]
    blood_group : Annotated[str,Field(..., description="Blood group of the student.")]

    model_config = {
        "from_attributes": True }
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# @app.get("/view_student",response_model=List[UserView])
# def view_student(db: db_dependency):
#     try:
#         student_instances = db.query(models.User)
#         print(student_instances,"_________________")
#         return student_instances
#     # return JSONResponse(status_code=200,content=student_instances)
#     except Exception as e:
#         raise HTTPException (status_code=500,detail=str(e))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/login", response_model=Token)
def login_user(input_data: LoginRequest = Body(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == input_data.email).first()

    if not user or not verify_password(input_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        print("____________________>")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload,"__________________________________________+_+__")
        email: str = payload.get("sub")
        print(email)
        if email is None:
            raise HTTPException(
                status_code=400,
                detail="Token payload invalid",
            )
        return TokenData(email=email)
    except InvalidTokenError:
        raise HTTPException(
            status_code=400,
            detail="Invalid token",
        )
    
@app.get("/me",response_model = UserOutDetatils)
def get_my_info(db: db_dependency,current_user: models.User = Depends(get_current_user)):
    print(current_user,"_________________________++++++++++++++++++++++++++++++++++++++")
    user_data = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user_data:
        raise HTTPException(status_code=400, detail="User not found")
    print(user_data,"!!!!!!!!!!!!!!")
    return UserOutDetatils(
        id=user_data.id,
        email=user_data.email,
        name=user_data.name,
        age=user_data.age,
        gender=user_data.gender,
        phone_number=user_data.phone_number,
        blood_group=user_data.blood_group
    )