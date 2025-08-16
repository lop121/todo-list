from fastapi import FastAPI

from . import routes

app = FastAPI(title='Tasks')

app.include_router(routes.router)
