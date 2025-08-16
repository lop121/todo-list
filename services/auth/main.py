import uvicorn
from fastapi import FastAPI

from services.auth import routes

app = FastAPI(title='To-Do List')
app.include_router(routes.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
