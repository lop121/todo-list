from fastapi import FastAPI

from . import routes

app = FastAPI(title='To-Do List')
app.include_router(routes.router)
