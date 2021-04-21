

from fastapi import FastAPI

from ...db_definition import credentials, init_db
from .server import router

app = FastAPI()

drop_database = False


@app.on_event('startup')
def init():
    init_db(credentials, drop_database)


app.include_router(router, prefix="")
