from fastapi import FastAPI, HTTPException , status ,Depends
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# Importing from Model.py file
import models
# Importing from database.py 
from database import SessionLocal ,engine

app = FastAPI()

origins_urls = [
    # URL
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins_urls,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],

)

class TransactionBase(BaseModel):
    amount : float
    category : str
    description : str 
    is_income : bool
    date : str

class TransactionModel(TransactionBase):
    id : int 
     
    class Config:
        from_attributes = True

def get_database():

    db = SessionLocal()

    try:
        yield db 

    finally:
        db.close()


# Dependency injection
db_dependency = Annotated[Session , Depends(get_database)]

models.Base.metadata.create_all(bind = engine)


# Createing The EndPonts


@app.post("/transactions/" , response_model=TransactionModel)
async def create_transaction(transaction : TransactionBase , db: db_dependency ): #type: ignore
    db_transcactions = models.Transaction(**transaction.dict())
    db.add(db_transcactions)
    db.commit()
    db.refresh(db_transcactions)

    return db_transcactions


@app.get("/transactions/" , response_model=list[TransactionModel])
async def read_transactions(db:db_dependency , skip : int = 0 , limit : int = 100):

    transactions = db.query(models.Transaction).offset(skip).limit(limit).all()

    return transactions

# @app.delete("/transactions/{transaction_id}/" , status_code= status.HTTP_204_NO_CONTENT)
# async def delete_transactions(transaction_id : int, db:db_dependency):

#     transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    
#     if transaction is None:
#         raise HTTPException(status_code=404 , detail= "Successfully deleted")
    
#     db.delete(transaction)
#     db.commit()


#     return {"Transaction" : "Deleted"}
