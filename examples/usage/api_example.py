from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ai_agent.core.query_handler import QueryHandler

app = FastAPI()
handler = QueryHandler()

class Query(BaseModel):
    query: str
    server: Optional[str] = None

@app.post("/api/query")
async def process_query(query: Query):
    try:
        response = await handler.process_query(query.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, str(e))

@app.get("/api/files/")
async def get_files(server: str, path: str):
    return await handler.read_file(server, path)
