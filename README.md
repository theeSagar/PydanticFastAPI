# FastAPI + PostgreSQL - 

This is a simple FastAPI-based RESTful API for managing student data. 
It uses SQLAlchemy for ORM, PostgreSQL for the database, and Pydantic for data validation.

# Some understanding of FastAPI  - 
- models.py SQLAlchemy model, similar to Django ORM model.
- schemas.py (Pydantic models = Django serializers)(type validationa and data validation.)
- main.py is like(views.py + urls.py in Django)

## Requirements


schemas.py (Pydantic models = Django serializers)
- Python 3.9+
- PostgreSQL installed and running
- `pip` (Python package manager)


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/theeSagar/FastAPI.git
cd your-repo

### Create and Activate a Virtual Environment
python -m venv venv
source venv/bin/activate

### To run the server
uvicorn main:app --reload
