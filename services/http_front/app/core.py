

from fastapi import FastAPI, Response

from ...db_definition import credentials, init_db
from .server import router as send_router
from .admin import router as admin_router

app = FastAPI()

drop_database = False


@app.on_event('startup')
def init():
    init_db(credentials, drop_database)


@app.get('/live')
def live():
    return Response('OK')


@app.get('/templates')
def list_templates():
    # TODO
    pass


app.include_router(send_router, prefix="/send")
app.include_router(admin_router, prefix="/admin")
