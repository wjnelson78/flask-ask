from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine, MetaData, Table, select, update
from typing import List, Dict
from pydantic import BaseModel

class Email(BaseModel):
    id: str
    subject: str
    sender: str
    received: str
    status: str
    action_taken: int


app = FastAPI()
db_path = "sqlite:///./emails.db"  # path to your SQLite database
engine = create_engine(db_path)
metadata = MetaData()

emails = Table(
    'emails',
    metadata,
    Column('id', String, primary_key=True),
    Column('subject', String),
    Column('sender', String),
    Column('received', String),
    Column('status', String),
    Column('action_taken', Integer, default=0),
    autoload_with=engine
)

@app.get("/unread_emails/", response_model=List[Email])
async def get_unread_emails():
    query = select(emails).where(emails.c.status == 'unread')
    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()
    return [dict(row._asdict()) for row in rows]

@app.put("/mark_email_as_read/{email_id}")
async def mark_email_as_read(email_id: str):
    with engine.begin() as connection:  # this will handle the commit for us
        query = update(emails).where(emails.c.id == email_id).values(status='read')
        result = connection.execute(query)

    if result.rowcount:
        return {"status": "success", "message": "Email marked as read."}
    else:
        raise HTTPException(status_code=404, detail="Email not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
