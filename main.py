from fastapi import FastAPI,Path, HTTPException
import json

app=FastAPI()

def load_data():
    with open("patients.json","r") as f:
        data=json.load(f)

    return data

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
      