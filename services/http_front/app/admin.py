from fastapi import APIRouter
from starlette.responses import Response
from ...db_definition import Identity, Sender
from .dto import CreateIdentityBody, CreateSenderBody


# add security here
router = APIRouter()


@router.post('/identity')
def create_identity(body: CreateIdentityBody):
    i = Identity(name=body.name)
    return Response(status_code=201)


@router.delete('/identity/{id}')
def delete_identity(id: int):
    identity = Identity[id]
    del identity
    return Response(status_code=204)


@router.get('/identity/{id}')
def get_identity(id: int):
    return Identity[id].to_json()


@router.post('/identity/{id}/sender')
def create_sender(id: int, body: CreateSenderBody):
    identity = Identity[id]
    if identity is not None:
        s = Sender(
            # not used as of now
            credentials={},
            quota=body.quota,
            email=body.email,
            identity=identity
        )
        return Response(status_code=201)
    else:
        return Response(status_code=404)


@router.delete('/sender/{id}')
def deactivate_sender(id: int):
    Sender[id].deactivate()
    return Response(status_code=204)


@router.patch('/sender/{id}')
def update_sender(quota: int, id: int):
    sender = Sender[id]
    sender.quota = quota
    return sender.to_json()
